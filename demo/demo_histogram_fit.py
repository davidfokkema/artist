import numpy as np
import scipy.optimize
import scipy.stats

from artist import Plot


def main():
    # Draw random numbers from the normal distribution
    np.random.seed(1)
    N = np.random.normal(size=2000)

    # define bin edges
    edge = 5
    bin_width = .1
    bins = np.arange(-edge, edge + .5 * bin_width, bin_width)

    # build histogram and x, y values at the center of the bins
    n, bins = np.histogram(N, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2
    y = n

    # fit normal distribution pdf to data
    f = lambda x, N, mu, sigma: N * scipy.stats.norm.pdf(x, mu, sigma)
    popt, pcov = scipy.optimize.curve_fit(f, x, y)
    print("Parameters from fit (N, mu, sigma):", popt)

    # make graph
    graph = Plot()

    # graph histogram
    graph.histogram(n, bins)

    # graph model with fit parameters
    x = np.linspace(-edge, edge, 100)
    graph.plot(x, f(x, *popt), mark=None)

    # set labels and limits
    graph.set_xlabel("value")
    graph.set_ylabel("count")
    graph.set_label("Fit to data")
    graph.set_xlimits(-6, 6)

    # save graph to file
    graph.save('histogram-fit')


if __name__ == '__main__':
    main()
