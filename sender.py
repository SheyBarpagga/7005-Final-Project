import socket
import time
import sys
import header
import threading
from ipaddress import ip_address, IPv4Address, IPv6Address
import matplotlib.pyplot as plt
from itertools import count
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')

class Sender:
    def __init__(self):
        self.HOST = sys.argv[1]
        self.PORT = int(sys.argv[2])
        self.buffer = 1024
        self.seq_num = 0
        self.ack_num = 0
        self.syn = 0
        self.ack = 0
        self.packet_count = 0
        self.x_vals = []
        self.y_vals = []
        self.index = count()

    
    def setup_socket(self, ip) -> socket.socket:
        try:
            if type(ip_address(ip)) is IPv4Address:
                return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            elif type(ip_address(ip)) is IPv6Address:
                return socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            else:
                raise ValueError("Invalid IP type")
        except ValueError as e:
            raise ValueError(f'Invalid IP: {ip}') from e
    

    def send_message(self, message, sock: socket.socket, seq_num, ack_num, syn, ack_flag):
        attempts = 0

        while attempts < 3:
            head = header.Header(seq_num, ack_num, syn, ack_flag)
            header_bits = head.bits()
            data = message.encode()
            packet = header_bits + data
            # print(f'Packet sent line 20: {packet}')
            print(f'Sent Header:')
            head.details()
            sock.sendto(packet, (self.HOST, self.PORT))
            self.packet_count += 1
            try:
                ack, _ = sock.recvfrom(self.buffer)
                head = header.bits_to_header(ack)
                print("Received:")
                head.details()
                # print(f'received ack: {head.get_ack() == 1}\n')

                self.seq_num = seq_num + 1
                ack_num = head.get_ack_num()
                self.ack_num = ack_num

                self.packet_count += 1
                return True
            except socket.timeout:
                print("No ack\n")
                attempts += 1
        return False
    
    def handshake(self, sock: socket.socket):
        head = header.Header(0, 0, 1, 0)
        header_bits = head.bits()
        sock.sendto(header_bits, (self.HOST, self.PORT))
        self.packet_count += 1
        try:
            syn_ack, _ = sock.recvfrom(self.buffer)
            self.packet_count += 1
            header_bits = header.bits_to_header(syn_ack)
            if header_bits.get_ack() is 1 and header_bits.get_syn() is 1:
                print("You are now connected!")
                header_bits = header.Header(header_bits.get_seq_num(), header_bits.get_ack_num() + 1, 0, 1)
                sock.sendto(header_bits.bits(), (self.HOST, self.PORT))
                self.packet_count += 1
            else:
                print("handshake unsuccessful")
                exit(1)
        except socket.timeout:
            print("The socket timed out.")
            exit(1)

    def get_host(self):
        return self.HOST
    
    def get_seq_num(self):
        return self.seq_num
    
    def get_ack_num(self):
        return self.ack_num
    
    def get_syn(self):
        return self.syn
    
    def get_ack(self):
        return self.ack

    def animate(self, i):
        self.x_vals.append(next(self.index))
        self.y_vals.append(self.packet_count)
        self.packet_count = 0
        plt.cla()
        plt.plot(self.x_vals, self.y_vals)

    def run_graph(self):
        anim = FuncAnimation(plt.gcf(), self.animate, interval=1000)
        plt.tight_layout()
        plt.show()

    def run_graph(self):
        anim = FuncAnimation(plt.gcf(), self.animate, interval=1000)
        plt.tight_layout()
        plt.show()

    def run_sender(self, sender):
        sock = self.setup_socket(self.HOST)
        
        try:
            sock = sender.setup_socket(sender.get_host())
            sock.settimeout(3)
        except ValueError as e:
            print(e)
            exit(1)

        sender.handshake(sock)

        try:
            while True:

                seq_num = sender.get_seq_num()
                ack_num = sender.get_ack_num()
                syn = sender.get_syn()
                ack_flag = sender.get_ack()
                user_input = input("Enter message: ")  # Doesn't work for < #.txt

                if not sender.send_message(user_input, sock, seq_num, ack_num, syn, ack_flag):
                    print("failed to send after 3 attempts")
        except KeyboardInterrupt:
            print("\nClient shut down server")
        finally:
            sock.close()

    

def main():
    sender = Sender()

    threading.Thread(target=sender.run_graph).start()
    threading.Thread(target=sender.run_sender(sender)).start()
    

if __name__ == '__main__':
    main()