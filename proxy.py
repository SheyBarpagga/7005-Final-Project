import socket
import random
import threading
import time
import sys
import header
import csv
from ipaddress import ip_address, IPv4Address, IPv6Address


SEND_HOST = sys.argv[1]
SEND_PORT = int(sys.argv[2])
RECV_HOST = sys.argv[3]
RECV_PORT = int(sys.argv[4])
HOST = sys.argv[5]
GUI_PORT = 34878
PORT = 34901
PORTR = 34906

F = open("proxy.csv", mode="w", newline='')
WRITER = csv.writer(F)


buffer = 1024


def create_socket(host, port)-> socket.socket:
    try:
        ip = type(ip_address(host))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, int(port)))
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, int(port)))
    return sock

def write_to_csv(message, seq_num, ack_num, syn, ack_flag):
    if ack_flag == 1:
        data = ["ack", seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)
    else:
        data = ["data: " + message, seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)

def create_gui_socket()-> socket.socket:
    try:
        ip = type(ip_address(HOST))
    except ValueError:
        print("Invalid IP")
        exit(1)
    if ip is IPv4Address:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, int(GUI_PORT)))
        sock.listen(1)
        sock.accept()
    elif ip is IPv6Address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, int(GUI_PORT)))
        sock.listen(1)
        sock.accept()
    return sock



def get_sockets()-> tuple[socket.socket, socket.socket]:
    return create_socket(HOST, PORT), create_socket(HOST, PORTR)


def recv_print(sock: socket.socket)-> tuple[bytes, tuple]:
    data, addr = sock.recvfrom(buffer)
    head = header.bits_to_header(data)
    print("Received: ")
    head.details()
    return (data, addr)


def create_packet(message: str, seq_num, ack_num, syn, ack_flag):
    head = header.Header(seq_num, ack_num, syn, ack_flag)
    header_bits = head.bits()
    data = message.encode()
    packet = header_bits + data
    return packet




def handle_packet(sock: socket.socket, gui_sock: socket.socket, drop, delay, data, addr):
    head = header.bits_to_header(data)
    if drop_rand(drop):
        print("Dropped packet:\nsequence number: " + head.get_seq_num() + "\nack number: " + head.get_ack_num())
        write_to_csv("drop: " + header.get_body(data), head.get_seq_num(), head.get_ack_num(), head.get_syn(), head.get_ack())
        if(head.get_ack() == 1):
            gui_sock.sendto("DROP_ACK".encode(), int(GUI_PORT))
        else:
            gui_sock.sendto("DROP_DAT".encode(), int(GUI_PORT))
        return
    if sleep_rand(delay):
        write_to_csv("delay: " + header.get_body(data), head.get_seq_num(), head.get_ack_num(), head.get_syn(), head.get_ack())
        if(head.get_ack() == 1):
            gui_sock.sendto("DLAY_ACK".encode(), int(GUI_PORT))
        else:
            gui_sock.sendto("DLAY_DAT".encode(), int(GUI_PORT))
    sock.sendto(data, addr)



def handle_send(sock: socket.socket, gui_sock: socket.socket, drop, delay):
    try:
        while True:
            data, _ = recv_print(sock)
            print(_)
            if(_ == (SEND_HOST, SEND_PORT)):
                handle_packet(sock, gui_sock, drop, delay, data, (RECV_HOST, RECV_PORT))
            else:
                handle_packet(sock, gui_sock, drop, delay, data, (SEND_HOST, SEND_PORT))
    except KeyboardInterrupt:
        print("Client shutdown proxy")
    finally:
        sock.close()
        exit(0)



def sleep_rand(percentage):
    if(random.uniform(0,100) < percentage):
        time.sleep(random.uniform(0, 2.5))
        return True
    else:
        return False


def drop_rand(percentage):
    if(random.uniform(0,100) < percentage):
        return True
    else:
        return False


def get_inputs():
    data_drop = input("Enter the percentage of data packets to drop: ")
    data_delay = input("Enter the percentage of data packets to delay: ")
    ack_drop = input("Enter the percentage of ack packets to drop: ")
    ack_delay = input("Enter the percentage of ack packets to delay: ")
    return int(data_drop), int(data_delay), int(ack_drop), int(ack_delay)

# def handle_gui(sock: socket, gui_sock: socket.socket, )



def main():
    data_drop, data_delay, ack_drop, ack_delay = get_inputs()
    ack_sock, data_sock = get_sockets()
    # sock = create_socket(HOST, PORT)
    gui_sock = create_gui_socket()

    recv_thread = threading.Thread(target=handle_send, args=(ack_sock, gui_sock, ack_drop, ack_delay))
    sender_thread = threading.Thread(target=handle_send, args=(data_sock, gui_sock, data_drop, data_delay))
    # recv_thread = threading.Thread(target=handle_send, args=(ack_sock, ack_drop, ack_delay))
    # sender_thread = threading.Thread(target=handle_send, args=(data_sock, data_drop, data_delay))

    recv_thread.start()
    sender_thread.start()
    recv_thread.join()
    sender_thread.join()




if __name__ == "__main__":
    main()
