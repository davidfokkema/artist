import numpy as np

from artist import PolarPlot


def main():
    plot = PolarPlot()
    x = np.random.uniform(0, 360, 10000)
    n, bins = np.histogram(x, bins=180)
    plot.histogram(n, bins)
    plot.save('test_histogram')


if __name__ == '__main__':
    main()
