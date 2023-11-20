import socket
import time
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address

HOST = sys.argv[1]
PORT = int(sys.argv[2])
buffer = 1024


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

def send_message(message, sock):
    attempts = 0
    while attempts < 3:
        head = header.Header(1, 0, 1, 0) # hardcoded placeholder
        header_bits = head.bits()
        data = message.encode()
        packet = header_bits + data
        print(f'Packet sent line 20: {packet}')

        sock.sendto(packet, (HOST, PORT))
        try:
            # add seq num, ack num logic as well
            ack, _ = sock.recvfrom(buffer)

            head = header.bits_to_header(ack)
            head.details()
            print(f'received ack: {head.get_ack() == 1}\n')
            return True
        except socket.timeout:
            print("No ack\n")
            attempts += 1
    return False



def main():
    try:
        sock = setup_socket(HOST)
        sock.settimeout(3)
    except ValueError as e:
        print(e)
        exit(1)

    try:
        while True:
            user_input = input("Enter message: ")  # Doesn't work for < #.txt
            if not send_message(user_input, sock):
                print("failed to send after 3 attempts")
    except KeyboardInterrupt:
        print("\nClient shut down server")
    finally:
        sock.close()


if __name__ == '__main__':
    main()