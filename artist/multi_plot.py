"""Create a plot containing multiple subplots.

Contents
--------

:class:`MultiPlot`
    Create a plot containing multiple subplots.

:class:`SubPlotContainer`
    Adds metadata to a SubPlot instance for use in a MultiPlot.

"""

import jinja2
import tempfile
import os
import subprocess
import shutil

from plot import BasePlotContainer, SubPlot


class MultiPlot(BasePlotContainer):

    """Create a plot containing multiple subplots.

    This class creates a 2D plot containing multiple subplots.  The number
    of rows and columns can be specified and some of the subplot
    rectangles can remain empty (nothing is drawn, not even an axis
    rectangle).  Its various methods add data, annotations and options
    which is stored in class variables.  Finally, the plot can be rendered
    using the Jinja2 templating engine resulting in a LaTeX or PDF file.

    """

    def __init__(self, rows, columns, axis='',
                 width=r'.67\linewidth', height=None):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
            'artist', 'templates'), finalize=self._convert_none)
        self.template = environment.get_template('multi_plot.tex')
        self.document_template = environment.get_template(
            'document.tex')

        self.rows = rows
        self.columns = columns
        self.xmode, self.ymode = self._get_axis_modes(axis)
        self.width = width
        self.height = height
        self.xlabel = None
        self.ylabel = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None}
        self.ticks = {'x': [], 'y': []}

        self.subplots = []
        for i in range(rows):
            for j in range(columns):
                self.subplots.append(SubPlotContainer(i, j, self.xmode,
                                                      self.ymode))

    def set_empty(self, row, column):
        """Keeps one of the subplots completely empty."""

        subplot = self.get_subplot_at(row, column)
        subplot.set_empty()

    def set_empty_for_all(self, row_column_list):
        """Keeps all specified subplots completely empty."""

        for row, column in row_column_list:
            self.set_empty(row, column)

    def set_title(self, row, column, text):
        """Set a title text."""

        subplot = self.get_subplot_at(row, column)
        subplot.set_title(text)

    def set_label(self, row, column, text, location='upper right',
                  style=None):
        """Set a label for the subplot.

        :param row, column: specify the subplot.
        :param text: the label text.
        :param location: the location of the label inside the plot.  May
            be one of 'center', 'upper right', 'lower right', 'upper
            left', 'lower left'.
        :param style: any TikZ style to style the text.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_label(text, location, style)

    def show_xticklabels(self, row, column):
        """Show the x-axis tick labels for a subplot."""

        subplot = self.get_subplot_at(row, column)
        subplot.show_xticklabels()

    def show_xticklabels_for_all(self, row_column_list=None):
        """Show the x-axis tick labels for all specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None

        """
        if row_column_list is None:
            for subplot in self.subplots:
                subplot.show_xticklabels()
        else:
            for row, column in row_column_list:
                self.show_xticklabels(row, column)

    def show_yticklabels(self, row, column):
        """Show the y-axis tick labels for a subplot."""

        subplot = self.get_subplot_at(row, column)
        subplot.show_yticklabels()

    def show_yticklabels_for_all(self, row_column_list=None):
        """Show the y-axis tick labels for all specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None

        """
        if row_column_list is None:
            for subplot in self.subplots:
                subplot.show_yticklabels()
        else:
            for row, column in row_column_list:
                self.show_yticklabels(row, column)

    def set_xticklabels_position(self, row, column, position):
        """Specify the position of the axis tick labels.

        This is generally only useful for multiplots containing only one
        row.  This can be used to e.g. alternatively draw the tick labels
        on the bottom or the top of the subplot.

        :param row, column: specify the subplot.
        :param position: 'top' or 'bottom' to specify the position of the
            tick labels.

        """
        pgfplots_translation = {'top': 'right', 'bottom': 'left'}
        fixed_position = pgfplots_translation[position]

        subplot = self.get_subplot_at(row, column)
        subplot.set_xticklabels_position(fixed_position)

    def set_yticklabels_position(self, row, column, position):
        """Specify the position of the axis tick labels.

        This is generally only useful for multiplots containing only one
        column.  This can be used to e.g. alternatively draw the tick
        labels on the left or the right of the subplot.

        :param row, column: specify the subplot.
        :param position: 'left' or 'right' to specify the position of the
            tick labels.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_yticklabels_position(position)

    def set_xlimits(self, row, column, min=None, max=None):
        """Set x-axis limits of a subplot.

        :param row, column: specify the subplot.
        :param min: minimal axis value
        :param max: maximum axis value

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xlimits(min, max)

    def set_xlimits_for_all(self, row_column_list=None, min=None, max=None):
        """Set x-axis limits of specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param min: minimal axis value
        :param max: maximum axis value

        """
        if row_column_list is None:
            self.limits['xmin'] = min
            self.limits['xmax'] = max
        else:
            for row, column in row_column_list:
                self.set_xlimits(row, column, min, max)

    def set_ylimits(self, row, column, min=None, max=None):
        """Set y-axis limits of a subplot.

        :param row, column: specify the subplot.
        :param min: minimal axis value
        :param max: maximum axis value

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_ylimits(min, max)

    def set_ylimits_for_all(self, row_column_list=None, min=None, max=None):
        """Set y-axis limits of specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param min: minimal axis value
        :param max: maximum axis value

        """

        if row_column_list is None:
            self.limits['ymin'] = min
            self.limits['ymax'] = max
        else:
            for row, column in row_column_list:
                self.set_ylimits(row, column, min, max)

    def set_xticks(self, row, column, ticks):
        """Manually specify the x-axis tick values.

        :param row, column: specify the subplot.
        :param ticks: list of tick values.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xticks(ticks)

    def set_xticks_for_all(self, row_column_list=None, ticks=None):
        """Manually specify the x-axis tick values.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :param ticks: list of tick values.

        """
        if row_column_list is None:
            self.ticks['x'] = ticks
        else:
            for row, column in row_column_list:
                self.set_xticks(row, column, ticks)

    def set_logxticks(self, row, column, logticks):
        """Manually specify the x-axis log tick values.

        :param row, column: specify the subplot.
        :param logticks: list of tick . FIXME

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_logxticks(logticks)

    def set_logxticks_for_all(self, row_column_list=None, logticks=None):
        if row_column_list is None:
            self.ticks['x'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logxticks(row, column, logticks)

    def set_yticks(self, row, column, ticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_yticks(ticks)

    def set_yticks_for_all(self, row_column_list=None, ticks=None):
        if row_column_list is None:
            self.ticks['y'] = ticks
        else:
            for row, column in row_column_list:
                self.set_yticks(row, column, ticks)

    def set_logyticks(self, row, column, logticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_logyticks(logticks)

    def set_logyticks_for_all(self, row_column_list=None, logticks=None):
        if row_column_list is None:
            self.ticks['y'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logyticks(row, column, logticks)

    def get_subplot_at(self, row, column):
        idx = row * self.columns + column
        return self.subplots[idx]

    def render(self, template=None):
        if not template:
            template = self.template

        response = template.render(rows=self.rows, columns=self.columns,
                                   xmode=self.xmode, ymode=self.ymode,
                                   width=self.width, height=self.height,
                                   xlabel=self.xlabel, ylabel=self.ylabel,
                                   limits=self.limits, ticks=self.ticks,
                                   subplots=self.subplots,
                                   plot_template=self.template)
        return response

    def set_xlabel(self, text):
        self.xlabel = text

    def set_ylabel(self, text):
        self.ylabel = text

    def set_subplot_xlabel(self, row, column, text):
        subplot = self.get_subplot_at(row, column)
        subplot.set_xlabel(text)

    def set_subplot_ylabel(self, row, column, text):
        subplot = self.get_subplot_at(row, column)
        subplot.set_ylabel(text)


class SubPlotContainer(SubPlot):
    def __init__(self, row, column, xmode, ymode):
        self.row = row
        self.column = column
        self.xmode, self.ymode = xmode, ymode
        self.empty = False
        self.show_xticklabel = False
        self.show_yticklabel = False
        self.xticklabel_pos = None
        self.yticklabel_pos = None
        super(SubPlotContainer, self).__init__()

    def set_empty(self):
        self.empty = True

    def show_xticklabels(self):
        self.show_xticklabel = True

    def show_yticklabels(self):
        self.show_yticklabel = True

    def set_xticklabels_position(self, position):
        self.xticklabel_pos = position

    def set_yticklabels_position(self, position):
        self.yticklabel_pos = position
