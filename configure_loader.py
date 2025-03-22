import yaml

_config = None

def load_config():
    global _config
    if _config is None:
        with open('config.yaml', 'r') as stream:
            try:
                _config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                _config = None
    return _config
    