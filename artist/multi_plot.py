import jinja2
import tempfile
import os
import subprocess
import shutil

from plot import BasePlotContainer, SubPlot


class MultiPlot(BasePlotContainer):
    def __init__(self, rows, columns, axis='',
                 width=r'.67\linewidth', height=None):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
                                                    'artist', 'templates'),
                                         finalize=self._convert_none)
        self.template = environment.get_template('multi_plot.tex')
        self.document_template = environment.get_template(
                                    'document_multi_plot.tex')

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
        subplotcontainer = self.get_subplotcontainer_at(row, column)
        subplotcontainer.set_empty()

    def set_empty_for_all(self, row_column_list):
        for row, column in row_column_list:
            self.set_empty(row, column)

    def set_title(self, row, column, text):
        subplot = self.get_subplot_at(row, column)
        subplot.set_title(text)

    def set_label(self, row, column, text, location='upper right',
                  style=None):
        subplot = self.get_subplot_at(row, column)
        subplot.set_label(text, location, style)

    def show_xticklabels(self, row, column):
        subplotcontainer = self.get_subplotcontainer_at(row, column)
        subplotcontainer.show_xticklabels()

    def show_xticklabels_for_all(self, row_column_list=None):
        if row_column_list is None:
            for subplotcontainer in self.subplots:
                subplotcontainer.show_xticklabels()
        else:
            for row, column in row_column_list:
                self.show_xticklabels(row, column)

    def show_yticklabels(self, row, column):
        subplotcontainer = self.get_subplotcontainer_at(row, column)
        subplotcontainer.show_yticklabels()

    def show_yticklabels_for_all(self, row_column_list=None):
        if row_column_list is None:
            for subplotcontainer in self.subplots:
                subplotcontainer.show_yticklabels()
        else:
            for row, column in row_column_list:
                self.show_yticklabels(row, column)

    def set_xticklabels_position(self, row, column, position):
        subplotcontainer = self.get_subplotcontainer_at(row, column)
        subplotcontainer.set_xticklabels_position(position)

    def set_yticklabels_position(self, row, column, position):
        subplotcontainer = self.get_subplotcontainer_at(row, column)
        subplotcontainer.set_yticklabels_position(position)

    def set_xlimits(self, row, column, min=None, max=None):
        subplot = self.get_subplot_at(row, column)
        subplot.set_xlimits(min, max)

    def set_xlimits_for_all(self, row_column_list=None, min=None, max=None):
        if row_column_list is None:
            self.limits['xmin'] = min
            self.limits['xmax'] = max
        else:
            for row, column in row_column_list:
                self.set_xlimits(row, column, min, max)

    def set_ylimits(self, row, column, min=None, max=None):
        subplot = self.get_subplot_at(row, column)
        subplot.set_ylimits(min, max)

    def set_ylimits_for_all(self, row_column_list=None, min=None, max=None):
        if row_column_list is None:
            self.limits['ymin'] = min
            self.limits['ymax'] = max
        else:
            for row, column in row_column_list:
                self.set_ylimits(row, column, min, max)

    def set_xticks(self, row, column, ticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_xticks(ticks)

    def set_xticks_for_all(self, row_column_list, ticks):
        if row_column_list is None:
            self.ticks['x'] = ticks
        else:
            for row, column in row_column_list:
                self.set_xticks(row, column, ticks)

    def set_logxticks(self, row, column, logticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_logxticks(logticks)

    def set_logxticks_for_all(self, row_column_list, logticks):
        if row_column_list is None:
            self.ticks['x'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logxticks(row, column, logticks)

    def set_yticks(self, row, column, ticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_yticks(ticks)

    def set_yticks_for_all(self, row_column_list, ticks):
        if row_column_list is None:
            self.ticks['y'] = ticks
        else:
            for row, column in row_column_list:
                self.set_yticks(row, column, ticks)

    def set_logyticks(self, row, column, logticks):
        subplot = self.get_subplot_at(row, column)
        subplot.set_logyticks(logticks)

    def set_logyticks_for_all(self, row_column_list, logticks):
        if row_column_list is None:
            self.ticks['y'] = ['1e%d' % u for u in logticks]
        else:
            for row, column in row_column_list:
                self.set_logyticks(row, column, logticks)

    def get_subplotcontainer_at(self, row, column):
        idx = row * self.columns + column
        return self.subplots[idx]

    def get_subplot_at(self, row, column):
        container = self.get_subplotcontainer_at(row, column)
        return container

    def render(self, template=None):
        if not template:
            template = self.template

        response = template.render(rows=self.rows, columns=self.columns,
                                   xmode=self.xmode, ymode=self.ymode,
                                   width=self.width, height=self.height,
                                   xlabel=self.xlabel, ylabel=self.ylabel,
                                   limits=self.limits, ticks=self.ticks,
                                   subplots=self.subplots)
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
