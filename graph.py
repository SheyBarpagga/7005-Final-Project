import socket
import multiprocessing
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import header

HOSTS = [('Sender', '10.0.0.47', 34879),
                        ('Receiver', '10.0.0.47', 34989),
                        ('Proxy', '10.0.0.47', 34878)]

packets = [
    'ACK_RECV',
    'DROP_ACK',
    'DLAY_ACK',
    'DTA_RECV',
    'DROP_DAT',
    'DLAY_DAT',
    'ACK_SENT',
    'DATA_SNT'
]

servers = ["Sender", "Receiver", "Proxy"]

colors = [
    'pink',
    'blue',
    'green',
    'orange',
    'yellow',
    'red',
    'purple',
    'gray'
]


    
def recv_convert(sock: socket.socket)-> tuple[bytes]:
    data = sock.recv(8)
    if data.decode() == '':
        return (0)
    print(data.decode())
    return data.decode()   



def connect_to_server(sender, host, port, data):
    sock = socket.socket()
    try:
        sock.connect((host, port))
        while True:
            body = recv_convert(sock)
            if(body != 0):
                data[sender].append((packets.index(body), time.time()))
    except KeyboardInterrupt:
        print("exiting...")
    finally:
        sock.close()

def set_grph(ax, sender):
        ax.set_ylabel('Number of Packets')
        ax.set_xlabel('Time')
        ax.set_title(f'Data from {["Sender", "Receiver", "Proxy"][sender]}')

        ax.legend(loc='upper left')

# def handle_socket(sock, label, data_queue):
#     timestamps = []
#     data_types = []

#     plt.ion()  # Turn on interactive mode
#     fig, ax = plt.subplots()

#     while True:
#         data = sock.recv(8)
#         if not data:
#             break

#         timestamp = time.time()
#         data_type = struct.unpack('8s', data)[0].decode('utf-8').strip('\x00')
#         print(f"Received {data_type} from {label} at {timestamp}")

#         # Enqueue data for plotting
#         data_queue.put((timestamp, data_type))

#         # Plot data
#         timestamps.append(timestamp)
#         data_types.append(data_type)
#         ax.clear()
#         ax.scatter(timestamps, data_types, color='blue')
#         ax.set(xlabel='Time', ylabel='Data Type')
#         plt.pause(0.1)
#         # plt.show()

def update_plot(i, ax, sender, data):
    if data[sender]:
        ax.clear()

        times = [t for _, t in data[sender]]
        values = [v for v, _ in data[sender]]
        print(data[sender])

        pckt_counts = {pckt: 0 for pckt in range(len(colors))}
        print(pckt_counts)
        prev = {pckt: [] for pckt in range(len(colors))}

        for value, time in zip(values, times):
            print(value)
            pckt_counts[value] += 1
            for pckt in prev:
                prev[pckt].append(pckt_counts[pckt])

        for packet in range(len(colors)):
            ax.plot(times, prev[packet], color=colors[packet], label=packets[packet])
        set_grph(ax, sender)


def grph(sender, data):
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax, sender, data), interval=1000, save_count=100)
    plt.show()


def init(data):
    processes = []
    for i, (description, host, port) in enumerate(HOSTS):
        process = multiprocessing.Process(target=connect_to_server, args=(i, host, port, data))
        process.start()
        processes.append(process)

    for i in range(3):
        plot_process = multiprocessing.Process(target=grph, args=(i, data))
        plot_process.start()
        processes.append(plot_process)

    for process in processes:
        process.join()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    manager = multiprocessing.Manager()
    data = manager.dict({0: manager.list(), 1: manager.list(), 2: manager.list()})
    init(data)

