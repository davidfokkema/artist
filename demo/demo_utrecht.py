import numpy as np
from PIL import Image

from artist import Plot


def main():
    stations = np.genfromtxt('data/cluster-utrecht-stations.txt',
                             names=['x', 'y'])

    graph = Plot(width=r'.7\linewidth', height=r'.5\linewidth')

    image = Image.open('data/cluster-utrecht-background.png')
    graph.scatter(stations['x'], stations['y'])
    graph.draw_image(image, 0, 0, 768, 512)
    graph.set_axis_equal()

    graph.save('utrecht')


if __name__ == '__main__':
    main()
