import numpy as np
from PIL import Image

from artist import Plot


def main():
    stations = np.genfromtxt('data/cluster-utrecht-stations.txt',
                             names=['x', 'y'])
    image = Image.open('data/cluster-utrecht-background.png')

    graph = Plot(width=r'.75\linewidth', height=r'.5\linewidth')

    graph.scatter(stations['x'], stations['y'])
    graph.draw_image(image)

    graph.set_axis_equal()

    nw = ['%.4f' % i for i in (52.10650519075632, 5.053710938)]
    se = ['%.4f' % i for i in (52.05249047600099, 5.185546875)]

    graph.set_xlabel('Longitude [$^\circ$]')
    graph.set_xticks([0, image.size[0]])
    graph.set_xtick_labels([nw[1], se[1]])

    graph.set_ylabel('Latitude [$^\circ$]')
    graph.set_yticks([0, image.size[1]])
    graph.set_ytick_labels([se[0], nw[0]])

    graph.save('utrecht')


if __name__ == '__main__':
    main()
