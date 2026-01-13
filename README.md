# DAB Pythonic Client (dab-py)
A Python client for DAB functionalities, including DAB Terms API and WHOS API.

## Installation (0.9.0)
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

## DAB API `om_api: DABClient, WHOSClient, HISCentralClient, Constraints`
This notebook and module provide programmatic access to DAB services (currently WHOS and HIS-Central) via the OGC OM-JSON API. The API is documented and available for testing here: https://gs-service-preproduction.geodab.eu/gs-service/om-api/
- **WHOS:** https://whos.geodab.eu/gs-service/om-api
- **HIS-Central:** https://his-central.geodab.eu/gs-service/om-api/
### Features
- Generic DAB client (`DABClient`) for core functionality shared across services. 
- Service-specific subclasses (`WHOSClient`, `HISCentralClient`) for convenient instantiation with the correct base URL.
- Pythonic, **object-oriented access** via `Feature`, `Observation`, and `Download` classes. 
- Support **all constrainst** with the **bounding box** as a default and others (e.g., observed property, ontology, country, provider) as optional. 
  - Retrieve **features** and **observations** as Python objects using the `Constraints`. 
  - Extended download-specific constraints via `DownloadConstraints`.
    - PUT: Create asynchronous downloads
    - GET: Check download status by download ID
    - DELETE: Remove downloads by ID (no indexing required)
- **Per-page pagination** built in → use `.next()` on object class to fetch subsequent pages.
- Convert API responses to `pandas` DataFrames for easier inspection and analysis. 
- Generate automatic (default) time-series plots of observation data points using `matplotlib`.

### Usage
The tutorial is accessible through our Jupyter Notebook demo: https://github.com/ESSI-Lab/dab-pynb.
```bash
from dabpy import *
from IPython.display import display


# Replace with your token and optional view (WHOS or HIS-Central)
token = "my-token"  # replace with your actual token
view = "whos" # replace with 'whos' or 'his-central'
client = DABClient(token=token, view=view)

'''--------- 00 DEFINE THE CONSTRAINTS ---------'''
# 00.1: Define bounding box coordinates (south, west, north, east), example of Finland.
south = 60.398
west = 22.149
north = 60.690
east = 22.730
# 00.2: Create the constraints, only spatial constraints are applied in this example, while the other filters remain optional.
constraints = Constraints(bbox = (south, west, north, east))

'''--------- 01 GET DATA ---------'''
## 01.1 GET FEATURES
# 01.1.1: Retrieve features matching the previously defined constraints (only bbox).
features = client.get_features(constraints)
# 01.1.2: (optional: Convert Features to DataFrame if needed).
features_df = features.to_df()
display(features_df)

'''
--- Use next() only to fetch all the pages ---
# 01.2.1: # Fetch next page (if available).
nextFeatures = features.next()
# 01.2.2: (optional) Convert current page features to DataFrame.
nextFeatures_df = nextFeatures.to_df()   
display(nextFeatures_df)
'''

## 01.2 GET OBSERVATIONS
# 01.2.1: Retrieve observations matching the previously defined constraints (only bbox).
observations = client.get_observations(constraints)

# 01.2.2: (optional: Convert Observations to DataFrame if needed)
observations_df = observations.to_df()
display(observations_df)

# 01.2.3: (or) retrieve observations from a different constraints - by defining new_constraints.
new_constraints = Constraints(feature=features[9].id)
observations_new_constraints = client.get_observations(new_constraints)

# 01.2.4: (optional: Convert Observations to DataFrame if needed)
observations_new_constraints_df = observations_new_constraints.to_df()
display(observations_new_constraints_df)


## 01.3 GET DATA POINTS
# 01.3.1: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations_new_constraints[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")
# 01.3.2: (optional: Convert Observation Points to DataFrame if needed)
obs_points_df = client.points_to_df(obs_with_data)
display(obs_points_df)
# 01.3.3: (optional: Example of Graphical Time-Series)
client.plot_observation(obs_with_data, "Example of Time-series, custom your own title")

'''--------- 02 DOWNLOAD DATA OBSERVATIONS ---------'''
# 02.00: Define bounding box coordinates (or you can use from previous one)
south_2 = 41.722
west_2 = 12.233
north_2 = 41.791
east_2 = 12.296

# 02.01: Create New DownloadConstraints
download_constraints = DownloadConstraints(
    bbox = (south_2, west_2, north_2, east_2),
    # if use from previous define constraints, base_constraints = constraints,
    asynchDownloadName = "download_example" # Name the downloaded file is mandatory
)

# 02.02: PUT: Create Download
create_resp = client.create_download(download_constraints)
print(create_resp)
# Extract download ID (real ID used internally)
download_id = create_resp["id"]

# 02.03: GET: Check Status of Downloaded List
downloads = client.get_download_status(download_id)
display(downloads.to_df())

# 02.04: DELETE: Delete by ID
delete_resp = client.delete_download(download_id)
print(delete_resp)
```
