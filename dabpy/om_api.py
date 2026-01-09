import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
from datetime import datetime

def obfuscate_token(url, token):
    """Replace the token in a URL with '***' for safe printing."""
    return url.replace(token, "***")

class Feature:
    """Python representation of a WHOS feature."""
    def __init__(self, feature_json):
        self.id = feature_json["id"]
        self.name = feature_json["name"]
        self.coordinates = feature_json["shape"]["coordinates"]
        self.parameters = {param["name"]: param["value"] for param in feature_json["parameter"]}
        self.related_party = feature_json.get("relatedParty", [])

        if self.related_party:
            self.contact_name = self.related_party[0].get("individualName", "")
            self.contact_email = self.related_party[0].get("electronicMailAddress", "")
        else:
            self.contact_name = ""
            self.contact_email = ""

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Coordinates": f"{self.coordinates[0]}, {self.coordinates[1]}",
            "Source": self.parameters.get("source", ""),
            "Identifier": self.parameters.get("identifier", ""),
            "Contact Name": self.contact_name,
            "Contact Email": self.contact_email
        }

    def __repr__(self):
        return f"<Feature id={self.id} name={self.name}>"

class Observation:
    """Python representation of a WHOS observation."""
    def __init__(self, obs_json):
        params = {param["name"]: param["value"] for param in obs_json.get("parameter", [])}
        self.id = obs_json["id"]
        self.type = obs_json.get("type")
        self.source = params.get("source")
        self.observed_property_definition = params.get("observedPropertyDefinition")
        self.original_observed_property = params.get("originalObservedProperty")
        self.observed_property = obs_json.get("observedProperty", {}).get("title")
        self.phenomenon_time_begin = obs_json.get("phenomenonTime", {}).get("begin")
        self.phenomenon_time_end = obs_json.get("phenomenonTime", {}).get("end")
        self.feature_of_interest_href = obs_json.get("featureOfInterest", {}).get("href")
        result_meta = obs_json.get("result", {}).get("defaultPointMetadata", {})
        self.uom = result_meta.get("uom")
        self.interpolation_type = result_meta.get("interpolationType", {}).get("title")
        self.points = obs_json.get("result", {}).get("points", [])

    def to_dict(self):
        return {
            "ID": self.id,
            "Source": self.source,
            "Observed Property Definition": self.observed_property_definition,
            "Original Observed Property": self.original_observed_property,
            "Observed Property": self.observed_property,
            "Phenomenon Time Begin": self.phenomenon_time_begin,
            "Phenomenon Time End": self.phenomenon_time_end,
            "Feature of Interest Href": self.feature_of_interest_href,
            "Observation Type": self.type,
            "Unit of Measurement": self.uom,
            "Interpolation Type": self.interpolation_type
        }

    def __repr__(self):
        return f"<Observation id={self.id} property={self.observed_property}>"

class WHOSClient:
    """WHOS API client to retrieve features and observations as Python objects or Pandas DataFrame."""
    def __init__(self, token, view="whos"):
        self.token = token
        self.view = view
        self.base_url = f"https://whos.geodab.eu/gs-service/services/essi/token/{token}/view/{view}/om-api/"

    # --- Retrieve features ---
    def get_features(self, constraints, paginate=False, max_pages=None, verbose=True):
        if not hasattr(constraints, "to_query"):
            raise ValueError("constraints must be a Constraints object")

        base_query = constraints.to_query()
        url = f"{self.base_url}features?{base_query}"
        all_features, page = [], 1

        while True:
            if verbose:
                print(f"Retrieving page {page}: " + obfuscate_token(url, self.token))

            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()

            all_features.extend([Feature(f) for f in data.get("results", [])])
            completed = data.get("completed", True)
            token = data.get("resumptionToken")

            if not paginate or completed or not token or (max_pages and page >= max_pages):
                break

            url = f"{self.base_url}features?{base_query}&resumptionToken={urllib.parse.quote(token)}"
            page += 1

        if verbose:
            if completed:
                print(f"Returned {len(all_features)} features (completed, data finished).")
            else:
                print(f"Returned {len(all_features)} features (not completed, more data available).")
                print(f"Update the call with 'paginate=True' to see all data.")

        return all_features

    # --- Retrieve observations ---
    def get_observations(self, constraints, paginate=False, max_pages=None, verbose=True):
        if not hasattr(constraints, "to_query"):
            raise ValueError("constraints must have a to_query() method")

        base_query = constraints.to_query()
        url = f"{self.base_url}observations?{base_query}"
        all_obs, page = [], 1

        while True:
            if verbose:
                print(f"Retrieving page {page}: " + obfuscate_token(url, self.token))

            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()

            all_obs.extend([Observation(o) for o in data.get("member", [])])
            completed = data.get("completed", True)
            token = data.get("resumptionToken")

            if not paginate or completed or not token or (max_pages and page >= max_pages):
                break

            url = f"{self.base_url}observations?{base_query}&resumptionToken={urllib.parse.quote(token)}"
            page += 1

        if verbose:
            if completed:
                print(f"Returned {len(all_obs)} observations (completed, data finished).")
            else:
                print(f"Returned {len(all_obs)} observations (not completed, more data available).")
                print(f"Update the call with 'paginate=True' to see all data.")

        return all_obs

    # --- Retrieve observation with full data ---
    def get_observation_with_data(self, observation_id, begin=None, end=None):
        url = self.base_url + f"observations?includeData=true&observationIdentifier={urllib.parse.quote(observation_id)}"
        if begin:
            url += "&beginPosition=" + urllib.parse.quote(begin)
        if end:
            url += "&endPosition=" + urllib.parse.quote(end)

        print("Retrieving " + obfuscate_token(url, self.token))
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"HTTP GET failed: {response.status_code}")
        data = response.json()
        if "member" not in data or not data["member"]:
            print("No observation data available for the requested time range.")
            return None
        return Observation(data["member"][0])

    # --- Convert objects to DataFrame ---
    def features_to_df(self, features):
        """Convert observations to a DataFrame."""
        if not features:
            return pd.DataFrame()
        return pd.DataFrame([f.to_dict() for f in features])

    def observations_to_df(self, observations):
        """Convert observations to a DataFrame."""
        if not observations:
            return pd.DataFrame()
        return pd.DataFrame([obs.to_dict() for obs in observations])

    def points_to_df(self, observation):
        """Convert Observation points to a DataFrame with Time and Value columns.
        Handles None or empty points automatically.
        """
        if not observation:
            print("No observation data available for the requested time range.")
            return pd.DataFrame(columns=["Time", "Value"])
        if not observation.points:
            print("No data points available for this observation.")
            return pd.DataFrame(columns=["Time", "Value"])

        return pd.DataFrame([
            {"Time": p.get("time", {}).get("instant"), "Value": p.get("value")}
            for p in observation.points
        ])

    def plot_observation(self, obs, title=None):
        """Plot time series of an observation. Handles None automatically."""
        if not obs:
            print("No observation data available for the requested time range.")
            return
        if not obs.points:
            print("No data points available for this observation.")
            return

        times = [
            datetime.fromisoformat(p["time"]["instant"].replace("Z", "+00:00"))
            for p in obs.points
        ]
        values = [p["value"] for p in obs.points]

        plt.figure(figsize=(10, 5))
        plt.plot(times, values, "o-", label=obs.observed_property)

        title_str = title or f"{obs.observed_property} time series"
        plt.title(title_str)

        plt.xlabel("Date")
        plt.ylabel(f"Value ({obs.uom})")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()