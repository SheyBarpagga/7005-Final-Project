import socket
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address

seq_list = []

def create_socket()-> tuple[socket.socket, str, int]:
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

def recv_convert(sock: socket)-> tuple[header.Header, bytes, tuple]:
    data, addr = sock.socket.recvfrom(1024)
    head = header.bits_to_header(data) 
    body = header.get_body(data)
    return (head, body, addr)

def keep_sequence():
    sorted(seq_list, key=lambda data: data[0].seq_num)

def print_data():
    if seq_list[-1][0].seq_num != (seq_list[-2][0].seq_num + 1):
        return
    else:
        #
        


def main():
    sock, ip, port = create_socket()
    seq_num = 1
    while True:
        head, body, addr = recv_convert()
        if head.syn == 1:
            ack_num = head.seq_num + 1
            syn_ack = header.Header(seq_num, ack_num, 1, 1)
            sock.sendto(syn_ack.bits(), addr)
        else:
            seq_num += 1
            ack_num = head.seq_num + 1
            ack = header.Header(seq_num, ack_num, 0, 1)
            seq_list.append([head, body])
            keep_sequence()
            sock.sendto(ack.bits, addr)





main()