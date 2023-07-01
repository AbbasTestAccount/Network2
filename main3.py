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
        print(self.domain, self.type)

    def findIP(self):
        # at the beginning of the project, we should read our last datas from cache.json
        load_cache_from_file()
        if cache.get(self.domain):
            ip, gottonTime = cache[self.domain]
            if ((now() - gottonTime) <= CACHE_EXPIRATION_TIME):
                print(
                    f'name : {self.domain}\nip : {ip} cache hit !!!\n')
                cache[self.domain] = (ip, now())
                print(ip)
                return ip

        else:
            try:
                # get ip from DNSServer
                ip = gethostbyname_manual(self.domain)
                cache[self.domain] = (ip, now())
                save_cache_to_file()
                return ip
            except Exception as e:
                traceback.print_exc()
                print(
                    f"name : {self.requested_domain}\nerror is happened while finding ip {e}\n")
        return None


def inet_ntoa(addr):
    octets = []
    for i in range(4):
        octet = addr & 0xFF  # Extract the least significant 8 bits
        octets.append(str(octet))
        addr >>= 8  # Shift the address right by 8 bits to get the next octet
    return '.'.join(reversed(octets))


def gethostbyname_manual(domain):
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
    query += b"\x00\x01"  # Query type (A record)
    query += b"\x00\x01"  # Query class (Internet)

    # Send the query to a DNS server
    for server in EXTERNAL_DNS_SERVERS:
        try:
            s.sendto(query, (server, 53))
            data, addr = s.recvfrom(1024)
            if data:
                # Parse the response message and extract the IP address
                # if query_type == 1 or query_type == 28:
                #     ip_address = socket.inet_ntoa(response[-4:]) if query_type == 1 else socket.inet_ntop(
                #         socket.AF_INET6, response[-16:])
                #     cache[cache_key] = ip_address
                #     save_cache_to_file()
                ip = socket.inet_ntoa(data[-4:])
                return ip
        except socket.timeout:
            pass


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
                    s.sendto(ip.encode(), addr)
                else:
                    message = "IP of the domain isn't available"
                    s.sendto(message.encode(), addr)
                # print(cache)
            except socket.timeout:
                break

print("time by using DNS Proxy : ",
      now() - startTime)
