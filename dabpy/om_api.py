import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
from datetime import datetime

def obfuscate_token(url, token):
    """Replace the token in a URL with '***' for safe printing."""
    return url.replace(token, "***")

# --- Feature and Observation classes ---
class Feature:
    def __init__(self, feature_json):
        self.id = feature_json["id"]
        self.name = feature_json["name"]
        self.coordinates = feature_json["shape"]["coordinates"]
        self.parameters = {param["name"]: param["value"] for param in feature_json["parameter"]}
        self.related_party = feature_json.get("relatedParty", [])
        self.contact_name = self.related_party[0].get("individualName", "") if self.related_party else ""
        self.contact_email = self.related_party[0].get("electronicMailAddress", "") if self.related_party else ""

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
    def __init__(self, obs_json):
        params = {param["name"]: param["value"] for param in obs_json.get("parameter", [])}
        self.id = obs_json["id"]
        self.source = params.get("source")
        self.observed_property = obs_json.get("observedProperty", {}).get("title")
        self.phenomenon_time_begin = obs_json.get("phenomenonTime", {}).get("begin")
        self.phenomenon_time_end = obs_json.get("phenomenonTime", {}).get("end")
        self.points = obs_json.get("result", {}).get("points", [])

    def to_dict(self):
        return {
            "ID": self.id,
            "Source": self.source,
            "Observed Property": self.observed_property,
            "Phenomenon Time Begin": self.phenomenon_time_begin,
            "Phenomenon Time End": self.phenomenon_time_end
        }

    def __repr__(self):
        return f"<Observation id={self.id} property={self.observed_property}>"

