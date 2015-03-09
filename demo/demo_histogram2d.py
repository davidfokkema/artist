import numpy as np

from artist import Plot, MultiPlot


def main():

    x = np.random.normal(0, 50, 50000)
    y = np.random.normal(0, 15, 50000)

    ranges = ([(-100, 0), (-50, 0)],
              [(0, 100), (-50, 0)],
              [(-100, 0), (0, 50)],
              [(0, 100), (0, 50)])
    types = ('reverse_bw', 'bw', 'reverse_bw', 'bw')
    bitmaps = (True, True, False, False)

    plot = Plot()
    for r, t, b in zip(ranges, types, bitmaps):
        n, xbins, ybins = np.histogram2d(x, y, bins=15, range=r)
        plot.histogram2d(n, xbins, ybins, type=t, bitmap=b)

    plot.save('histogram2d')

    plot = MultiPlot(2, 2, width=r'.4\linewidth')
    subplot_idxs = [(1, 0), (1, 1), (0, 0), (0, 1)]
    for idx, r, t, b in zip(subplot_idxs, ranges, types, bitmaps):
        p = plot.get_subplot_at(*idx)
        n, xbins, ybins = np.histogram2d(x, y, bins=15, range=r)
        p.histogram2d(n, xbins, ybins, type=t, bitmap=b)
    plot.show_yticklabels_for_all([(1, 0), (0, 1)])
    plot.show_xticklabels_for_all([(1, 0), (0, 1)])

    plot.save('multi_histogram2d')


if __name__ == '__main__':
    main()
