import tomllib

def load_config(path="config/config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)