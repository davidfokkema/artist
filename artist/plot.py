"""Create a plot.

Contents
--------

:class:`BasePlotContainer`
    Base class for standalone plots.

:class:`SubPlot`
    Plot data in a data rectangle.

:class:`Plot`
    Create a plot containing a single subplot.

"""

import subprocess
import os
import tempfile
import shutil
from itertools import izip_longest

import jinja2
import numpy as np
from math import log10


RELATIVE_NODE_LOCATIONS = {'upper right': {'node_location': 'below left',
                                           'x': 1, 'y': 1},
                           'upper left': {'node_location': 'below right',
                                          'x': 0, 'y': 1},
                           'lower left': {'node_location': 'above right',
                                          'x': 0, 'y': 0},
                           'lower right': {'node_location': 'above left',
                                           'x': 1, 'y': 0},
                           'center': {'node_location': 'center',
                                      'x': 0.5, 'y': 0.5}}


class BasePlotContainer(object):

    """Base class for stand-alone plots.

    This class provides methods for rendering the plot.  To provide
    methods for plotting and annotating, subclass this base class.

    """

    # The templates must be initialized on instantiation.
    template = None
    document_template = None

    def render(self, template=None):
        """Render the plot using a template.

        Once the plot is complete, it needs to be rendered.  Artist uses
        the Jinja2 templating engine.  The default template results in a
        LaTeX file which can be included in your document.

        :param template: a user-supplied template or None.
        :type template: string or None.
        :returns: the rendered template as string.

        This is a very minimal implementation.  Override this method to
        include variables in the template.render call.

        """
        if not template:
            template = self.template

        response = template.render()
        return response

    def render_as_document(self):
        """Render the plot as a stand-alone document.

        :returns: the rendered template as string.

        """
        return self.render(self.document_template)

    def save(self, dest_path):
        r"""Save the plot as a includable LaTeX file.

        The output file can be included (using \input) in your LaTeX
        document.

        :param dest_path: path of the file.

        """
        dest_path = self._add_extension('tex', dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render())

    def save_as_document(self, dest_path):
        """Save the plot as a stand-alone LaTeX file.

        :param dest_path: path of the file.

        """
        dest_path = self._add_extension('tex', dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render_as_document())

    def save_as_pdf(self, dest_path):
        """Save the plot as a PDF file.

        Save and render the plot using LaTeX to create a PDF file.

        :param dest_path: path of the file.

        """
        dest_path = self._add_extension('pdf', dest_path)
        build_dir = tempfile.mkdtemp()
        build_path = os.path.join(build_dir, 'document.tex')
        with open(build_path, 'w') as f:
            f.write(self.render_as_document())
        pdf_path = self._build_document(build_path)
        self._crop_document(pdf_path)
        shutil.copyfile(pdf_path, dest_path)
        shutil.rmtree(build_dir)

    def _build_document(self, path):
        dir_path = os.path.dirname(path)
        try:
            subprocess.check_output(['pdflatex', '-halt-on-error',
                                     '-output-directory', dir_path, path],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            output_lines = exc.output.split('\n')
            error_lines = [line for line in output_lines if
                           line and line[0] == '!']
            errors = '\n'.join(error_lines)
            raise RuntimeError("LaTeX compilation failed:\n" + errors)

        pdf_path = path.replace('.tex', '.pdf')
        return pdf_path

    def _crop_document(self, path):
        dirname = os.path.dirname(path)
        output_path = os.path.join(dirname, 'crop-output.pdf')
        try:
            subprocess.check_output(['pdfcrop', path, output_path],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("Cropping PDF failed:\n" + exc.output)
        os.rename(output_path, path)

    def _add_extension(self, extension, path):
        if not '.' in path:
            return path + '.' + extension
        else:
            return path

    def _convert_none(self, variable):
        if variable is not None:
            return variable
        else:
            return ''

    def _get_axis_modes(self, axis):
        if axis == 'loglog':
            return 'log', 'log'
        elif axis == 'semilogx':
            return 'log', 'normal'
        elif axis == 'semilogy':
            return 'normal', 'log'
        else:
            return 'normal', 'normal'


class SubPlot(object):

    """Plot data in a data rectangle.

    Provides methods to plot or histogram data, shade regions, add labels,
    pins and titles.  This class is not meant to be used directly.
    Instead, use the Plot class for single plots, or the MultiPlot class
    for plots containing multiple subplots.

    """

    def __init__(self):
        self.shaded_regions_list = []
        self.plot_series_list = []
        self.histogram2d_list = []
        self.pin_list = []
        self.horizontal_lines = []
        self.vertical_lines = []
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.label = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None}
        self.ticks = {'x': [], 'y': []}
        self.axis_equal = False

    def plot(self, x, y, xerr=[], yerr=[], mark='o',
             linestyle='solid', use_steps=False, markstyle=None):
        """Add a data series to the plot.

        :param x: array containing x-values.
        :param y: array containing y-values.
        :param xerr: (optional) array containing errors on the x-values.
        :param yerr: (optional) array containing errors on the y-values.
        :param mark: the symbol used to mark the data point.  May be None,
            or any plot mark accepted by TikZ (e.g. *, x, +, o, square,
            triangle).
        :param linestyle: the line style used to connect the data points.
            May be None, or any line style accepted by TikZ (e.g. solid,
            dashed, dotted, thick, or even combinations like
            "red,thick,dashed").
        :param use_steps: if True, draw a stepped plot.
        :param markstyle: the style of the plot marks (e.g. 'mark
            size=.75pt')

        The dimensions of x, y, xerr and yerr should be equal.  However,
        xerr and yerr may be empty lists.

        """
        self._clear_plot_mark_background(x, y, mark)
        options = self._parse_plot_options(mark, linestyle, use_steps,
                                           markstyle)
        plot_series = self._create_plot_series_object(x, y, xerr, yerr,
                                                      options)
        self.plot_series_list.append(plot_series)

    def _clear_plot_mark_background(self, x, y, mark):
        options = self._create_mark_background_options(mark)
        if options:
            plot_series = self._create_plot_series_object(x, y,
                                                          options=options)
            # make sure all background clear operations are performed first
            self.plot_series_list.insert(0, plot_series)

    def _create_plot_series_object(self, x, y, xerr=[], yerr=[],
                                   options=None):
        return {'options': options, 'data': list(izip_longest(x, y, xerr,
                                                              yerr)),
                'show_xerr': True if len(xerr) else False,
                'show_yerr': True if len(yerr) else False}

    def histogram(self, counts, bin_edges, linestyle='solid'):
        """Plot a histogram.

        The user needs to supply the histogram.  This method only plots
        the results.  You can use NumPy's histogram function.

        :param counts: array containing the count values.
        :param bin_edges: array containing the bin edges.
        :param linestyle: the line style used to connect the data points.
            May be None, or any line style accepted by TikZ (e.g. solid,
            dashed, dotted, thick, or even combinations like
            "red,thick,dashed").

        Example::

            >>> plot = artist.Plot()
            >>> x = np.random.normal(size=1000)
            >>> n, bins = np.histogram(x)
            >>> plot.histogram(n, bins)

        """
        if len(bin_edges) - 1 != len(counts):
            raise RuntimeError(
                "The length of bin_edges should be length of counts + 1")
        x = bin_edges
        y = list(counts) + [counts[-1]]
        self.plot(x, y, mark=None, linestyle=linestyle, use_steps=True)

    def histogram2d(self, counts, x_edges, y_edges, type='bw',
                    style=None):
        """Plot a two-dimensional histogram.

        The user needs to supply the histogram.  This method only plots
        the results.  You can use NumPy's histogram2d function.

        :param counts: array containing the count values.
        :param x_edges: array containing the x-axis bin edges.
        :param y_edges: array containing the y-axis bin edges.
        :param type: the type of histogram.  Allowed values are 'bw' for
            filled squares with shades from black (minimum value) to white
            (maximum value), 'reverse_bw' for filled squares with the
            shades reversed and 'area' for squares where the area of the
            square is a measure of the count in the bin.
        :param style: optional TikZ styles to apply (e.g. 'red').  Note
            that many color styles are overridden by the 'bw' and
            'reverse_bw' types.

        """
        if counts.shape != (len(x_edges) - 1, len(y_edges) - 1):
            raise RuntimeError(
                "The length of x_edges and y_edges should match counts")

        if type not in ['bw', 'reverse_bw', 'area']:
            raise RuntimeError("Histogram type %s not supported" % type)

        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2

        self.histogram2d_list.append({'x_edges': x_edges,
                                      'y_edges': y_edges,
                                      'x_centers': x_centers,
                                      'y_centers': y_centers,
                                      'counts': counts,
                                      'max': counts.max(),
                                      'type': type,
                                      'style': style})
        self.set_xlimits(min(x_edges), max(x_edges))
        self.set_ylimits(min(y_edges), max(y_edges))

    def set_title(self, text):
        """Set a title text."""

        self.title = text

    def set_label(self, text, location='upper right', style=None):
        """Set a label for the plot.

        :param text: the label text.
        :param location: the location of the label inside the plot.  May
            be one of 'center', 'upper right', 'lower right', 'upper
            left', 'lower left'.
        :param style: any TikZ style to style the text.

        """
        if location in RELATIVE_NODE_LOCATIONS:
            label = RELATIVE_NODE_LOCATIONS[location].copy()
            label['text'] = text
            label['style'] = style
            self.label = label
        else:
            raise RuntimeError("Unknown label location: %s" % location)

    def add_pin(self, text, location='left', x=None, use_arrow=False,
                relative_position=None, style=None):
        """Add pin to most recent data series.

        :param text: the text of the pin label.
        :param location: the location of the pin relative to the data
            point.  Any location accepted by TikZ is allowed.
        :type location: string
        :param x: the x location of the data point (in the most recent
            data series) at which to place the label.  This is
            interpolated between the actual data points.  If None, only
            the relative_position parameter is used.
        :param use_arrow: specifies whether to draw an arrow between the
            data point and the pin label text.
        :type use_arrow: boolean
        :param relative_position: location of the data point as a relative
            number between 0 and 1.
        :param style: optional TikZ styles to apply (e.g. 'red').

        """
        try:
            series = self.plot_series_list[-1]
        except IndexError:
            raise RuntimeError("""
                First plot a data series, before using this function""")

        data = series['data']
        series_x, series_y = zip(*data)[:2]

        if x is not None:
            y = np.interp(x, series_x, series_y)
        else:
            x, y = series_x, series_y

        self.add_pin_at_xy(x, y, text, location, relative_position,
                           use_arrow, style)

    def add_pin_at_xy(self, x, y, text, location='above right',
                      relative_position=.9, use_arrow=True, style=None):
        """Add pin at x, y location.

        :param x: array, list or float, specifying the location of the
            pin.
        :param y: array, list or float, specifying the location of the
            pin.
        :param text: the text of the pin label.
        :param location: the location of the pin relative to the data
            point.  Any location accepted by TikZ is allowed.
        :param relative_position: location of the data point as a relative
            number between 0 and 1.
        :param use_arrow: specifies whether to draw an arrow between the
            data point and the pin label text.
        :type use_arrow: boolean
        :param style: optional TikZ styles to apply (e.g. 'red').

        If x, y are arrays or lists, relative position is used to pick a
        point from the arrays.  A relative position of 0.0 will be the
        first point from the series, while 1.0 will be the last point.

        """
        if relative_position is None:
            if location == 'left':
                relative_position = 0.
            elif location == 'right':
                relative_position = 1.
            else:
                relative_position = .8

        x, y = self._calc_position_for_pin(x, y, relative_position)
        self.pin_list.append({'x': x, 'y': y, 'text': text,
                              'location': location,
                              'use_arrow': use_arrow,
                              'options': style})

    def shade_region(self, x, lower, upper, color='lightgray'):
        """Shade a region between upper and lower bounds.

        :param x: array containing x-values
        :param lower: array containing y-values of lower bounds
        :param upper: array containing y-values of upper bounds
        :param color: TikZ style to color the region

        """
        x = list(x)
        reversed_x = list(x)
        reversed_x.reverse()

        lower = list(lower)
        upper = list(upper)
        upper.reverse()

        x = x + reversed_x
        y = lower + upper
        self.shaded_regions_list.append({'data': zip(x, y), 'color': color})

    def draw_horizontal_line(self, yvalue, linestyle=None):
        """Draw a horizontal line.

        :param yvalue: y-value of the line
        :param linestyle: TikZ linestyle (e.g. dashed, solid, red)

        """
        self.horizontal_lines.append({'value': yvalue,
                                      'options': linestyle})

    def draw_vertical_line(self, xvalue, linestyle=None):
        """Draw a vertical line.

        :param xvalue: x-value of the line
        :param linestyle: TikZ linestyle (e.g. dashed, solid, red)

        """
        self.vertical_lines.append({'value': xvalue,
                                    'options': linestyle})

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

    def set_xlimits(self, min=None, max=None):
        """Set limits for the x-axis.

        :param min: minimum value to be displayed.  If None, it will be
            calculated.
        :param max: maximum value to be displayed.  If None, it will be
            calculated.

        """
        self.limits['xmin'] = min
        self.limits['xmax'] = max

    def set_ylimits(self, min=None, max=None):
        """Set limits for the y-axis.

        :param min: minimum value to be displayed.  If None, it will be
            calculated.
        :param max: maximum value to be displayed.  If None, it will be
            calculated.

        """
        self.limits['ymin'] = min
        self.limits['ymax'] = max

    def set_xticks(self, ticks):
        """Set ticks for the x-axis.

        :param ticks: locations for the ticks along the axis.

        """
        self.ticks['x'] = ticks

    def set_logxticks(self, logticks):
        """Set ticks for the logarithmic x-axis.

        :param logticks: logarithm of the locations for the ticks along
            the axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        self.ticks['x'] = ['1e%d' % u for u in logticks]

    def set_yticks(self, ticks):
        """Set ticks for the y-axis.

        :param ticks: locations for the ticks along the axis.

        """
        self.ticks['y'] = ticks

    def set_logyticks(self, logticks):
        """Set ticks for the logarithmic y-axis.

        :param logticks: logarithm of the locations for the ticks along
            the axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        self.ticks['y'] = ['1e%d' % u for u in logticks]

    def set_axis_equal(self):
        """Scale the axes so the unit vectors have equal length."""

        self.axis_equal = True

    def _parse_plot_options(self, mark=None, linestyle=None,
                            use_steps=False, markstyle=None):
        options = []
        if mark is not None:
            options.append('mark=%s' % mark)
        else:
            options.append('no markers')

        if linestyle is not None:
            options.append(linestyle)
        else:
            options.append('only marks')

        if use_steps is True:
            options.append('const plot')

        if markstyle is not None:
            options.append('mark options={%s}' % markstyle)

        options_string = ','.join(options)
        return options_string

    def _create_mark_background_options(self, mark=None):
        options = []
        if mark is not None:
            if mark in ['o', 'square', 'triangle', 'diamond', 'pentagon']:
                if mark == 'o':
                    mark = ''
                options.append('mark=%s*,mark options=white,only marks' % mark)
        options_string = ','.join(options)
        return options_string

    def _calc_position_for_pin(self, x, y, relative_position):
        try:
            max_idx_x = len(x) - 1
            max_idx_y = len(y) - 1
        except TypeError:
            return x, y
        else:
            assert max_idx_x == max_idx_y, \
                'If x and y are iterables, they must be the same length'

            x0, x1 = x[0], x[-1]
            if self.xmode == 'log':
                xs = 10 ** (relative_position * (log10(x1) - log10(x0)) +
                            log10(x0))
            else:
                xs = relative_position * (x1 - x0) + x0
            ys = np.interp(xs, x, y)
            return xs, ys


class Plot(SubPlot, BasePlotContainer):

    """Create a plot containing a single subplot.

    This class creates a 2D plot.  Its various methods add data,
    annotations and options which is stored in class variables.  Finally,
    the plot can be rendered using the Jinja2 templating engine resulting
    in a LaTeX or PDF file.

    """

    def __init__(self, axis='', width=r'.67\linewidth', height=None):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
            'artist', 'templates'), finalize=self._convert_none)
        self.template = environment.get_template('plot.tex')
        self.document_template = environment.get_template(
            'document.tex')

        self.width = width
        self.height = height
        self.xmode, self.ymode = self._get_axis_modes(axis)

        super(Plot, self).__init__()

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

        response = template.render(
            xmode=self.xmode,
            ymode=self.ymode,
            title=self.title,
            width=self.width,
            height=self.height,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            limits=self.limits,
            ticks=self.ticks,
            axis_equal=self.axis_equal,
            plot=self,
            plot_template=self.template)
        return response
