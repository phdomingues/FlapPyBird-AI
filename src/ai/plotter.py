import itertools
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np
import queue
from functools import partial
from matplotlib.collections import PathCollection
from typing import Any

class NetworkPlotter:
    def __init__(self) -> None:
        self.plot_queue = mp.Queue(1)
        self.process = mp.Process(target=NetworkPlotter.subprocess, args=(self.plot_queue,))
        self.process.start()
    
    def update(self, activations: dict[str, Any]):
        try:
            self.plot_queue.put_nowait(activations)
        except queue.Full:
            self.plot_queue.get_nowait()
            self.plot_queue.put_nowait(activations)

    def subprocess(plot_queue):
        neuron_coords = {
            'input': tuple(zip(np.repeat(5, 5), np.arange(5,26,5))),
            'fc1': tuple(zip(np.repeat(25, 6), np.arange(2.5,28,5))),
            'fc2': tuple(zip(np.repeat(45, 3), np.arange(10,21,5))),
            'output': ((65,15),)
        }

        neuron_x = [item for row in map(lambda a: [x[0] for x in a], neuron_coords.values()) for item in row]
        neuron_y = [item for row in map(lambda a: [x[1] for x in a], neuron_coords.values()) for item in row]
        fig, ax = plt.subplots()
        ax.set_axis_off()
        # Plot connections
        layers = ['input', 'fc1', 'fc2', 'output']
        plot_connections = {layer: dict() for layer in layers}
        for i in range(len(layers)-1):
            back_layer = neuron_coords[layers[i]]
            front_layer = neuron_coords[layers[i+1]]
            indexer = range(len(back_layer))
            for (idx, back_coord), front_coord in list(itertools.product(zip(indexer, back_layer),front_layer)):
                x = [back_coord[0], front_coord[0]]
                y = [back_coord[1], front_coord[1]]
                line = ax.plot(x, y, color='k', lw=2, alpha=1, zorder=0)
                try:
                    plot_connections[layers[i]][idx].extend(line)
                except KeyError:
                    plot_connections[layers[i]][idx] = line
            pass
        # Plot neurons
        plot_neurons = ax.scatter(neuron_x, neuron_y, s=400, facecolors='w', edgecolors='k', lw=1, zorder=1)

        ani = animation.FuncAnimation(fig, partial(NetworkPlotter.animate, neurons=plot_neurons, connections=plot_connections, queue=plot_queue), interval=1)
        plt.show()

    def animate(frame, neurons:PathCollection=None, connections=None, queue=None):
        data = queue.get()
        layers = ['input', 'fc1', 'fc2']
        for layer in layers:
            for cons, activation in zip(connections[layer].values(), data[layer]):
                activation = max(-1,min(1,activation)) # Constraints activation between -1 and 1
                for con in cons:
                    con.set_color('g' if activation > 0 else 'r')
                    con.set_linewidth(1 + (3 - 1) * abs(activation))

        neurons.set_facecolor(['w' for _ in range(14)] + ['g' if data['fc3'] > 0.5 else 'r'])
    
    def __del__(self):
        self.process.join(10)
        if self.process.is_alive():
            self.process.terminate()
        self.process.close()