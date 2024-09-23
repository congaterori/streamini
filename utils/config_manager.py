import yaml

CONFIG_FILE = "config/assistant.yaml"

def load_config():
    """Loads configuration from the YAML file."""
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config

def update_config(key, value):
    """Updates a specific key in the YAML configuration file."""
    config = load_config()
    config[key] = value
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)
