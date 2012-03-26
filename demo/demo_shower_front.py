import numpy as np

from artist import GraphArtist


def main():
    x, t25, t50, t75 = np.loadtxt('DIR-boxplot_arrival_times-1.txt')

    graph = GraphArtist(width=r'.5\linewidth')
    graph.plot(x, t50, mark='*')
    graph.shade_region(x, t25, t75)
    graph.set_xlabel(r"Core distance [\si{\meter}]")
    graph.set_ylabel(r"Arrival time delay [\si{\nano\second}]")
    graph.set_ylimits(min=0)
    graph.save('shower-front')


if __name__ == '__main__':
    main()
