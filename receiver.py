import socket
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address

seq_list = []

HOST = sys.argv[1]
PORT = int(sys.argv[2])
buffer = 1024


def create_socket()-> socket.socket:
    # sock
    check_port()
    try:
        ip = type(ip_address(HOST))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, PORT))
        print(f'Socket connected to {HOST},{PORT}')
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.bind((HOST, PORT))
        print(f'Socket connected to {HOST},{PORT}')
    return sock
    

def check_port():
    if PORT is None:
        print("No port number provided!")
        exit(1)
    try:
        return int(PORT)
    except:
        print("port must be an int")

def recv_convert(sock: socket.socket)-> tuple[header.Header, bytes, tuple]:
    data, addr = sock.recvfrom(buffer)
    head = header.bits_to_header(data) 
    body = header.get_body(data)
    return (head, body, addr)

def keep_sequence():
    sorted(seq_list, key=lambda data: data[0].seq_num)

# def print_data():
#     if seq_list[-1][0].seq_num != (seq_list[-2][0].seq_num + 1):
#         return
#     else:
#         #
        
def handshake(sock: socket.socket):
    try:
        syn_ack, _ = sock.recvfrom(buffer)
        header_bits = header.bits_to_header(syn_ack)
        if header_bits.get_syn() == 1:
            header_bits = header.Header(header_bits.get_seq_num(), header_bits.get_ack_num() + 1, 1, 1)
            sock.sendto(header_bits.bits(), (HOST, PORT))
            sock.recvfrom(buffer)
            ack, _ = sock.recvfrom(buffer)
            header_bits = header.bits_to_header(ack)
            if header_bits.get_ack == 1:
                print("Handshake successful, you are now connected!")
        else:
            print("handshake unsuccessful")
            exit(1)
    except socket.timeout:
        print("The socket timed out.")
        exit(1)

def main():
    sock = create_socket()
    seq_num = 1

    while True:
        head, body, addr = recv_convert(sock)
        seq_num += 1
        ack_num = head.seq_num + 1
        ack = header.Header(seq_num, ack_num, 0, 1)
        seq_list.append([head, body])
        keep_sequence()
        sock.sendto(ack.bits, addr)





main()