import numpy as np

from artist import GraphArtist


def main():
    locations = np.genfromtxt('data/sciencepark-locations.txt',
                              names=['x', 'y'])

    graph = GraphArtist()

    graph.plot(locations['x'], locations['y'], linestyle=None)
    graph.set_axis_equal()
    graph.save('sciencepark')


if __name__ == '__main__':
    main()
