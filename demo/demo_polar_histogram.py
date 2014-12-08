import numpy as np

from artist import PolarPlot


def main():
    plot = PolarPlot()

    # Full range histogram
    x = np.random.uniform(0, 360, 10000)
    n, bins = np.histogram(x, bins=np.linspace(0, 360, 181))
    plot.histogram(n, bins)

    # Offset range histogram
    x = np.random.normal(400, 130, 2500)
    n, bins = np.histogram(x, bins=np.linspace(270, 630, 91))
    plot.histogram(n, bins, linestyle='blue')

    # Part range histogram
    x = np.random.uniform(90, 300, 2000)
    n, bins = np.histogram(x, bins=np.linspace(90, 300, 22))
    plot.histogram(n, bins, linestyle='red')

    plot.save('polar_histogram')


if __name__ == '__main__':
    main()
