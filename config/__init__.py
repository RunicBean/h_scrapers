import os
import configparser


def configure():
    ENV_PATH = os.environ

    try:
        config_path = ENV_PATH['HSCRAPER_CONFIG_PATH']
    except KeyError:
        raise KeyError('No HSCRAPER_CONFIG_PATH variable in environment.')
    conf_parser = configparser.ConfigParser()
    conf_parser.read(config_path)
    return conf_parser
