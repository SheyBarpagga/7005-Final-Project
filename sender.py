import socket
import time
import sys
import header
import threading
from ipaddress import ip_address, IPv4Address, IPv6Address
import csv
# import matplotlib.pyplot as plt
from itertools import count
# from matplotlib.animation import FuncAnimation

HOST = sys.argv[1]
PORT = int(sys.argv[2])
PROXY_HOST = sys.argv[3]
PROXY_PORT = int(sys.argv[4])

F = open("sender.csv", mode="w", newline='')
WRITER = csv.writer(F)

buffer = 1024

sender_details = {
    "seq_num": 0,
    "ack_num": 1,
}

ack_list = []

# def create_gui_socket()-> tuple[socket.socket, tuple]:
#     # sock
#     # addr
#     try:
#         ip = type(ip_address(HOST))
#     except ValueError:
#         print("Invalid IP")
#         exit(1)
#     if ip is IPv4Address:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind((HOST, 34879))
#         sock.listen(1)
#         client, addr = sock.accept()
#     elif ip is IPv6Address:
#         sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind((HOST, 34879))
#         sock.listen(1)
#         client, addr = sock.accept()
#     return client, addr

def setup_socket() -> socket.socket:
    try:
        if type(ip_address(HOST) is IPv4Address):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((HOST, PORT))
            return sock
        elif type(ip_address(HOST) is IPv6Address):
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.bind((HOST, PORT))
            return sock
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
    #gui_sock.sendto(create_packet("ACK_RECV", 0, 0, 0, 0), gui_addr)
    write_to_csv("", head.get_seq_num(), head.get_ack_num(), head.get_syn(), head.get_ack())
    return (head, body, addr)



def check_ack(head: header.Header):
    print("90")
    h: header.Header
    if head.get_syn() == 0 and head.get_ack() == 0:
        return False
    for h in ack_list:
        if h.get_ack_num() == head.get_ack_num():
            return False
    ack_list.append(head)
    return True

def get_syn_ack(head: header.Header, sock: socket.socket):
    if(head.get_syn() == 1 and head.get_ack() == 1):
        packet = create_packet("", 1, 1, 0, 1)
        sock.sendto(packet, (PROXY_HOST, PROXY_PORT))
        print("You are now connected!")
        return


def send_message(message, sock: socket.socket, seq_num, ack_num, syn, ack_flag):

    attempts = 0

    while attempts < 20:

        packet = create_packet(message, seq_num, ack_num, syn, ack_flag)
        sock.sendto(packet, (PROXY_HOST, PROXY_PORT))
        #gui_sock.sendto(create_packet("DATA_SENT", 0, 0, 0, 0), gui_addr)
        write_to_csv(message, seq_num, ack_num, syn, ack_flag)
        try:
            head = header.Header(0,0,0,0)
            while not check_ack(head):
                head, body, addr = recv_convert(sock)
            sender_details["seq_num"] += head.get_ack_num()
            sender_details["ack_num"] = head.get_ack_num()
            write_to_csv("", head.get_seq_num(), head.get_ack_num(), head.get_syn(), head.get_ack())    
            get_syn_ack(head, sock)
            return True
        except socket.timeout:
            print("No ack\n")
            attempts += 1

    return False


def handshake(sock: socket.socket):
    if not send_message("", sock, 0, 0, 1, 0):
        print("handshake unsuccessful")
        exit(1)
    print("handshake successful")

def write_to_csv(message, seq_num, ack_num, syn, ack_flag):
    if ack_flag == 1:
        data = ["Recieved ack", seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)
    else:
        data = ["Sent message: " + message, seq_num, ack_num, syn, ack_flag]
        WRITER.writerow(data)


def main():
    # sender = Sender()
    try:
        sock = setup_socket()
        sock.settimeout(1.5)
        
    except ValueError as e:
        print(e)
        exit(1)
    # gui_sock, gui_addr = create_gui_socket()
    handshake(sock)
    try:
        while True:
            user_input = input("Enter message: ")
            if not send_message(user_input, sock, sender_details["seq_num"], sender_details["ack_num"], 0, 0):
                print("failed to send after 3 attempts")
                exit()
    except KeyboardInterrupt:
        print("\nClient shut down server")
    finally:
        sock.close()


if __name__ == '__main__':
    main()


    # while attempts < 3:
    #     head = header.Header(seq_num, ack_num, syn, ack_flag)
    #     header_bits = head.bits()
    #     data = message.encode()
    #     packet = header_bits + data
    #     # print(f'Packet sent line 20: {packet}')
    #     print(f'Sent Header:')
    #     head.details()
    #     sock.sendto(packet, (self.HOST, self.PORT))
    #     self.packet_count += 1
    #     try:
    #         ack, _ = sock.recvfrom(self.buffer)
    #         head = header.bits_to_header(ack)
    #         print("Received:")
    #         head.details()
    #         # print(f'received ack: {head.get_ack() == 1}\n')

    #         self.seq_num = seq_num + 1
    #         ack_num = head.get_ack_num()
    #         self.ack_num = ack_num

    #         self.packet_count += 1
    #         return True
    #     except socket.timeout:
    #         print("No ack\n")
    #         attempts += 1
    # return False
    
    # def handshake(self, sock: socket.socket):
    #     head = header.Header(0, 0, 1, 0)
    #     header_bits = head.bits()
    #     sock.sendto(header_bits, (self.HOST, self.PORT))
    #     self.packet_count += 1
    #     try:
    #         syn_ack, _ = sock.recvfrom(self.buffer)
    #         self.packet_count += 1
    #         header_bits = header.bits_to_header(syn_ack)
    #         print("Received:")
    #         header_bits.details()
    #         if header_bits.get_ack() == 1 and header_bits.get_syn() == 1:
    #             print("You are now connected!")
    #             header_bits = header.Header(header_bits.get_seq_num(), header_bits.get_ack_num() + 1, 0, 1)
    #             sock.sendto(header_bits.bits(), (self.HOST, self.PORT))
    #             self.packet_count += 1
    #         else:
    #             print("handshake unsuccessful")
    #             exit(1)
    #     except socket.timeout:
    #         print("The socket timed out.")
    #         exit(1)




# class Sender:
#     def __init__(self):
#         self.HOST = sys.argv[1]
#         self.PORT = int(sys.argv[2])
#         self.buffer = 1024
#         self.seq_num = 0
#         self.ack_num = 0
#         self.syn = 0
#         self.ack = 0
#         self.packet_count = 0
#         self.x_vals = []
#         self.y_vals = []
#         self.index = count()

#     def get_host(self):
#         return self.HOST
    
#     def get_seq_num(self):
#         return self.seq_num
    
#     def get_ack_num(self):
#         return self.ack_num
    
#     def get_syn(self):
#         return self.syn
    
#     def get_ack(self):
#         return self.ack

#     def animate(self, i):
#         self.x_vals.append(next(self.index))
#         self.y_vals.append(self.packet_count)
#         self.packet_count = 0
#         plt.cla()
#         plt.plot(self.x_vals, self.y_vals)

#     def run_graph(self):
#         anim = FuncAnimation(plt.gcf(), self.animate, interval=1000)
#         plt.tight_layout()
#         plt.show()

#     def run_graph(self):
#         anim = FuncAnimation(plt.gcf(), self.animate, interval=1000)
#         plt.tight_layout()
#         plt.show()

#     def run_sender(self, sender):
#         sock = self.setup_socket(self.HOST)
        
#         try:
#             sock = sender.setup_socket(sender.get_host())
#             sock.settimeout(3)
#         except ValueError as e:
#             print(e)
#             exit(1)

#         # sender.handshake(sock)