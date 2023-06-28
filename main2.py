import json
import socket

with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

CACHE_EXPIRATION_TIME = settings["cache-expiration-time"]
EXTERNAL_DNS_SERVERS = settings["external-dns-servers"]

cache = {}

# ساخت یک سوکت UDP برای گوش دادن به درخواست های DNS
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 53))  # Listen on localhost port 53

while True:
    data, addr = sock.recvfrom(1024)
