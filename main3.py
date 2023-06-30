import datetime
import json
import socket
import threading

HOST = "127.0.0.1"
PORT = 53

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

        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # use a UDP connection
        #     s.settimeout(4.0)  # set a timeout to resend data if it didn't send
        #     s.bind((HOST, PORT))
        #     # todo
        # should use some thread here to send N requests

        if cache.get(self.requested_domain) and (datetime.datetime.now().timestamp() - cache[self.requested_domain][1]) <= CACHE_EXPIRATION_TIME:
            print(f'name : {self.requested_domain}\nip : {cache[self.requested_domain][0]} cache hit !!!\n')
            cache[self.requested_domain] = (cache[self.requested_domain][0], datetime.datetime.now().timestamp())

        else:
            try:
                ip = socket.gethostbyname(self.requested_domain)  # get ip from DNSServer
                gottenTime = datetime.datetime.now().timestamp()
                cache[self.requested_domain] = (ip,gottenTime)

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
            ip = gethostbyname_manual(self.requested_domain)

            print(f'name : {self.requested_domain}\nip : {ip}\n')

        except Exception as e:
            print(f"name : {self.requested_domain}\nerror is happened while finding ip {e}\n")

def gethostbyname_manual(domain):
    # Set up a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(4.0)

    # Set up the DNS query message
    query = b"\xAB\xCD"  # Message ID
    query += b"\x01\x00"  # Flags
    query += b"\x00\x01"  # Question count
    query += b"\x00\x00"  # Answer count
    query += b"\x00\x00"  # Authority count
    query += b"\x00\x00"  # Additional count
    for label in domain.split("."):
        query += bytes([len(label)]) + label.encode()  # Domain name

    query += b"\x00"  # End of domain name
    query += b"\x00\x01"  # Query type (A record)
    query += b"\x00\x01"  # Query class (Internet)

    # Send the query to a DNS server
    for server in EXTERNAL_DNS_SERVERS:
        try:
            s.sendto(query, (server, 53))
            data, addr = s.recvfrom(1024)
            if data:
                # Parse the response message and extract the IP address
                ip = socket.inet_ntoa(data[-4:])
                return ip
        except socket.timeout:
            pass


domains = [
    "youtube.com"
    , "youtube.com"
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
    , "youtube.com"
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
    , "youtube.com"
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
    , "amazon.com"]

startTime = datetime.datetime.now().timestamp()

for domain in domains:
    dnsServer = DNSServer(domain)
    threading.Thread(target=dnsServer.findIP()).start()

dnsServerTime = datetime.datetime.now().timestamp() - startTime
print("-----------------------------------")
startTime = datetime.datetime.now().timestamp()

for domain in domains:
    dnsProxy = DNSProxy(domain)
    print(cache)
    threading.Thread(target=dnsProxy.findIP()).start()

print("time by using DNS Server : ", dnsServerTime, "\n")

print("time by using DNS Proxy : ", datetime.datetime.now().timestamp() - startTime)
