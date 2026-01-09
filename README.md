# DAB Pythonic Client (dab-py)
A Python client for DAB functionalities, including DAB Terms API and WHOS API.

## Installation (0.6.0)
Install the core package (includes `pandas` and `matplotlib`):
```bash
pip install --upgrade dab-py
```

## DAB Terms API `dab_py: TermsAPI`
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

## WHOS API `om_api: WHOSClient, Constraints`
This notebook and module are used to programmatically access WHOS DAB functionalities through the OGC OM-JSON based API, which is documented and available for testing here: https://whos.geodab.eu/gs-service/om-api.
### Features
- Pythonic, **object-oriented access** via `Feature` and `Observation` classes. 
- Support **all constrainst** with the **bounding box** as a default and others (e.g., observed property, ontology, country, provider) as optional. 
- Retrieve **features** and **observations** as Python objects using the `Constraints`.
- **Per-page pagination** built in → use `.next()` on object class to fetch subsequent pages.
- Convert API responses to `pandas` DataFrames for easier inspection and analysis. 
- Generate automatic (default) time-series plots of observation data points using `matplotlib`.

### Usage
The tutorial is accessible through our Jupyter Notebook demo: `dab-py_demo_whos.ipynb`.
```bash
from dabpy import WHOSClient, Constraints
from IPython.display import display

# Replace with your WHOS API token and optional view
token = "my-token"  # replace with your actual token
view = "whos"
client = WHOSClient(token=token, view=view)


## 00 DEFINE FEATURE CONSTRAINTS
# Define bounding box coordinates (south, west, north, east), example of Finland.
south = 60.398
west = 22.149
north = 60.690
east = 22.730
# Create feature constraints, only spatial constraints are applied, while the other filters remain optional.
constraints = Constraints(bbox = (south, west, north, east))


## 01 GET FEATURES
# 01.1.1: Retrieve features matching the previously defined constraints (only bbox).
features = client.get_features(constraints)
# 01.1.2: (optional: Convert Features to DataFrame if needed).
features_df = features.to_df()
display(features_df)

'''
--- Use next() only to fetch all the pages ---
# 01.2.1: # Fetch next page (if available).
features.next()
# 01.2.2: (optional) Convert current page features to DataFrame.
features_df = features.to_df() # now includes next page
display(features_df)
'''

## 02 GET OBSERVATIONS
# 02.1.1: Retrieve observations matching the previously defined constraints (only bbox).
observations = client.get_observations(constraints)
# Use 'paginate=True' - observations = client.get_observations(constraints, paginate=True) to fetch all pages.

# 02.1.2: (optional: Convert Observations to DataFrame if needed).
observations_df = client.observations_to_df(observations)
display(observations_df)

# 02.2.1: (or retrieve observations from a different constraints - by defining new_constraints).
new_constraints = Constraints(feature=features[9].id)
observations_new_constraints = client.get_observations(new_constraints)
# Use 'paginate=True' - observations_new_constraints = client.get_observations(new_constraints, paginate=True) to fetch all pages.

# 02.2.2: (optional: Convert Observations to DataFrame if needed)
observations_new_constraints_df = client.observations_to_df(observations_new_constraints)
display(observations_new_constraints_df)


## 03 GET DATA POINTS
# 03.1: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations_new_constraints[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")
# 03.2: (optional: Convert Observation Points to DataFrame if needed)
obs_points_df = client.points_to_df(obs_with_data)
display(obs_points_df)
# 03.3: (optional: Example of Graphical Time-Series)
client.plot_observation(obs_with_data, "Example of Time-series, custom your own title")
```
