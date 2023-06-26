import datetime
import json
from nslookup import Nslookup

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


class DNSProxy:
    def __init__(self, requested_domain):
        self.requested_domain = requested_domain

    def findIP(self):

    # at the beginning of the project, we should read our last datas from cache.json
        load_cache_from_file()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # use a UDP connection
            s.settimeout(4.0)  # set a timeout to resend data if it didn't send
            s.bind((HOST, PORT))
            # todo
            # should use some thread here to send N requests

            if cache.get(self.requested_domain):
                print(f'name : {self.requested_domain}\nip : {cache[self.requested_domain]} cache hit !!!\n')
            else:
                try:
                    ip = socket.gethostbyname(self.requested_domain)  # get ip from DNSServer
                    cache[self.requested_domain] = ip

                    save_cache_to_file()

                    print(f'name : {self.requested_domain}\nip : {ip}\n')

                except Exception as e:
                    print(f"name : {self.requested_domain}\nerror is happened while finding ip {e}\n")


class DNSServer:
    def __init__(self, requested_domain):
        self.requested_domain = requested_domain

    def findIP(self):
        try:
            # get ip from DNSServer
            ip = socket.gethostbyname(self.requested_domain)

            print(f'name : {self.requested_domain}\nip : {ip}\n')

        except Exception as e:
            print(f"name : {self.requested_domain}\nerror is happened while finding ip {e}\n")


domains = {"youtube.com"
    , "www.blogger.com"
    , "github.com"
    , "www.google.com"
    , "apple.com"
    , "play.google.com"
    , "support.google.com"
    , "wordpress.org"
    , "linkedin.com"
    , "github.com"
    , "youtube.com"
    , "youtube.com"
    , "www.google.com"
    , "www.google.com"
    , "microsoft.com"
    , "github.com"
    , "cloudflare.com"
    , "youtu.be"
    , "maps.google.com"
    , "www.google.com"
    , "amazon.com"
    , "whatsapp.com"
    , "en.wikipedia.org"
    , "maps.google.com"
    , "youtube.com"
    , "amazon.com"
    , "docs.google.com"
    , "plus.google.com"
    , "adobe.com"
    , "amazon.com"
    , "www.google.com"
    , "sites.google.com"
    , "googleusercontent.com"
    , "drive.google.com"
    , "bp.blogspot.com"
    , "mozilla.org"
    , "accounts.google.com"
    , "europa.eu"
    , "t.me"
    , "www.google.com"
    , "policies.google.com"
    , "github.com"
    , "vk.com"
    , "maps.google.com"
    , "vimeo.com"
    , "istockphoto.com"
    , "uol.com.br"
    , "maps.google.com"
    , "facebook.com"
    , "amazon.com"
    , "maps.google.com"
    , "search.google.com"
    , "adobe.com"
    , "www.google.com"
    , "apple.com"
    , "play.google.com"
    , "support.google.com"
    , "wordpress.org"
    , "linkedin.com"
    , "github.com"
    , "youtube.com"
    , "youtube.com"
    , "www.google.com"
    , "www.google.com"
    , "microsoft.com"
    , "github.com"
    , "cloudflare.com"
    , "youtu.be"
    , "maps.google.com"
    , "www.google.com"
    , "amazon.com"
    , "whatsapp.com"
    , "en.wikipedia.org"
    , "maps.google.com"
    , "youtube.com"
    , "amazon.com"
    , "docs.google.com"
    , "plus.google.com"
    , "adobe.com"
    , "amazon.com"
    , "www.google.com"
    , "sites.google.com"
    , "googleusercontent.com"
    , "drive.google.com"
    , "bp.blogspot.com"
    , "mozilla.org"
    , "accounts.google.com"
    , "europa.eu"
    , "t.me"
    , "www.google.com"
    , "policies.google.com"
    , "github.com"
    , "vk.com"
    , "maps.google.com"
    , "vimeo.com"
    , "istockphoto.com"
    , "uol.com.br"
    , "maps.google.com"
    , "facebook.com"
    , "amazon.com"}

startTime = datetime.datetime.now().timestamp()

for domain in domains:
    dnsServer = DNSServer(domain)
    dnsServer.findIP()

dnsServerTime = datetime.datetime.now().timestamp() - startTime
print("-----------------------------------")
startTime = datetime.datetime.now().timestamp()

for domain in domains:
    dnsProxy = DNSProxy(domain)
    dnsProxy.findIP()


print("time by using DNS Server : ", dnsServerTime, "\n")

print("time by using DNS Proxy : ", datetime.datetime.now().timestamp() - startTime)
