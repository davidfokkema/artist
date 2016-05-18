from artist import Plot
import math
import numpy as npy


L = 2 * math.pi


def square(x):
    ''' Square wave of period 2*L '''
    def H(x):
        ''' Heaveside step function '''
        if x < 0.0:
            return 0.0
        if x == 0.0:
            return 0.5
        if x > 0.0:
            return 1.0
    return 2 * (H(x / L) - H(x / L - 1)) - 1


def fourier(x, N):
    ''' fourier approximation with N terms'''
    term = 0.0
    for n in range(1, N, 2):
        term += (1.0 / n) * math.sin(n * math.pi * x / L)
    return (4.0 / (math.pi)) * term


X = npy.linspace(0.0, 2 * L, num=1000)
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
