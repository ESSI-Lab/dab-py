# DAB Pythonic Client (dab-py)
A Python client for DAB functionalities, including DAB Terms API and WHOS API.

## Installation (0.4.0)
Install the core package (includes `pandas` and `matplotlib`):
```bash
pip install --upgrade dab-py
```

## DAB Terms API `dabpy`
This repository contains a minimal client for retrieving controlled vocabulary terms (e.g., instruments) from the Blue-Cloud/GeoDAB service using a token and view.
### Features
- Retrieve terms from the DAB Terms API with a single call.
- Simple object model: Term and Terms containers.
- Small dependency footprint (requests).
### Usage
```bash
from dabpy import TermsAPI

def main():
    # Blue-Cloud/GeoDAB provided credentials for the public terms view
    token = "my-token"
    view = "blue-cloud-terms"

    # Desired parameters
    term_type = "instrument"
    max_terms = 10

    # Call the API. The implementation prints:
    # - Number of terms received from API: <n>
    # - A header line and up to `max_terms` items
    api = TermsAPI(token=token, view=view)
    api.get_terms(type=term_type, max=max_terms)

if __name__ == "__main__":
    main()

```

## WHOS API `om_api`
This notebook and module are used to programmatically access WHOS DAB functionalities through the OGC OM-JSON based API, which is documented and available for testing here: https://whos.geodab.eu/gs-service/om-api.
### Features
- Pythonic, **object-oriented access** via `Feature` and `Observation` classes. 
- Support **all constrainst** with the **bounding box** as a default and others (e.g., observed property, ontology, country, provider) as optional. 
- Retrieve **features** and **observations** as Python objects.
- Convert API responses to `pandas` DataFrames for easier inspection and analysis. 
- Generate automatic (default) time-series plots of observation data points using `matplotlib`.

### Usage
The tutorial is accessible through our Jupyter Notebook demo: `dab-py_demo_whos.ipynb`.
```bash
from dabpy import WHOSClient, Constraints

# Replace with your WHOS API token and optional view
token = "my-token"
view = "whos"
client = WHOSClient(token=token, view=view)

## 00 DEFINE FEATURE CONSTRAINTS
# Define bounding box coordinates (south, west, north, east)
south = 60.347
west = 22.438
north = 60.714
east = 23.012

# Create feature constraints, only spatial constraints are applied, while the other filters remain optional.
constraints = Constraints(bbox = (south, west, north, east))

## 01 GET FEATURES
# 01.1: Get Features as Python objects
features = client.get_features(constraints)

# 01.1: (optional: Convert Features to DataFrame if needed)
features_df = client.features_to_df(features)
if features_df is not None:
    display(features_df)


## 02 GET OBSERVATIONS
# 02.1: Get Observations as Python objects
feature_used = features[4]
feature_id = feature_used.id
observations = client.get_observations(feature_id)

# 02.2: (optional: Convert Observations to DataFrame if needed)
observations_df = client.observations_to_df(observations)
if observations_df is not None:
    display(observations_df)

## 03 GET DATA POINTS
# 03.1: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")

# 03.2: (optional: Convert Observation Points to DataFrame if needed)
if obs_with_data:
    obs_points_df = client.points_to_df(obs_with_data)
    display(obs_points_df)
else:
    print("No observation data available for the requested time range.")

# 03.3: (optional: Example of Graphical Time-Series)
if obs_with_data:
    client.plot_observation(obs_with_data, feature=feature_used)
else:
    print("No observation data available for the requested time range.")
```

