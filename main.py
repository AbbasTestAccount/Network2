import json

with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

CACHE_EXPIRATION_TIME = settings["cache-expiration-time"]
EXTERNAL_DNS_SERVERS = settings["external-dns-servers"]

cache = {}


def save_cache_to_file():
    with open("cache.json", "w") as cache_file:
        # covert into json
        json.dump(cache, cache_file)


def load_cache_from_file():
    global cache
    with open("cache.json", "r") as cache_file:
        # load data from json
        cache = json.load(cache_file)


print(CACHE_EXPIRATION_TIME, EXTERNAL_DNS_SERVERS)
