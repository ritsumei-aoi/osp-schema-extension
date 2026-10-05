import json
import numpy as np

# Copy verification_results.json from scratch to docs/issues/verification_results.json
with open("scratch/verification_results.json", "r") as f:
    data = json.load(f)

with open("docs/issues/verification_results.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved docs/issues/verification_results.json successfully!")
