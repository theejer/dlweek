"""Quick test script to get exact connectivity prediction output."""

import json
from app.services import connectivity_predictor

# Input coordinates: Gopalganj, Bihar
latitude = 26.185754
longitude = 84.881594

print("Input:")
print(json.dumps({
    "latitude": latitude,
    "longitude": longitude
}, indent=2))

print("\nCalling connectivity_predictor.predict_connectivity_for_latlon()...\n")

# Get prediction
result = connectivity_predictor.predict_connectivity_for_latlon(latitude, longitude)

print("Output:")
print(json.dumps(result, indent=2))
