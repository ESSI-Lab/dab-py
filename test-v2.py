from dabpy import *
from IPython.display import display

# Replace with your token and optional view (WHOS or HIS-Central)
token = "my-token"  # replace with your actual token
view = "whos" # replace with 'whos' or 'his-central'
client = DABClient(token=token, view=view)

# ----------------------------
# 1. GET DATA (FEATURES AND OBSERVATIONS)
# ----------------------------

'''--------- 1.0 DEFINE THE CONSTRAINTS ---------'''
# 00.1: Define bounding box coordinates (south, west, north, east), example of Turku, Finland.
south = 60.398
west = 22.149
north = 60.690
east = 22.730
# 00.2: Create the constraints, only spatial constraints are applied in this example, while the other filters remain optional.
constraints = Constraints(bbox = (south, west, north, east))

'''--------- 1.1 GET DATA FEATURES ---------'''
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

'''--------- 1.2 GET DATA OBSERVATIONS ---------'''
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

'''--------- 1.3 GET DATA POINTS ---------'''
## 01.3 GET DATA POINTS
# 01.3.1: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations_new_constraints[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")
# 01.3.2: (optional: Convert Observation Points to DataFrame if needed)
obs_points_df = client.points_to_df(obs_with_data)
display(obs_points_df)
# 01.3.3: (optional: Example of Graphical Time-Series)
client.plot_observation(obs_with_data, "Example of Time-series, custom your own title")


# ----------------------------
# 2. DOWNLOAD DATA OBSERVATIONS (APPLICABLE ONLY FOR HIS-CENTRAL SERVER *AT THE MOMENT*)
# ----------------------------

'''--------- 00 DEFINE THE CONSTRAINTS ---------'''
# 00.1: Define bounding box coordinates (or you can use from previous one)
south_2 = 41.777
west_2 = 12.392
north_2 = 41.832
east_2 = 12.456
# 00.2: Create New DownloadConstraints
download_constraints = DownloadConstraints(
    bbox = (south_2, west_2, north_2, east_2),
    # if use from previous define constraints --> base_constraints = constraints,
    asynchDownloadName = "download_example" # Name the downloaded file is mandatory
)

'''--------- 01 PUT: Create Download ---------'''
# 01.01: PUT: Create Download
create_resp = client.create_download(download_constraints)
# 01.02: Optional: Create and Save Automatically
create_save_resp = client.create_save_download(download_constraints, filename = None)

'''--------- 02 GET: Check Status of Downloaded List ---------'''
# 02.01: GET: Check Status of Downloaded List
download_id = None
status_resp = client.get_download_status(download_id)
display(status_resp.to_df())
# 02.02: Optional: Save the Downloaded File Locally
save_resp = client.save_download(download_id, filename = None)

'''--------- 03 DELETE: Delete by ID ---------'''
# 03.01: DELETE: Delete by ID
delete_resp = client.delete_download(download_id)
print(delete_resp)