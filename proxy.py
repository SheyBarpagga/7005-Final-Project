import socket
import random
import threading
import time
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address


RECV_HOST = sys.argv[1]
RECV_PORT = sys.argv[2]
SEND_HOST = sys.argv[3]
SEND_PORT = sys.argv[4]

HOST = sys.argv[5]

buffer = 1024

def create_socket()-> socket.socket:
    sock
    check_port()
    try:
        ip = type(ip_address(HOST))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.bind(HOST, SEND_PORT)
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(HOST, SEND_PORT)
    return sock


def check_port(port):
    if port is None:
        print("No port number provided!")
        exit(1)
    try:
        return int(port)
    except:
        print("port must be an int")

def proxy():
    proxy_sock = create_socket()

    receiver_addr = (RECV_HOST, RECV_PORT)

    while True:
        data, sender_addr = proxy_sock.recvfrom(1024)
        print(f"Received packet from sender: {data.decode()}")
        send_to_receiver(data, proxy_sock, receiver_addr)

        ack_data, _ = proxy_sock.recvfrom(1024)
        print(f"Received ACK from receiver: {ack_data.decode()}")
        send_to_sender(ack_data, proxy_sock, sender_addr)


def send_to_receiver(data, sock: socket.socket, addr):
    sleep_rand(25)
    if drop_rand():
        print("Dropped packet to receiver")
    else:
        sock.sendto(data, addr)

def send_to_sender(data, sock: socket.socket, addr):
    sleep_rand(25)
    if drop_rand():
        print("Dropped ACK to sender")
    else:
        sock.sendto(data, addr)

if __name__ == "__main__":

    proxy_thread = threading.Thread(target=proxy, args=())
    proxy_thread.start()

    proxy_thread.join()

def sleep_rand(percentage):
    if(random.uniform(0,100) < percentage):
        time.sleep(random.uniform(0, 2))

def drop_rand(percentage):
    if(random.uniform(0,100) < percentage):
        return True


