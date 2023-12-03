import socket
import time
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address

HOST = sys.argv[1]
PORT = int(sys.argv[2])
buffer = 1024

sender_details = {
    "seq_num": 0,
    "ack_num": 0,
    "syn": 0,
    "ack": 0
}

def setup_socket(ip) -> socket.socket:
    try:
        if type(ip_address(ip) is IPv4Address):
            return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif type(ip_address(ip) is IPv6Address):
            return socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            raise ValueError("Invalid IP type")
    except ValueError as e:
        raise ValueError(f'Invalid IP: {ip}') from e

def send_message(message, sock: socket.socket, seq_num, ack_num, syn, ack_flag):
    attempts = 0

    while attempts < 3:
        head = header.Header(seq_num, ack_num, syn, ack_flag)
        header_bits = head.bits()
        data = message.encode()
        packet = header_bits + data
        # print(f'Packet sent line 20: {packet}')
        print(f'Sent Header:')
        head.details()
        sock.sendto(packet, (HOST, PORT))
        try:
            ack, _ = sock.recvfrom(buffer)
            head = header.bits_to_header(ack)
            print("Received:")
            head.details()
            # print(f'received ack: {head.get_ack() == 1}\n')

            sender_details["seq_num"] = seq_num + 1
            ack_num = head.get_ack_num()
            sender_details["ack_num"] = ack_num
            return True
        except socket.timeout:
            print("No ack\n")
            attempts += 1
    return False

def handshake(sock: socket.socket):
    head = header.Header(0, 0, 1, 0)
    header_bits = head.bits()
    sock.sendto(header_bits, (HOST, PORT))
    try:
        syn_ack, _ = sock.recvfrom(buffer)
        header_bits = header.bits_to_header(syn_ack)
        if header_bits.get_ack() is 1 and header_bits.get_syn() is 1:
            print("You are now connected!")
            header_bits = header.Header(header_bits.get_seq_num(), header_bits.get_ack_num() + 1, 0, 1)
            sock.sendto(header_bits, (HOST, PORT))
        else:
            print("handshake unsuccessful")
            exit(1)
    except socket.timeout:
        print("The socket timed out.")
        exit(1)
    


            

def main():

    try:
        sock = setup_socket(HOST)
        sock.settimeout(3)
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
    except KeyboardInterrupt:
        print("\nClient shut down server")
    finally:
        sock.close()


if __name__ == '__main__':
    main()