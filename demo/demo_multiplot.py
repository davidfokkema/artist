import numpy as np
from numpy import pi, sin, cos, tan

import artist


def main():
    np.random.seed(1)

    graph = artist.MultiPlot(2, 3, width=r'.33\linewidth',
                             height=r'.33\linewidth')
    x = np.linspace(-pi, pi)
    graph.plot(0, 1, x, sin(x), mark=None)
    graph.add_pin(0, 1, '$\sin(x)$', relative_position=.5)
    graph.plot(1, 0, x, cos(x), mark=None)
    graph.add_pin_at_xy(1, 0, 1, .5, '$\cos(x)$', use_arrow=True)
    graph.plot(1, 2, x, tan(x), mark=None)

    x = np.random.normal(size=1000)
    n, bins = np.histogram(x, bins=20)
    graph.histogram(0, 0, n, bins)
    graph.add_pin(0, 0, 'histogram', location='left', relative_position=.5)

    x = range(5)
    lower = np.random.uniform(-2, -1, size=5)
    median = np.random.uniform(-.5, .5, size=5)
    upper = np.random.uniform(1, 2, size=5)
    graph.plot(0, 2, x, median, mark='*')
    graph.shade_region(0, 2, x, lower, upper)

    graph.plot(1, 1, range(5), np.random.normal(size=5))

    graph.show_xticklabels_for_all([(0, 0), (1, 1), (0, 2)])
    graph.show_yticklabels(0, 0)
    graph.show_yticklabels(1, 2)

    graph.save('multiplot')
    graph.save_as_document('preview')
    graph.save_as_pdf('preview')


if __name__ == '__main__':
    main()
