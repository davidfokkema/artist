import numpy as np

from artist import Plot


def main():
    locations = np.genfromtxt(
        'data/SP-DIR-plot_sciencepark_cluster-detectors.txt',
        names=['x', 'y'])
    stations = np.genfromtxt(
        'data/SP-DIR-plot_sciencepark_cluster-stations.txt',
        names=['id', 'x', 'y'])

    graph = Plot()

    graph.scatter(locations['x'], locations['y'])
    graph.set_axis_equal()

    locations = ['right'] * len(stations)
    locations[0] = 'left'
    locations[5] = 'above right'
    locations = iter(locations)
    for num, x, y in stations:
        graph.add_pin_at_xy(x, y, int(num), location=next(locations),
                            use_arrow=False, style='gray,label distance=1ex')

    x = [stations['x'][u] for u in [0, 2, 5]]
    y = [stations['y'][u] for u in [0, 2, 5]]
    x.append(x[0])
    y.append(y[0])
    graph.plot(x, y, mark=None, linestyle='dashed')

    graph.add_pin_at_xy([x[0], x[1]], [y[0], y[1]], r'\SI{128}{\meter}',
                        relative_position=.4, location='below right',
                        use_arrow=False)
    graph.add_pin_at_xy([x[0], x[2]], [y[0], y[2]], r'\SI{151}{\meter}',
                        relative_position=.5, location='left',
                        use_arrow=False)
    graph.add_pin_at_xy([x[2], x[1]], [y[2], y[1]], r'\SI{122}{\meter}',
                        relative_position=.5, location='above right',
                        use_arrow=False)

    graph.set_xlabel(r"Distance [\si{\meter}]")
    graph.set_ylabel(r"Distance [\si{\meter}]")

    graph.save('sciencepark')


if __name__ == '__main__':
    main()
