import socket
import time
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address

HOST = sys.argv[1]
PORT = int(sys.argv[2])
buffer = 1024
connected = False

ack_list = []

sender_details = {
    "seq_num": 0,
    "ack_num": 0,
    "syn": 0,
    "ack": 0
}

def setup_socket() -> socket.socket:
    try:
        if type(ip_address(HOST) is IPv4Address):
            return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif type(ip_address(HOST) is IPv6Address):
            return socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            raise ValueError("Invalid IP type")
    except ValueError as e:
        raise ValueError(f'Invalid IP: {HOST}') from e
    

def create_packet(message: str, seq_num, ack_num, syn, ack_flag):
    head = header.Header(seq_num, ack_num, syn, ack_flag)
    header_bits = head.bits()
    data = message.encode()
    packet = header_bits + data
    print(f'Sending Header:')
    head.details()
    return packet


def recv_convert(sock: socket.socket)-> tuple[header.Header, bytes, tuple]:
    data, addr = sock.recvfrom(buffer)
    head = header.bits_to_header(data) 
    body = header.get_body(data)
    print("Received:")
    head.details()
    return (head, body, addr)


def update_seq(head: header.Header):
    sender_details["seq_num"] += 1
    ack_num = head.get_ack_num()
    sender_details["ack_num"] = ack_num

def check_ack(head: header.Header):
    h: header.Header
    for h in ack_list:
        if h.get_ack_num() == head.get_ack_num():
            return False
    ack_list.append(head)
    return True

def get_syn_ack(head: header.Header, sock: socket.socket):
    if(head.get_syn == 1 and head.get_ack == 1):
        if(not connected):
            packet = create_packet("", 1, 1, 0, 1)
            sock.sendto(packet, (HOST, PORT))
            connected = True
            print("You are now connected!")
        print("duplicate syn,ack recieved")

def send_message(message, sock: socket.socket, seq_num, ack_num, syn, ack_flag):

    attempts = 0

    while attempts < 3:

        packet = create_packet(message, seq_num, ack_num, syn, ack_flag)
        sock.sendto(packet, (HOST, PORT))

        try:
            head = header.Header(0,0,0,0)

            while not check_ack(head):
                head, body, addr = recv_convert(sock)
                
            get_syn_ack(head, sock)
            update_seq(head)

            return True
        
        except socket.timeout:
            print("No ack\n")
            attempts += 1

    return False



def handshake(sock: socket.socket):
    if not send_message("", sock, 0, 0, 1, 0):
        print("handshake unsuccessful")
        exit(1)
    
    

            

def main():

    try:
        sock = setup_socket()
        sock.settimeout(1)
    except ValueError as e:
        print(e)
        exit(1)
    handshake(sock)
    try:
        while True:
            seq_num = sender_details["seq_num"]
            ack_num = sender_details["ack_num"]
            syn = sender_details["syn"]
            ack_flag = sender_details["ack"]
            user_input = input("Enter message: ")  # Doesn't work for < #.txt
            if not send_message(user_input, sock, seq_num, ack_num, syn, ack_flag):
                print("failed to send after 3 attempts")
                exit()
    except KeyboardInterrupt:
        print("\nClient shut down server")
    finally:
        sock.close()


if __name__ == '__main__':
    main()