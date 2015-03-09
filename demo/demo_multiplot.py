import numpy as np
from numpy import pi, sin, cos, tan

import artist


def main():
    np.random.seed(1)

    graph = artist.MultiPlot(2, 3, width=r'.25\linewidth',
                             height=r'.25\linewidth')
    x = np.linspace(-pi, pi)

    subplot = graph.get_subplot_at(0, 1)
    subplot.plot(x, sin(x), mark=None)
    subplot.add_pin('$\sin(x)$', relative_position=.5)

    subplot = graph.get_subplot_at(1, 0)
    subplot.plot(x, cos(x), mark=None)
    subplot.add_pin_at_xy(1, .5, '$\cos(x)$', use_arrow=True)

    subplot = graph.get_subplot_at(1, 2)
    subplot.plot(x, tan(x), mark=None)

    x = np.random.normal(size=1000)
    n, bins = np.histogram(x, bins=20)
    subplot = graph.get_subplot_at(0, 0)
    subplot.histogram(n, bins)
    subplot.add_pin('histogram', location='left', relative_position=.5)

    x = range(5)
    lower = np.random.uniform(-2, -1, size=5)
    median = np.random.uniform(-.5, .5, size=5)
    upper = np.random.uniform(1, 2, size=5)
    subplot = graph.get_subplot_at(0, 2)
    subplot.plot(x, median, mark='*')
    subplot.shade_region(x, lower, upper)

    subplot = graph.get_subplot_at(1, 1)
    subplot.plot(range(5), np.random.normal(size=5))

    graph.show_xticklabels_for_all([(0, 0), (1, 1), (0, 2)])
    graph.show_yticklabels(0, 0)
    graph.show_yticklabels(1, 2)

    graph.set_ylabel(r"Particle density [\si{\per\square\meter}]")
    graph.set_xlabel(r"Core distance [\si{\meter}]")

    graph.set_title(0, 1, "Nice plot")

    graph.set_subplot_xlabel(0, 0, "number")
    graph.set_subplot_ylabel(1, 2, r"$\tan x$")

    graph.save('multiplot')


if __name__ == '__main__':
    main()
