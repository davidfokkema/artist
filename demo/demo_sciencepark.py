import numpy as np

from artist import GraphArtist


def main():
    locations = np.genfromtxt('data/sciencepark-locations.txt',
                              names=['x', 'y'])

    graph = GraphArtist(width=r'.5\linewidth', height=r'.65\linewidth')

    graph.plot(locations['x'], locations['y'], linestyle=None)
    graph.save('sciencepark')


if __name__ == '__main__':
    main()
