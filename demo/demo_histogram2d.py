import numpy as np

from artist import Plot


def main():
    plot = Plot()

    x = np.random.normal(0, 50, 50000)
    y = np.random.normal(0, 15, 50000)

    ranges = ([(-100, 0), (-50, 0)],
              [(0, 100), (-50, 0)],
              [(-100, 0), (0, 50)],
              [(0, 100), (0, 50)])
    types = ('reverse_bw', 'bw', 'reverse_bw', 'bw')
    bitmaps = (True, True, False, False)

    for r, t, b in zip(ranges, types, bitmaps):
        n, xbins, ybins = np.histogram2d(x, y, bins=20, range=r)
        plot.histogram2d(n, xbins, ybins, type=t, bitmap=b)

    plot.save('histogram2d')


if __name__ == '__main__':
    main()
