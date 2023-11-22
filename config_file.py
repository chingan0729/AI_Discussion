from configparser import ConfigParser

config = ConfigParser()

try:
    config.read("config.ini")
except:
    # print(config["API"]["OPENAI_API_KEY"])
    raise SystemExit()