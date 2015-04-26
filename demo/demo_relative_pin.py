from numpy import linspace, pi, sin, cos

from artist import Plot


def main():
    plot = Plot(width=r'.5\linewidth', height=r'.5\linewidth')
    r = linspace(1, 5, 100)
    phi = linspace(0, 4.5 * pi, 100)
    x = r * cos(phi)
    y = r * sin(phi)
    plot.plot(x, y, mark=None)
    plot.add_pin('start', relative_position=0, use_arrow=True)
    plot.add_pin('half', relative_position=.5, use_arrow=True)
    plot.add_pin('46\%', relative_position=.46, use_arrow=True,
                 location='above')
    plot.add_pin('end', relative_position=1, use_arrow=True, location='below')

    phi = linspace(0, 2 * pi, 10)
    x = 6 * cos(phi)
    y = 6 * sin(phi)
    plot.plot(x, y, mark=None, linestyle='thick, gray')
    plot.add_pin('start', relative_position=0, use_arrow=True,
                 location='above right')
    plot.add_pin('half', relative_position=.5, use_arrow=True,
                 location='above left')
    plot.add_pin('70\%', relative_position=.7, use_arrow=True,
                 location='below')
    plot.add_pin('end', relative_position=1, use_arrow=True,
                 location='below right')

    plot.plot([-5, 2, 5], [-7.5, -7.5, -7.5], linestyle='lightgray')
    plot.add_pin('50\%', relative_position=.5, use_arrow=True,
                 location='above right')

    plot.set_xlimits(-8, 8)
    plot.set_ylimits(-8, 8)
    plot.save('relative_pin')

    # With one logarithmic axis
    plot = Plot(axis='semilogy')

    x = [2, 2, 2]
    y = [1, 10, 100]
    plot.plot(x, y)
    for xi, yi in zip(x, y):
        plot.add_pin_at_xy(xi, yi, '(%d,%d)' % (xi, yi),
                           location='below right')
    plot.add_pin('half', relative_position=.5, use_arrow=True,
                 location='right')

    x = [4, 5, 6]
    y = [3, 3, 3]
    plot.plot(x, y)
    for xi, yi in zip(x, y):
        plot.add_pin_at_xy(xi, yi, '(%d,%d)' % (xi, yi), location='below')
    plot.add_pin('half', relative_position=.5, use_arrow=True,
                 location='above')

    x = [3, 4, 5]
    y = [1, 10, 100]
    plot.plot(x, y)
    for xi, yi in zip(x, y):
        plot.add_pin_at_xy(xi, yi, '(%d,%d)' % (xi, yi), location='above left')
    plot.add_pin('half', relative_position=.5, use_arrow=True,
                 location='right')

    plot.save('relative_pin_log')


if __name__ == "__main__":
    main()
