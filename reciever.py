import socket
import sys
import header
import utils


from ipaddress import ip_address, IPv4Address, IPv6Address

def create_socket():
    sock
    port = get_port()
    try:
        ip = type(ip_address(sys.argv[2]))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.bind(sys.argv[2], port)
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(sys.argv[2], port)
    return sock, sys.argv[2], port
    

def get_port():
    port = sys.argv[1]
    if port is None:
        print("No port number provided!")
        exit(1)
    try:
        return int(port)
    except:
        print("port must be an int")

def recv_convert(sock: socket):
    data, addr = sock.socket.recvfrom(1024)
    head = utils.bits_to_header(data) 
    body = utils.get_body(data)
    return (head, body, addr)


def main():
    sock, ip, port = create_socket()
    while True:
        head, body = recv_convert()
        if head.syn == 1:
            seq_num = 1
            ack_num = head.seq_num + 1

    
create_socket()