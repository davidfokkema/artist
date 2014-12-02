import numpy as np

from artist import PolarPlot


def main():

    directions = np.genfromtxt('data/discrete-directions.txt',
                               names=['azimuth', 'zenith'])

    plot = PolarPlot(use_radians=True)
    plot.scatter(directions['azimuth'], directions['zenith'],
                 markstyle='mark size=.75pt')

    plot.set_xlabel('Azimuth [rad]')
    plot.set_ylabel('Zenith [rad]')

    plot.save('discrete_directions')


if __name__ == '__main__':
    main()
