from dabpy import *
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
nextFeatures = features.next()
# 01.2.2: (optional) Convert current page features to DataFrame.
nextFeatures_df = nextFeatures.to_df()   
display(nextFeatures_df)
'''

## 02 GET OBSERVATIONS
# 02.1.1: Retrieve observations matching the previously defined constraints (only bbox).
observations = client.get_observations(constraints)

# 02.1.2: (optional: Convert Observations to DataFrame if needed)
observations_df = observations.to_df()
display(observations_df)

# 02.2.1: (or) retrieve observations from a different constraints - by defining new_constraints.
new_constraints = Constraints(feature=features[9].id)
observations_new_constraints = client.get_observations(new_constraints)

# 02.2.2: (optional: Convert Observations to DataFrame if needed)
observations_new_constraints_df = observations_new_constraints.to_df()
display(observations_new_constraints_df)


## 03 GET DATA POINTS
# 03.1: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations_new_constraints[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")
# 03.2: (optional: Convert Observation Points to DataFrame if needed)
obs_points_df = client.points_to_df(obs_with_data)
display(obs_points_df)
# 03.3: (optional: Example of Graphical Time-Series)
client.plot_observation(obs_with_data, "Example of Time-series, custom your own title")