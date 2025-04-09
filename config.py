import os
import json

# Define the AppData folder path
APPDATA_FOLDER = os.path.join(os.getenv("APPDATA"), "copypaster")
CONFIG_FILE = os.path.join(APPDATA_FOLDER, "config.json")
TEMP_FOLDER = os.path.join(APPDATA_FOLDER, "temp")

# Ensure the temp folder exists
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Default configuration
DEFAULT_CONFIG = {
    "notifications_enabled": True
}

def load_config():
    """Load the configuration from the config file."""
    if not os.path.exists(APPDATA_FOLDER):
        os.makedirs(APPDATA_FOLDER)  # Create the folder if it doesn't exist

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)  # Save default config if the file doesn't exist

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Save the configuration to the config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)