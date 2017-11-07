# import numpy as np

from artist import Plot, MultiPlot


def main():
    # data series
    x = [0, 40, 60, 69, 80, 90, 100]
    y = [0, 0, 0.5, 2.96, 2, 1, .5]

    # make graph
    graph = Plot()

    # make Plot
    graph.plot(x, y, mark=None, linestyle='smooth,very thick')

    # set labels and limits
    graph.set_xlabel(r"$f [\si{\mega\hertz}]$")
    graph.set_ylabel("signal strength")
    graph.set_xlimits(0, 100)
    graph.set_ylimits(0, 5)

    # set scale: 1cm equals 10 units along the x-axis
    graph.set_xscale(cm=10)
    # set scale: 1cm equals 1 unit along the y-axis
    graph.set_yscale(cm=1)

    # set ticks at every unit along the y axis
    graph.set_yticks(range(6))

    # set graph paper
    graph.use_graph_paper()

    # save graph to file
    graph.save('mm-paper')


def multiplot():
    # data series
    x = [0, 40, 60, 69, 80, 90, 100]
    y = [0, 0, 0.5, 2.96, 2, 1, .5]

    multiplot = MultiPlot(1, 2)

    # make graph
    graph1 = multiplot.get_subplot_at(0, 0)
    graph2 = multiplot.get_subplot_at(0, 1)

    # make Plot
    graph1.plot(x, y, mark=None, linestyle='smooth,very thick')
    graph2.plot(x, y, mark=None, linestyle='smooth,very thick')

    multiplot.show_xticklabels_for_all()
    multiplot.show_yticklabels(0, 0)
    multiplot.set_xticklabels_position(0, 1, 'top')
    multiplot.set_yticks_for_all(ticks=range(6))

    graph1.set_xlimits(0, 100)
    graph2.set_xlimits(60, 80)
    multiplot.set_ylimits_for_all(min=0, max=5)

    # set scale: 1cm equals 10 or 5 units along the x-axis
    graph1.set_xscale(cm=10)
    graph2.set_xscale(cm=5)
    # set scale: 1cm equals 1 unit along the y-axis
    graph1.set_yscale(cm=1)
    graph2.set_yscale(cm=1)

    # set graph paper
    graph1.use_graph_paper()
    graph2.use_graph_paper()

    # set labels
    multiplot.set_xlabel(r"$f [\si{\mega\hertz}]$")
    multiplot.set_ylabel("signal strength")

    # save graph to file
    multiplot.save('mm-paper-multiplot')


if __name__ == '__main__':
    main()
    multiplot()
