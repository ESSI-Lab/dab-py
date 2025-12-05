from dabpy import WHOSClient, Constraints

# Replace with your WHOS API token and optional view
token = "my-token"
view = "whos"
client = WHOSClient(token=token, view=view)

# 00: Define the bounding box (Finland Example Area)
south, west, north, east = 60.347, 22.438, 60.714, 23.012
constraints = Constraints(bbox=(south, west, north, east))

# 01: Get Features as Python objects
features = client.get_features(constraints)
# 01b: (optinal: Convert Features to DataFrame if needed)
features_df = client.features_to_df(features)
print("\n=== Features Table ===")
print(features_df)

# 02: Get Observations as Python objects
feature_id = features[4].id
observations = client.get_observations(feature_id)
# 02b: (optinal: Convert Observations to DataFrame if needed)
observations_df = client.observations_to_df(observations)
print("\n=== Observations Table ===")
print(observations_df)

# 03: Get first observation with data points
obs_with_data = client.get_observation_with_data(observations[0].id, begin="2025-01-01T00:00:00Z", end="2025-02-01T00:00:00Z")
# 03b: (optinal: Convert Observation Points to DataFrame if needed)
if obs_with_data:
    obs_points_df = client.points_to_df(obs_with_data)
    print("\n=== Observation Points Table ===")
    print(obs_points_df)
else:
    print("No observation data available for the requested time range.")