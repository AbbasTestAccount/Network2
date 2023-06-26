import json
import socket

HOST = "127.0.0.1"
PORT = 5001

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


# at the beginning of the project, we should read our last datas from cache.json
load_cache_from_file()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # use a UDP connection
    s.settimeout(4.0)  # set a timeout to resend data if it didn't send
    s.bind(HOST, PORT)
# todo
# should use some thread here to send N requests


while True:
    requested_domain = ""
    if cache.get(requested_domain):
        print(f'{cache[requested_domain]}cache hit !!!\n')
        continue

    try:
        ip = socket.gethostname(requested_domain)  # get ip
        cache[requested_domain] = ip

        save_cache_to_file()

        print(f'{ip}\n')

    except Exception as e:
        print("error is happened !!!")
