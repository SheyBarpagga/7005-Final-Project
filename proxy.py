import socket
import random
import threading
import time
import sys
import header
from ipaddress import ip_address, IPv4Address, IPv6Address


SEND_HOST = sys.argv[1]
SEND_PORT = sys.argv[2]
RECV_PORT = sys.argv[3]
HOST = sys.argv[4]
GUI_PORT = sys.argv[5]

buffer = 1024

def create_socket(host, port, b)-> socket.socket:
    if b == 1:
        try:
            ip = type(ip_address(host))
        except ValueError:
            print("Invalid IP")
            exit(1)
        if ip is IPv4Address:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((host, port))
        elif ip is IPv6Address:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.bind((host, port))
        return sock
    else:
        try:
            ip = type(ip_address(HOST))
        except ValueError:
            print("Invalid IP")
            exit(1)
        if ip is IPv4Address:
            return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif ip is IPv6Address:
            return socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def create_gui_socket()-> socket.socket:
    try:
        ip = type(ip_address(HOST))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, GUI_PORT))
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.bind((HOST, GUI_PORT))
    return sock

    

def get_sockets()-> tuple[socket.socket, socket.socket]:
    return create_socket(SEND_HOST, SEND_PORT, 0), create_socket(HOST, RECV_PORT, 1)

def recv_print(sock: socket.socket)-> tuple[bytes, tuple]:
    data, addr = sock.recvfrom(buffer)
    head = header.bits_to_header(data) 
    print("Received: ")
    head.details()
    return (data, addr)

def handle_ack(sock: socket.socket, drop, delay):
    data, addr = recv_print(sock)
    if drop_rand(drop):
        print("Dropped ACK to sender")
    sleep_rand(delay)
    sock.sendto(data, addr)
    return(data, addr)

def handle_data(sock: socket.socket, drop, delay):
    data, addr = recv_print(sock)
    if drop_rand(drop):
        print("Dropped data to reciever")
    sleep_rand(delay)
    sock.sendto(data, addr)
    return (data, addr)

def handle_recv(sock: socket.socket, gui_sock: socket.socket, drop, delay):
    try:
        while True:
            data, addr = handle_ack(sock, drop, delay)
            gui_sock.sendto(data, addr)
    except KeyboardInterrupt:
        print("Client shutdown proxy")
    finally:
        sock.close()
        exit(0)

def handle_sender(sock: socket.socket, gui_sock: socket.socket, drop, delay):
    try:
        while True:
            data, addr = handle_data(sock, drop, delay)
            gui_sock.sendto(data, addr)
    except KeyboardInterrupt:
        print("Client shutdown proxy")
    finally:
        sock.close()
        exit(0)

def sleep_rand(percentage):
    if(random.uniform(0,100) < percentage):
        time.sleep(random.uniform(0, 2.5))

def drop_rand(percentage):
    if(random.uniform(0,100) < percentage):
        return True

def get_inputs():
    data_drop = input("Enter the percentage of data packets to drop: ")
    data_delay = input("Enter the percentage of data packets to delay: ")
    ack_drop = input("Enter the percentage of ack packets to drop: ")
    ack_delay = input("Enter the percentage of ack packets to delay: ")
    return data_drop, data_delay, ack_drop, ack_delay


def main():
    data_drop, data_delay, ack_drop, ack_delay = get_inputs()
    ack_sock, data_sock = get_sockets()
    gui_sock = create_gui_socket()
    recv_thread = threading.Thread(target=handle_recv, args=(ack_sock, gui_sock, ack_drop, ack_delay))
    sender_thread = threading.Thread(target=handle_sender, args=(data_sock, gui_sock, data_drop, data_delay))

    recv_thread.start()
    sender_thread.start()
    recv_thread.join()
    sender_thread.join()


if __name__ == "__main__":
    main()




