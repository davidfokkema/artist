import numpy as np

from artist import Plot


def main():
    x, t25, t50, t75 = np.loadtxt('data/DIR-boxplot_arrival_times-1.txt')

    graph = Plot()
    graph.plot(x, t50, mark='*')
    graph.shade_region(x, t25, t75)
    graph.set_xlabel(r"Core distance [\si{\meter}]")
    graph.set_ylabel(r"Arrival time delay [\si{\nano\second}]")
    graph.set_ylimits(min=0)
    graph.save('shower-front')


if __name__ == '__main__':
    main()
