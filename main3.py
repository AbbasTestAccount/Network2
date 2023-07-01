import datetime
import json
import socket
import random
import traceback

HOST = "127.0.0.1"
PORT = 53

with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

CACHE_EXPIRATION_TIME = settings["cache-expiration-time"]
EXTERNAL_DNS_SERVERS = settings["external-dns-servers"]

cache = {}


def now():
    return datetime.datetime.now().timestamp()


def save_cache_to_file():
    with open("cache.json", "w") as cache_file:
        # covert into json
        json.dump(cache, cache_file)


def load_cache_from_file():
    global cache
    try:
        with open("cache.json", "r") as cache_file:
            # load data from json
            cache = json.load(cache_file)
    except json.decoder.JSONDecodeError as e:
        pass


class DNSProxy:
    def __init__(self, query):
        self.extract_data(query)

    def extract_data(self, query):
        index = 12
        query_name = ''
        while True:
            label_length = query[index]
            if label_length == 0:
                break
            index += 1
            query_name += query[index:index+label_length].decode('utf-8') + '.'
            index += label_length
        self.domain = query_name[:-1]  # Remove the trailing period

        # Extract the query type
        self.type = (query[index+1] << 8) + query[index+2]

    def get_type(self):
        return self.type

    def findIP(self):
        # at the beginning of the project, we should read our last datas from cache.json
        load_cache_from_file()
        if cache.get(self.domain) and (now() - cache[self.domain][1]) <= CACHE_EXPIRATION_TIME:
            ip, gottonTime = cache[self.domain]
            print(
                f'name : {self.domain}\nip : {ip} cache hit !!!\n')
            return ip

        else:
            try:
                # get ip from DNSServer
                ip = gethostbyname_manual(self.domain, self.type)
                if (ip):
                    cache[self.domain] = (ip, now())
                    save_cache_to_file()
                return ip
            except Exception as e:
                print(
                    f"name : {self.domain}\nerror is happened while finding ip {e}\n")
        return None


def inet_ntoa(addr):
    octets = []
    for i in range(4):
        octet = addr & 0xFF  # Extract the least significant 8 bits
        octets.append(str(octet))
        addr >>= 8  # Shift the address right by 8 bits to get the next octet
    return '.'.join(reversed(octets))


def gethostbyname_manual(domain, query_type):
    # Set up a UDP socket
    if type(domain) is bytes:
        domain = domain.decode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(4.0)

    message_id = random.randint(0, 65535)
    # Set up the DNS query message
    query = message_id.to_bytes(2, byteorder="big")  # Message ID
    query += b"\x01\x00"  # Flags
    query += b"\x00\x01"  # Question count
    query += b"\x00\x00"  # Answer count
    query += b"\x00\x00"  # Authority count
    query += b"\x00\x00"  # Additional count
    for label in domain.split("."):
        query += bytes([len(label)]) + label.encode()  # Domain name

    query += b"\x00"  # End of domain name
    # query += b"\x00\x01"  # Query type (A record)
    if query_type == 1:  # A record
        query += b"\x00\x01"  # Query type (A record)
    elif query_type == 28:  # AAAA record
        query += b"\x00\x1c"  # Query type (AAAA record)
    else:
        raise ValueError("Invalid query type")
    query += b"\x00\x01"  # Query class (Internet)

    # Send the query to a DNS server
    for server in EXTERNAL_DNS_SERVERS:
        try:
            s.sendto(query, (server, 53))
            res, addr = s.recvfrom(1024)
            if res:
                if query_type == 1:  # A record
                    ip = socket.inet_ntoa(res[-4:])
                elif query_type == 28:  # AAAA record
                    ip = socket.inet_ntop(socket.AF_INET6, res[-16:])
                return ip
        except socket.timeout:
            pass


def generate_response_query(data, ip, query_type):
    # Construct the DNS response message
    response = b""
    response += data[:2]  # Copy the transaction ID from the query message
    response += b"\x81\x80"  # Flags: response message, no errors
    response += data[4:6]  # Questions count
    response += b"\x00\x01"  # Answer RRs count: 1
    response += b"\x00\x00"  # Authority RRs count
    response += b"\x00\x00"  # Additional RRs count

    # Answer section
    response += data[12:]  # Copy the question section from the query message
    response += b"\xc0\x0c"  # Pointer to the question section
    if query_type == 1:  # A record
        response += b"\x00\x01"  # Query type (A record)
        response += b"\x00\x04"  # Data length: 4 bytes for IPv4 address
        response += socket.inet_aton(ip)
    elif query_type == 28:  # AAAA record
        response += b"\x00\x1c"  # Query type (AAAA record)
        response += b"\x00\x10"  # Data length: 16 bytes for IPv6 address
        response += socket.inet_pton(socket.AF_INET6, ip)
    response += b"\x00\x01"  # Class: IN
    # TTL: cache expiration time
    response += int.to_bytes(CACHE_EXPIRATION_TIME, 4, byteorder="big")
    return response


startTime = now()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # use a UDP connection
    s.settimeout(6.0)
    s.bind((HOST, PORT))
    while True:
        data, addr = s.recvfrom(1024)
        if (data):
            try:
                dnsProxy = DNSProxy(data)
                ip = dnsProxy.findIP()
                if (ip):
                    s.sendto(generate_response_query(
                        data, ip, dnsProxy.get_type()), addr)
                else:
                    message = "IP of the domain isn't available"
                    s.sendto(message.encode(), addr)
            except socket.timeout:
                break

print("time by using DNS Proxy : ",
      now() - startTime)
