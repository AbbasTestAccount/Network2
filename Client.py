import socket
import time
import random

HOST = "127.0.0.1"
PORT = 53
domains = [
    "youtube.com", "youtube.com", "www.blogger.com", "github.com", "www.google.com", "apple.com", "play.google.com", "support.google.com", "wordpress.org", "linkedin.com", "github.com", "youtube.com", "youtube.com", "www.google.com", "www.google.com", "microsoft.com", "github.com", "cloudflare.com", "youtube.com", "maps.google.com", "www.google.com", "amazon.com", "whatsapp.com", "en.wikipedia.org", "maps.google.com", "youtube.com", "amazon.com", "docs.google.com", "plus.google.com", "adobe.com", "amazon.com", "www.google.com", "sites.google.com", "googleusercontent.com", "drive.google.com", "bp.blogspot.com", "mozilla.org", "accounts.google.com", "europa.eu", "t.me", "www.google.com", "policies.google.com", "github.com", "vk.com", "maps.google.com", "vimeo.com", "istockphoto.com", "uol.com.br", "maps.google.com", "facebook.com", "amazon.com", "maps.google.com", "search.google.com", "adobe.com", "www.google.com", "apple.com", "play.google.com", "support.google.com", "wordpress.org", "linkedin.com", "github.com", "youtube.com", "youtube.com", "www.google.com", "www.google.com", "microsoft.com", "github.com", "cloudflare.com", "youtube.com", "maps.google.com", "www.google.com", "amazon.com", "whatsapp.com", "en.wikipedia.org", "maps.google.com", "youtube.com", "amazon.com", "docs.google.com", "plus.google.com", "adobe.com", "amazon.com", "www.google.com", "sites.google.com", "googleusercontent.com", "drive.google.com", "bp.blogspot.com", "mozilla.org", "accounts.google.com", "europa.eu", "t.me", "www.google.com", "policies.google.com", "github.com", "vk.com", "maps.google.com", "vimeo.com", "istockphoto.com", "uol.com.br", "maps.google.com", "facebook.com", "amazon.com"]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(3.0)
client_socket.connect((HOST, PORT))

for domain in domains:
    client_socket.sendall(domain.encode())
    # user_input = input("Press 'q' to quit: ")
    # if user_input.lower() == "q":
    #     break
    try:
        data = client_socket.recv(1024)
        if (data):
            print(f"domain:{data}")
    except socket.timeout:
        print("client doesn't received any response from the server in 4 seconds")
        pass

    time.sleep(random.uniform(0.1, 1))


# received_data = client_socket.recv(1024)
# print('Received data:', received_data)

client_socket.close()
