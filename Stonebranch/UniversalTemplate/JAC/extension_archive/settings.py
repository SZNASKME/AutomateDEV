import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent

YAML_PATH = os.path.join(BASE_DIR, "extension.yml")
extension_yaml = yaml.safe_load(__loader__.get_data(YAML_PATH))
EXTENSION_NAME = extension_yaml["extension"]["name"]
EXTENSION_VERSION = extension_yaml["extension"]["version"]
