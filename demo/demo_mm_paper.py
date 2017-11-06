# import numpy as np

from artist import Plot


def main():
    # data series
    x = [0, 40, 60, 69, 80, 90, 100]
    y = [0, 0, 0.5, 2.96, 2, 1, .5]

    # make graph
    graph = Plot()

    # make Plot
    graph.plot(x, y, mark=None, linestyle='smooth,thick')

    # set labels and limits
    graph.set_xlabel(r"$f [\si{\mega\hertz}]$")
    graph.set_ylabel("signal strength")
    graph.set_xlimits(0, 100)
    graph.set_ylimits(0, 5)

    # save graph to file
    graph.save_as_document('mm-paper')
    graph.save_as_pdf('output')


if __name__ == '__main__':
    main()
