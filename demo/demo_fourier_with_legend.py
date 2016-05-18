import math

import numpy as np

from artist import Plot


L = 2 * math.pi


def square(x):
    """Square wave of period 2*L"""

    def H(x):
        """Heaveside step function"""

        if x < 0.:
            return 0.
        if x == 0.:
            return 0.5
        if x > 0.:
            return 1.
    return 2 * (H(x / L) - H(x / L - 1)) - 1


def fourier(x, N):
    """Fourier approximation with N terms"""

    term = 0.
    for n in range(1, N, 2):
        term += (1. / n) * math.sin(n * math.pi * x / L)
    return (4. / (math.pi)) * term


def add_custom_pin(plot, x, y, label, distance='3ex'):
    """Add a pin at the maximum value of a data series (sort of)"""

    # only use the second quarter, for cosmetic reasons
    q = int(0.25 * len(y))
    y = y[q:2*q]
    max_index = q + np.argmax(y)
    max_x = x[max_index]
    plot.add_pin(label, x=max_x, location='above', use_arrow=True,
                 style='pin distance=%s' % distance)


X = np.linspace(0., 2 * L, num=1000)
Y_sqr = [square(x) for x in X]
Y = lambda n: [fourier(x, n) for x in X]

graph = Plot()
graph.set_title("Fourier approximation")

graph.plot(x=X, y=Y(3), linestyle='red', mark=None, legend='n=3')
graph.plot(x=X, y=Y(5), linestyle='yellow', mark=None, legend='n=5')
graph.plot(x=X, y=Y(8), linestyle='green', mark=None, legend='n=8')
graph.plot(x=X, y=Y(13), linestyle='blue', mark=None, legend='n=13')
graph.plot(x=X, y=Y(55), linestyle='cyan', mark=None, legend='n=55')
graph.plot(x=X, y=Y_sqr, linestyle='black', mark=None, legend='square')

graph.save('fourier_with_legend')

graph = Plot()
graph.set_title("Fourier approximation")

graph.plot(x=X, y=Y(3), mark=None, linestyle='black!20')
add_custom_pin(graph, X, Y(3), 3)
graph.plot(x=X, y=Y(5), mark=None, linestyle='black!30')
add_custom_pin(graph, X, Y(5), 5)
graph.plot(x=X, y=Y(8), mark=None, linestyle='black!40')
add_custom_pin(graph, X, Y(8), 8)
graph.plot(x=X, y=Y(13), mark=None, linestyle='black!60')
add_custom_pin(graph, X, Y(13), 13, distance='5ex')
graph.plot(x=X, y=Y(55), mark=None, linestyle='black!80')
add_custom_pin(graph, X, Y(55), 55)
graph.plot(x=X, y=Y_sqr, mark=None, linestyle='thick')

graph.set_ylimits(max=1.7)

graph.save('fourier_with_labels')
