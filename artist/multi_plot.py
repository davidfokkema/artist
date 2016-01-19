"""Create a plot containing multiple subplots.

Contents
--------

:class:`MultiPlot`
    Create a plot containing multiple subplots.

:class:`SubPlotContainer`
    Adds metadata to a SubPlot instance for use in a MultiPlot.

"""

from math import sqrt
import warnings

import jinja2

from .plot import BasePlotContainer, SubPlot


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
                       'ymin': None, 'ymax': None,
                       'mmin': None, 'mmax': None,
                       'smin': None, 'smax': None}
        self.ticks = {'x': [], 'y': []}
        self.colorbar = None
        self.colormap = None
        self.external_filename = None
        self.axis_options = None

        self.subplots = []
        for i in range(rows):
            for j in range(columns):
                self.subplots.append(SubPlotContainer(i, j, self.xmode,
                                                      self.ymode))

    def save_assets(self, dest_path):
        """Save plot assets alongside dest_path.

        Some plots may have assets, like bitmap files, which need to be
        saved alongside the rendered plot file.

        :param dest_path: path of the main output file.

        """
        for idx, subplot in enumerate(self.subplots):
            subplot.save_assets(dest_path, suffix='_%d' % idx)

    def set_empty(self, row, column):
        """Keep one of the subplots completely empty.

        :param row,column: specify the subplot.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_empty()

    def set_empty_for_all(self, row_column_list):
        """Keep all specified subplots completely empty.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None

        """
        for row, column in row_column_list:
            self.set_empty(row, column)

    def set_title(self, row, column, text):
        """Set a title text.

        :param row,column: specify the subplot.
        :param text: title text.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_title(text)

    def set_label(self, row, column, text, location='upper right',
                  style=None):
        """Set a label for the subplot.

        :param row,column: specify the subplot.
        :param text: the label text.
        :param location: the location of the label inside the plot.  May
            be one of 'center', 'upper right', 'lower right', 'upper
            left', 'lower left'.
        :param style: any TikZ style to style the text.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_label(text, location, style)

    def show_xticklabels(self, row, column):
        """Show the x-axis tick labels for a subplot.

        :param row,column: specify the subplot.

        """
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
        """Show the y-axis tick labels for a subplot.

        :param row,column: specify the subplot.

        """
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

        :param row,column: specify the subplot.
        :param position: 'top' or 'bottom' to specify the position of the
            tick labels.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xticklabels_position(position)

    def set_yticklabels_position(self, row, column, position):
        """Specify the position of the axis tick labels.

        This is generally only useful for multiplots containing only one
        column.  This can be used to e.g. alternatively draw the tick
        labels on the left or the right of the subplot.

        :param row,column: specify the subplot.
        :param position: 'left' or 'right' to specify the position of the
            tick labels.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_yticklabels_position(position)

    def set_xlimits(self, row, column, min=None, max=None):
        """Set x-axis limits of a subplot.

        :param row,column: specify the subplot.
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

        :param row,column: specify the subplot.
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

    def set_mlimits(self, row, column, min=None, max=None):
        """Set limits for the point meta (colormap).

        Point meta values outside this range will be clipped.

        :param min: value for start of the colormap.
        :param max: value for end of the colormap.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_mlimits(min, max)

    def set_mlimits_for_all(self, row_column_list=None, min=None, max=None):
        """Set limits for point meta (colormap) for specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param min: value for start of the colormap.
        :param max: value for end of the colormap.

        """
        if row_column_list is None:
            self.limits['mmin'] = min
            self.limits['mmax'] = max
        else:
            for row, column in row_column_list:
                self.set_mlimits(row, column, min, max)

    def set_slimits(self, row, column, min, max):
        """Set limits for the point sizes.

        :param min: point size for the lowest value.
        :param max: point size for the highest value.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_slimits(min, max)

    def set_slimits_for_all(self, row_column_list=None, min=None, max=None):
        """Set point size limits of specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param min: point size for the lowest value.
        :param max: point size for the highest value.

        """
        if min is None or max is None:
            raise Exception('Both min and max are required.')
        if row_column_list is None:
            self.limits['smin'] = sqrt(min)
            self.limits['smax'] = sqrt(max)
        else:
            for row, column in row_column_list:
                self.set_slimits(row, column, min, max)

    def set_xticks(self, row, column, ticks):
        """Manually specify the x-axis tick values.

        :param row,column: specify the subplot.
        :param ticks: list of tick values.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xticks(ticks)

    def set_xticks_for_all(self, row_column_list=None, ticks=None):
        """Manually specify the x-axis tick values.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param ticks: list of tick values.

        """
        if row_column_list is None:
            self.ticks['x'] = ticks
        else:
            for row, column in row_column_list:
                self.set_xticks(row, column, ticks)

    def set_logxticks(self, row, column, logticks):
        """Manually specify the x-axis log tick values.

        :param row,column: specify the subplot.
        :param logticks: logarithm of the locations for the ticks along the
            axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_logxticks(logticks)

    def set_logxticks_for_all(self, row_column_list=None, logticks=None):
        """Manually specify the x-axis log tick values.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param logticks: logarithm of the locations for the ticks along the
            axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        if row_column_list is None:
            self.ticks['x'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logxticks(row, column, logticks)

    def set_yticks(self, row, column, ticks):
        """Manually specify the y-axis tick values.

        :param row,column: specify the subplot.
        :param ticks: list of tick values.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_yticks(ticks)

    def set_yticks_for_all(self, row_column_list=None, ticks=None):
        """Manually specify the y-axis tick values.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param ticks: list of tick values.

        """
        if row_column_list is None:
            self.ticks['y'] = ticks
        else:
            for row, column in row_column_list:
                self.set_yticks(row, column, ticks)

    def set_logyticks(self, row, column, logticks):
        """Manually specify the y-axis log tick values.

        :param row,column: specify the subplot.
        :param logticks: logarithm of the locations for the ticks along the
            axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_logyticks(logticks)

    def set_logyticks_for_all(self, row_column_list=None, logticks=None):
        """Manually specify the y-axis log tick values.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param logticks: logarithm of the locations for the ticks along the
            axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        if row_column_list is None:
            self.ticks['y'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logyticks(row, column, logticks)

    def set_xtick_labels(self, row, column, labels):
        """Manually specify the x-axis tick labels.

        :param row,column: specify the subplot.
        :param labels: list of tick labels.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xtick_labels(labels)

    def set_xtick_labels_for_all(self, row_column_list=None, labels=None):
        """Manually specify the x-axis tick labels.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param labels: list of tick labels.

        """
        if row_column_list is None:
            for subplot in self.subplots:
                self.set_xtick_labels(subplot.row, subplot.column, labels)
        else:
            for row, column in row_column_list:
                self.set_xtick_labels(row, column, labels)

    def set_ytick_labels(self, row, column, labels):
        """Manually specify the y-axis tick labels.

        :param row,column: specify the subplot.
        :param labels: list of tick labels.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_ytick_labels(labels)

    def set_ytick_labels_for_all(self, row_column_list=None, labels=None):
        """Manually specify the x-axis tick labels.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param labels: list of tick labels.

        """
        if row_column_list is None:
            for subplot in self.subplots:
                self.set_ytick_labels(subplot.row, subplot.column, labels)
        else:
            for row, column in row_column_list:
                self.set_ytick_labels(row, column, labels)

    def get_subplot_at(self, row, column):
        """Return the subplot at row, column position.

        :param row,column: specify the subplot.

        """
        idx = row * self.columns + column
        return self.subplots[idx]

    def render(self, template=None):
        """Render the plot using a template.

        Once the plot is complete, it needs to be rendered.  Artist uses
        the Jinja2 templating engine.  The default template results in a
        LaTeX file which can be included in your document.

        :param template: a user-supplied template or None.
        :type template: string or None.
        :returns: the rendered template as string.

        """
        if not template:
            template = self.template

        response = template.render(rows=self.rows, columns=self.columns,
                                   xmode=self.xmode, ymode=self.ymode,
                                   width=self.width, height=self.height,
                                   xlabel=self.xlabel, ylabel=self.ylabel,
                                   limits=self.limits, ticks=self.ticks,
                                   colorbar=self.colorbar,
                                   colormap=self.colormap,
                                   external_filename=self.external_filename,
                                   axis_options=self.axis_options,
                                   subplots=self.subplots,
                                   plot_template=self.template)
        return response

    def set_xlabel(self, text):
        """Set a label for the x-axis.

        :param text: text of the label.

        """
        self.xlabel = text

    def set_ylabel(self, text):
        """Set a label for the y-axis.

        :param text: text of the label.

        """
        self.ylabel = text

    def set_subplot_xlabel(self, row, column, text):
        """Set a label for the x-axis of a subplot.

        :param row,column: specify the subplot.
        :param text: text of the label.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_xlabel(text)

    def set_subplot_ylabel(self, row, column, text):
        """Set a label for the y-axis of a subplot.

        :param row,column: specify the subplot.
        :param text: text of the label.

        """
        subplot = self.get_subplot_at(row, column)
        subplot.set_ylabel(text)

    def set_scalebar_for_all(self, row_column_list=None,
                             location='lower right'):
        """Show marker area scale for subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :param location: the location of the label inside the plot.  May
            be one of 'center', 'upper right', 'lower right', 'upper
            left', 'lower left'.

        """
        if row_column_list is None:
            for subplot in self.subplots:
                subplot.set_scalebar(location)
        else:
            for row, column in row_column_list:
                subplot = self.get_subplot_at(row, column)
                subplot.set_scalebar(location)

    def set_colorbar(self, label='', horizontal=False):
        """Show the colorbar, it will be attached to the last plot.

        Not for the histogram2d, only for the scatter_table.
        Global mlimits should be set for this to properly reflect the
        colormap of each subplot.

        :param label: axis label for the colorbar.
        :param horizontal: boolean, if True the colobar will be horizontal.

        """
        if self.limits['mmin'] is None or self.limits['mmax'] is None:
            warnings.warn('Set (only) global point meta limits to ensure the '
                          'colorbar is correct for all subplots.')
        self.colorbar = {'label': label,
                         'horizontal': horizontal}

    def set_colormap(self, name):
        """Choose a colormap for all subplots.

        :param name: name of the colormap to use. (e.g. hot, cool, blackwhite,
                     greenyellow). If None a coolwarm colormap is used.

        """
        self.colormap = name

    def set_axis_options(self, row, column, text):
        """Set additionnal options as plain text."""

        subplot = self.get_subplot_at(row, column)
        subplot.set_axis_options(text)

    def set_axis_options_for_all(self, row_column_list=None, text=''):
        """Set point size limits of specified subplots.

        :param row_column_list: a list containing (row, column) tuples to
            specify the subplots, or None to indicate *all* subplots.
        :type row_column_list: list or None
        :param text: axis options for the given subplots or the overall plot.

        """
        if row_column_list is None:
            self.axis_options = text
        else:
            for row, column in row_column_list:
                self.set_axis_options(row, column, text)


class SubPlotContainer(SubPlot):

    """Add metadata to a SubPlot, for inclusion in MultiPlots.

    This class adds some metadata to a subplot, including the mode of the
    plot and whether to show tick labels.  For use in MultiPlots, the row
    and column position are attributes.

    """

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
        """Set the plot to be completely empty."""

        self.empty = True

    def show_xticklabels(self):
        """Show the x-axis tick labels for this subplot."""

        self.show_xticklabel = True

    def show_yticklabels(self):
        """Show the y-axis tick labels for this subplot."""

        self.show_yticklabel = True

    def set_xticklabels_position(self, position):
        """Specify the position of the axis tick labels.

        This is generally only useful for multiplots containing only one
        row.  This can be used to e.g. alternatively draw the tick labels
        on the bottom or the top of the subplot.

        :param position: 'top' or 'bottom' to specify the position of the
            tick labels.

        """
        pgfplots_translation = {'top': 'right', 'bottom': 'left'}
        fixed_position = pgfplots_translation[position]

        self.xticklabel_pos = fixed_position

    def set_yticklabels_position(self, position):
        """Specify the position of the axis tick labels.

        This is generally only useful for multiplots containing only one
        column.  This can be used to e.g. alternatively draw the tick
        labels on the left or the right of the subplot.

        :param position: 'left' or 'right' to specify the position of the
            tick labels.

        """
        self.yticklabel_pos = position
