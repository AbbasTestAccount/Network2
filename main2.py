import json
import socket
import struct
import threading

with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

CACHE_EXPIRATION_TIME = settings["cache-expiration-time"]
EXTERNAL_DNS_SERVERS = settings["external-dns-servers"]

cache = {}

HOST = "127.0.0.1"
PORT = 53


def load_cache_from_file():
    global cache
    with open("cache.json", "r") as cache_file:
        # load data from json
        cache = json.load(cache_file)


def save_cache_to_file():
    with open("cache.json", "w") as cache_file:
        # covert into json
        json.dump(cache, cache_file)


def parse_qname(dataToParse):
    domain = ''
    i = 0
    while i < len(dataToParse):
        length = dataToParse[i]
        if length == 0:
            i += 1
            break
        domain += dataToParse[i + 1:i + 1 + length].decode('utf-8') + '.'
        i += length + 1

    qtype = dataToParse[i: i + 2]
    qclass = dataToParse[i + 2: i + 4]

    return domain, qtype, qclass


def parse_rname(dataToParse):
    domain = ''
    i = 0
    while i < len(dataToParse):
        length = dataToParse[i]
        if length == 0:
            i += 1
            break
        domain += dataToParse[i + 1:i + 1 + length].decode('utf-8') + '.'
        i += length + 1

    return domain


def dNSRequest(data):
    print(data)
    id = data[:2]
    flags = data[2:4]
    questions = data[4:6]
    answers = data[6:8]
    authority = data[8:10]
    additional = data[10:12]
    qname, qtype, qclass = parse_qname(data[12:])
    # qtype = data[-4:-2]
    # qclass = data[-2:]

    print(qtype)
    final_output = id + flags + questions + answers + authority + additional + qtype + qclass

    return final_output


def dNSResponse(data):
    id = data[:2]
    flags = data[2:4]
    questions = data[4:6]
    number_of_answers = data[6:8]
    authority = data[8:10]
    additional = data[10:12]
    qname = parse_qname(data[12:])
    qtype = data[-4:-2]
    qclass = data[-2:]

    final_output = id + flags + questions + number_of_answers + authority + additional + qtype + qclass

    offset = 12 + len(qname) + 4
    answers = []
    for i in range(int.from_bytes(number_of_answers, byteorder='big')):
        rr_data = data[offset:]
        rname, rtype, rclass, ttl, rdlength, rdata = parsing(rr_data)
        answers.append(rname + rtype + rclass + ttl + rdlength + rdata)
        offset += len(rr_data)
    for j in range(0, len(answers)):
         final_output+= answers[j]

    return final_output


def parsing(data):
    i = 0
    rname = parse_rname(data[i:])
    i += len(rname) + 2
    rtype = data[i:i + 2]
    rclass = data[i + 2:i + 4]
    ttl = data[i + 4:i + 8]
    rdlength = data[i + 8:i + 10]
    rdata = data[i + 10:i + 10 + rdlength]
    return rname, rtype, rclass, ttl, rdlength, rdata


def __str__(self):
    return f"DNS Response: ID={self.id}, QNAME={self.qname}, QTYPE={self.qtype}, QCLASS={self.qclass}, RNAME={self.rname}, RTYPE={self.rtype}, RCLASS={self.rclass}, TTL={self.ttl}, RDLENGTH={self.rdlength}, RDATA={self.rdata}"


class DNSProxy:
    def findIP(self):
        load_cache_from_file()

        domain_name = parse_qname(data[12:])
        query_type = struct.unpack(">H", data[-4:-2])[0]
        cache_key = f"{domain_name}_{query_type}"

        if cache_key in cache:
            ip_address = cache[cache_key]
            response = dNSResponse(data)
            sock.sendto(response, addr)
        else:
            for dns_server in EXTERNAL_DNS_SERVERS:
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    client_socket.settimeout(1)
                    client_socket.sendto(data, (dns_server, PORT))
                    response, _ = client_socket.recvfrom(1024)

                    if len(response) > 0:
                        sock.sendto(response, addr)

                        if query_type == 1 or query_type == 28:
                            ip_address = socket.inet_ntoa(response[-4:]) if query_type == 1 else socket.inet_ntop(
                                socket.AF_INET6, response[-16:])
                            cache[cache_key] = ip_address
                            save_cache_to_file()

                        break
                except socket.timeout:
                    continue


def runDNSServer(dns_req):
    print(dns_req)
    for dns_server in EXTERNAL_DNS_SERVERS:
        try:
            external_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            external_sock.settimeout(2.0)
            external_sock.sendto(dns_req, (dns_server, PORT))

            # دریافت پاسخ از سرور DNS خارجی
            response_data = external_sock.recvfrom(1024)
            print(f'response_data: {response_data}')

            response = dNSResponse(response_data)

            # ارسال پاسخ به کلاینت
            sock.sendto(response_data[0], addr)
            print("send : ", response)
            break
        except socket.timeout:
            print("timeout happened")

    external_sock.close()


# ساخت یک سوکت UDP برای گوش دادن به درخواست های DNS
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))  # Listen on localhost port 53
while True:
    data, addr = sock.recvfrom(1024)
    dns_req = dNSRequest(data)
    threading.Thread(target=runDNSServer(dns_req)).start()

    # if dns_req.qtype != (b'\x00\x01' or b'\x00\x1C'):
    #     print("Unsupported Query Type")
    #     continue