# --- Collections with per-page support ---
class FeaturesCollection:
    """Collection of features with per-page pagination."""
    def __init__(self, client, constraints, initial_features=None, resumption_token=None, page=1, verbose=True):
        self.client = client
        self.constraints = constraints
        self.features = initial_features or []
        self.current_page_features = initial_features or []
        self.resumption_token = resumption_token
        self.completed = False
        self.page = page
        self.verbose = verbose
        if self.verbose:
            self._print_summary(len(self.current_page_features))

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx]

    def next(self):
        if self.completed or not self.resumption_token:
            print("No more data to fetch.")
            return self

        url = f"{self.client.base_url}features?{self.constraints.to_query()}&resumptionToken={urllib.parse.quote(self.resumption_token)}"
        self.page += 1
        if self.verbose:
            print(f"Retrieving page {self.page}: {url.replace(self.client.token, '***')}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        new_features = [Feature(f) for f in data.get("results", [])]
        self.current_page_features = new_features
        self.features.extend(new_features)
        token = data.get("resumptionToken")
        self.resumption_token = token.split(",")[0] if token else None
        self.completed = data.get("completed", True) or not self.resumption_token

        if self.verbose:
            self._print_summary(len(new_features))

        return self

    def to_df(self):
        return pd.DataFrame([f.to_dict() for f in self.current_page_features])

    def _print_summary(self, n_returned):
        prefix = "first" if self.page == 1 else "next"
        msg = f"Returned {prefix} {n_returned} features"
        if self.completed:
            print(msg + " (completed, data finished).")
        elif self.resumption_token:
            print(msg + " (not completed, more data available).\nUse class.next() to move to the next page.")
        else:
            print(msg + " (completed, data finished).")  # edge case: no token but completed=False

class ObservationsCollection:
    """Collection of observations with per-page pagination."""
    def __init__(self, client, constraints, initial_obs=None, resumption_token=None, page=1, verbose=True):
        self.client = client
        self.constraints = constraints
        self.observations = initial_obs or []
        self.current_page_obs = initial_obs or []
        self.resumption_token = resumption_token
        self.completed = False
        self.page = page
        self.verbose = verbose
        if self.verbose:
            self._print_summary(len(self.current_page_obs))

    def __len__(self):
        return len(self.observations)

    def __getitem__(self, idx):
        return self.observations[idx]

    def next(self):
        if self.completed or not self.resumption_token:
            print("No more data to fetch.")
            return self

        url = f"{self.client.base_url}observations?{self.constraints.to_query()}&resumptionToken={urllib.parse.quote(self.resumption_token)}"
        self.page += 1
        if self.verbose:
            print(f"Retrieving page {self.page}: {url.replace(self.client.token, '***')}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        new_obs = [Observation(o) for o in data.get("member", [])]
        self.current_page_obs = new_obs
        self.observations.extend(new_obs)
        token = data.get("resumptionToken")
        self.resumption_token = token.split(",")[0] if token else None
        self.completed = data.get("completed", True) or not self.resumption_token

        if self.verbose:
            self._print_summary(len(new_obs))

        return self

    def to_df(self):
        return pd.DataFrame([o.to_dict() for o in self.current_page_obs])

    def _print_summary(self, n_returned):
        prefix = "first" if self.page == 1 else "next"
        msg = f"Returned {prefix} {n_returned} observations"
        if self.completed:
            print(msg + " (completed, data finished).")
        elif self.resumption_token:
            print(msg + " (not completed, more data available).\nUse class.next() to move to the next page.")
        else:
            print(msg + " (completed, data finished).")  # edge case

# --- WHOS Client ---
class WHOSClient:
    def __init__(self, token, view="whos"):
        self.token = token
        self.view = view
        self.base_url = f"https://whos.geodab.eu/gs-service/services/essi/token/{token}/view/{view}/om-api/"

    def get_features(self, constraints, verbose=True):
        url = f"{self.base_url}features?{constraints.to_query()}"
        if verbose:
            print(f"Retrieving page 1: {obfuscate_token(url, self.token)}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        features_list = [Feature(f) for f in data.get("results", [])]
        token = data.get("resumptionToken")
        resumption_token = token.split(",")[0] if token else None
        collection = FeaturesCollection(self, constraints, features_list, resumption_token, page=1, verbose=verbose)
        collection.completed = data.get("completed", True)
        return collection

    def get_observations(self, constraints, verbose=True):
        url = f"{self.base_url}observations?{constraints.to_query()}"
        if verbose:
            print(f"Retrieving page 1: {obfuscate_token(url, self.token)}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        obs_list = [Observation(o) for o in data.get("member", [])]
        token = data.get("resumptionToken")
        resumption_token = token.split(",")[0] if token else None
        collection = ObservationsCollection(self, constraints, obs_list, resumption_token, page=1, verbose=verbose)
        collection.completed = data.get("completed", True)
        return collection

    def get_observation_with_data(self, observation_id, begin=None, end=None):
        url = self.base_url + f"observations?includeData=true&observationIdentifier={urllib.parse.quote(observation_id)}"
        if begin:
            url += "&beginPosition=" + urllib.parse.quote(begin)
        if end:
            url += "&endPosition=" + urllib.parse.quote(end)
        print("Retrieving " + obfuscate_token(url, self.token))
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if "member" not in data or not data["member"]:
            print("No observation data available for the requested time range.")
            return None
        return Observation(data["member"][0])

    def features_to_df(self, features):
        if not features:
            return pd.DataFrame()
        return pd.DataFrame([f.to_dict() for f in features])

    def observations_to_df(self, observations):
        if not observations:
            return pd.DataFrame()
        return pd.DataFrame([o.to_dict() for o in observations])

    def points_to_df(self, observation):
        if not observation or not observation.points:
            return pd.DataFrame(columns=["Time", "Value"])
        return pd.DataFrame([{"Time": p.get("time", {}).get("instant"), "Value": p.get("value")} for p in observation.points])

    def plot_observation(self, obs, title=None):
        if not obs or not obs.points:
            print("No data points available for this observation.")
            return
        times = [datetime.fromisoformat(p["time"]["instant"].replace("Z", "+00:00")) for p in obs.points]
        values = [p["value"] for p in obs.points]
        plt.figure(figsize=(10,5))
        plt.plot(times, values, "o-", label=obs.observed_property)
        plt.title(title or f"{obs.observed_property} time series")
        plt.xlabel("Date")
        plt.ylabel(f"Value ({getattr(obs,'uom', '')})")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
