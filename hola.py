"""Runs on the machine GitHub lends us, with the Python it already has."""

import os
import platform

print(f"Hola desde Python {platform.python_version()} en {platform.node()}")
print(f"Lo disparó: {os.getenv('GITHUB_ACTOR')} con un {os.getenv('GITHUB_EVENT_NAME')}")
