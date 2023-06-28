import json
import socket
import threading

with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

CACHE_EXPIRATION_TIME = settings["cache-expiration-time"]
EXTERNAL_DNS_SERVERS = settings["external-dns-servers"]

cache = {}


def parse_qname(dataToParse):
    domain = ''
    i = 0
    while i < len(dataToParse):
        length = dataToParse[i]
        if length == 0:
            break
        domain += dataToParse[i + 1:i + 1 + length].decode('utf-8') + '.'
        i += length + 1
    return domain


class DNSRequest:
    def __init__(self, data):
        self.id = data[:2]
        self.flags = data[2:4]
        self.questions = data[4:6]
        self.answers = data[6:8]
        self.authority = data[8:10]
        self.additional = data[10:12]
        self.qname = parse_qname(data[12:])
        self.qtype = data[-4:-2]
        self.qclass = data[-2:]


class DNSResponse:
    pass


# ساخت یک سوکت UDP برای گوش دادن به درخواست های DNS
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 53))  # Listen on localhost port 53

while True:
    data, addr = sock.recvfrom(1024)
    threading.Thread(target=DNSRequest(data)).start()

    external_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    external_sock.settimeout(2.0)
    for dns_server in EXTERNAL_DNS_SERVERS:
        try:

            external_sock.sendto(data, (dns_server, 53))

            # دریافت پاسخ از سرور DNS خارجی
            response_data = external_sock.recvfrom(1024)
            response = DNSResponse(response_data)

            # ارسال پاسخ به کلاینت
            sock.sendto(response_data[0], addr)
            print("send : ", response)
            break
        except socket.timeout:
            print("timeout happened")

    external_sock.close()
