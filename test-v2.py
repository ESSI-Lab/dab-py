from dabpy import WHOSClient, Constraints
from IPython.display import display

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