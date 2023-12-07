import matplotlib.pyplot as plt
from itertools import count
from matplotlib.animation import FuncAnimation
import random

plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()

def animate(i):
    x_vals.append(next(index))
    y_vals.append(random.randint(0, 10))
    plt.cla()
    plt.plot(x_vals, y_vals)


anim = FuncAnimation(plt.gcf(), animate, interval=1000)
plt.tight_layout()
plt.show()