import numpy as np

from artist import Plot


def main():
    plot = Plot()

    x0 = np.random.uniform(0, 50, 50000)
    x1 = x0 + 50
    y = np.random.normal(400, 150, 50000)

    for x, b in [(x0, True), (x1, False)]:
        n, xbins, ybins = np.histogram2d(x, y, bins=50)
        plot.histogram2d(n, xbins, ybins, type='reverse_bw', bitmap=b)

    plot.save_as_document('histogram2d')
    plot.save_as_pdf('histogram2d')


if __name__ == '__main__':
    main()
