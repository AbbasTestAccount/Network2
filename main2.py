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
    def __init__(self, data):
        self.id = data[:2]
        print(self.id)
        self.flags = data[2:4]
        self.questions = data[4:6]
        self.number_of_answers = data[6:8]
        self.authority = data[8:10]
        self.additional = data[10:12]
        self.qname = parse_qname(data[12:])
        self.qtype = data[-4:-2]
        self.qclass = data[-2:]

        self.rname = ''
        self.rtype = ''
        self.rclass = ''
        self.ttl = ''
        self.rdlength = ''
        self.rdata = ''

        self.answers = []
        offset = 12 + len(self.qname) + 4
        for i in range(int.from_bytes(self.number_of_answers, byteorder='big')):
            rr_data = data[offset:]
            rr = self.parse_rr(rr_data)
            self.answers.append(rr)
            offset += len(rr_data)

    def parse_rr(self, data):
        return self.parsing(data)

    def parsing(self, data):
        i = 0
        self.rname = parse_qname(data[i:])
        i += len(self.rname) + 2
        self.rtype = data[i:i + 2]
        self.rclass = data[i + 2:i + 4]
        self.ttl = data[i + 4:i + 8]
        self.rdlength = data[i + 8:i + 10]
        self.rdata = data[i + 10:i + 10 + self.rdlength]

    def __str__(self):
        return f"DNS Response: ID={self.id}, QNAME={self.qname}, QTYPE={self.qtype}, QCLASS={self.qclass}, RNAME={self.rname}, RTYPE={self.rtype}, RCLASS={self.rclass}, TTL={self.ttl}, RDLENGTH={self.rdlength}, RDATA={self.rdata}"


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
