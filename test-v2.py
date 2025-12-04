from dabpy import WHOSClient, Constraints

# Replace with your WHOS API token and optional view
token = "my-token"
view = "whos"  # default view
client = WHOSClient(token=token, view=view)

# 00: Define the bounding box (Finland Example Area)
south = 60.347
west = 22.438
north = 60.714
east = 23.012
constraints = Constraints(bbox=(south, west, north, east))

# 01: Get features as Python objects
features = client.get_features(constraints)
for f in features:
    print(f.id, f.name, f.coordinates, f.contact_name)

# 02: Get observations as Python objects
feature_id = features[4].id
observations = client.get_observations(feature_id)
for obs in observations:
    print(obs.id, obs.observed_property, obs.uom)

# 03: Plot first observation
obs_with_data = client.get_observation_with_data(observations[0].id,
                                                 begin="2025-01-01T00:00:00Z",
                                                 end="2025-02-01T00:00:00Z")

if obs_with_data is not None:
    client.plot_observation(obs_with_data)
else:
    print("No observation data available for the requested time range.")