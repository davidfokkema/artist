import numpy as np

from artist import Plot, MultiPlot


def main():

    x = np.random.normal(0, 50, 50000)
    y = np.random.normal(0, 15, 50000)

    ranges = ([(-100, 0), (-50, 0)],
              [(0, 100), (-50, 0)],
              [(-100, 0), (0, 50)],
              [(0, 100), (0, 50)])
    types = ('reverse_bw', 'color', 'bw', 'area')
    bitmaps = (True, True, False, False)
    subplot_idxs = [(1, 0), (1, 1), (0, 0), (0, 1)]

    plot = Plot()
    mplot = MultiPlot(2, 2, width=r'.4\linewidth')

    for idx, r, t, b in zip(subplot_idxs, ranges, types, bitmaps):
        n, xbins, ybins = np.histogram2d(x, y, bins=15, range=r)
        plot.histogram2d(n, xbins, ybins, type=t, bitmap=b)
        p = mplot.get_subplot_at(*idx)
        p.histogram2d(n, xbins, ybins, type=t, bitmap=b)

    mplot.show_yticklabels_for_all([(1, 0), (0, 1)])
    mplot.show_xticklabels_for_all([(1, 0), (0, 1)])

    plot.save('histogram2d')
    mplot.save('multi_histogram2d')


if __name__ == '__main__':
    main()
