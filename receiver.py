import socket
import sys
import header
import csv
from ipaddress import ip_address, IPv4Address, IPv6Address

seq_list = []

HOST = sys.argv[1]
PORT = int(sys.argv[2])

F = open("receiver.csv", mode="w", newline='')
WRITER = csv.writer(F)

buffer = 1024

reciever_details = {
    "seq_num": 0,
    "ack_num": 1,
}

def create_gui_socket()-> tuple[socket.socket, tuple]:
    # sock
    # addr
    try:
        ip = type(ip_address(HOST))
        print("27")
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, 34989))
        sock.listen(1)
        client, addr = sock.accept()
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, 34989))
        sock.listen(1)
        client, addr = sock.accept()
    return client, addr

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
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.settimeout(200)
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        # sock.settimeout(20)
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
    print(body)
    write_to_csv(body, head.get_seq_num(), head.get_ack_num(), head.get_syn(), head.get_ack())
    return (head, body, addr)


def check_seq(head: header.Header, sock: socket.socket, addr):
    print("84")
    h: header.Header
    if head.get_ack() == 0 and head.get_ack_num() == 0  and head.get_syn() == 0  and head.get_seq_num() == 0:
        return False
    for h in seq_list:
        if h.get_seq_num() == head.get_seq_num():
            print("Recieved duplicate data\nsequence number: " + str(h.get_seq_num()))
            # sock.sendto(h.bits(), addr)
            return False
    seq_list.append(head)
    return True

def create_packet(syn, ack_flag) -> bytes:
    head = header.Header(reciever_details["seq_num"], reciever_details["ack_num"], syn, ack_flag)
    header_bits = head.bits()
    print(f'Sending Header:')
    head.details()
    write_to_csv("", reciever_details["seq_num"], reciever_details["ack_num"], syn, ack_flag)
    return header_bits

        
def handshake(sock: socket.socket):
    try:
        head, body, addr = recv_convert(sock)
        if head.get_syn() == 1:
            send_ack(sock, addr, 1)
            head, body, addr = recv_convert(sock)
            print(head.get_ack())
            if head.get_ack() == 1:
                reciever_details["seq_num"] += 1
                print("Handshake successful, you are now connected!")
                return addr
        else:
            print("handshake unsuccessful")
            exit(1)
    except socket.timeout:
        print("The socket timed out.")
        exit(1)


def send_ack(sock: socket.socket, addr, syn):
    packet = create_packet(syn, 1)
    sock.sendto(packet, addr)
    #gui_sock.sendto(packet + "ACK_SENT".encode(), gui_addr)


def handle_msg(sock: socket.socket, addr):
    head = header.Header(0,0,0,0)
    try:
        head
        addr
        b = bytes(1)
        if not check_seq(head, sock, addr):
            head, b, addr = recv_convert(sock)
        print("Recieved message:\n" + b)
        reciever_details["ack_num"] += len(b)
        #gui_sock.sendto(head + "DATA_RECV", gui_addr)
        send_ack(sock, addr, 0)
    except socket.timeout:
        print("The other side has disconnected, the socket timed out")
        exit(0)
        
def write_to_csv(message, seq_num, ack_num, syn, ack_flag):
    if ack_flag == 1:
        data = ["Sent ack", seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)
    else:
        data = ["Recieved message: " + message, seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)
       
        

def main():
    sock = create_socket()
    # gui_sock, gui_addr = create_gui_socket()
    addr = handshake(sock)
    while True:
        try:
            handle_msg(sock, addr)
        except socket.timeout:
            print("socket timed out")
            F.close()
            sock.close()
            exit(0)
        except KeyboardInterrupt:
            print("user exited the program")
            F.close()
            sock.close()
            exit(0)



main()
