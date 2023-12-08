import socket
import multiprocessing
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import header

buffer = 1024

server_descriptions = [('Sender', '10.0.0.34', 34879),
                        ('Receiver', '10.0.0.34', 34989),
                        ('Proxy', '10.0.0.34', 34878)]

packets = {
    'ACK_RECV',
    'ACK_DROP'
    'ACK_DELAY',
    'DATA_RECV',
    'DATA_DROP',
    'DATA_DELAY',
    'ACK_SENT',
    'DATA_SENT'
}

servers = ["Sender", "Receiver", "Proxy"]

colors = [
    'red',
    'green',
    'lightcyan',
    'blue',
    'yellow',
    'orange',
    'purple',
    'pink',
    'gray'
]


    
def recv_convert(sock: socket.socket)-> tuple[header.Header, bytes]:
    data, addr = sock.recv(buffer)
    head = header.bits_to_header(data) 
    body = header.get_body(data)
    return (head, body)    

def get_info(head: header.Header, body):
    ack = head.get_ack()
    if ack == 1:
        if body == "drop":
            return 'ACK_DROP'
        elif body == "delay":
            return 'ACK_DELAY'
        elif body == "recv":
            return 'ACK_RECV'
        else:
            return 'ACK_SENT'
    else:
        if body == "drop":
            return 'DATA_DROP'
        elif body == "delay":
            return 'DATA_DELAY'
        elif body == "recv":
            return 'DATA_RECV'
        else:
            return 'DATA_SENT'


def connect_to_server(sender, host, port, data):
    sock = socket.socket()
    try:
        sock.connect((host, port))
        while True:
            head, body= recv_convert(sock)
            if head:
                info = get_info(head, body)
                print(info)
                data[sender].append((info, time.time()))
    except KeyboardInterrupt:
        pass
    except ConnectionRefusedError:
        print(f"Could not connect to server")
    finally:
        sock.close()


def update_plot(i, ax, sender, data):
    if data[sender]:
        ax.clear()

        times = [t for _, t in data[sender]]
        values = [v for v, _ in data[sender]]

        packet_count_per_type = {ptype: 0 for ptype in range(len(colors))}

        packet_history = {ptype: [] for ptype in range(len(colors))}

        for value, time in zip(values, times):
            packet_count_per_type[value] += 1
            for ptype in packet_history:
                packet_history[ptype].append(packet_count_per_type[ptype])

        for packet_type in range(len(colors)):
            ax.plot(times, packet_history[packet_type], color=colors[packet_type], label=packets[packet_type])

        ax.set_ylabel('Number of Packets')
        ax.set_xlabel('Time')
        ax.set_title(f'Data from {["Sender", "Receiver", "Proxy"][sender]}')

        ax.legend(loc='upper left', fontsize='small')


def start_plot(sender, data):
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax, sender, data), interval=1000)
    plt.show()


def start(data):
    processes = []

    for i, (description, host, port) in enumerate(server_descriptions):
        process = multiprocessing.Process(target=connect_to_server, args=(i, host, port, data))
        process.start()
        processes.append(process)

    for i in range(3):
        plot_process = multiprocessing.Process(target=start_plot, args=(i, data))
        plot_process.start()
        processes.append(plot_process)

    for process in processes:
        process.join()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    manager = multiprocessing.Manager()
    data = manager.dict({0: manager.list(), 1: manager.list(), 2: manager.list()})
    start(data)