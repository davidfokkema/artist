"""Create a plot.

Contents
--------

:class:`BasePlotContainer`
    Base class for standalone plots.

:class:`SubPlot`
    Plot data in a data rectangle.

:class:`Plot`
    Create a plot containing a single subplot.

:class:`PolarPlot`
    Create a plot containing a single polar subplot.

"""

import subprocess
import os
import tempfile
import shutil
import warnings
from math import sqrt, modf
try:
    # Python 2
    from itertools import izip_longest
except ImportError:
    # Python 3
    from itertools import zip_longest as izip_longest

from PIL import Image
import jinja2
import numpy as np

from .colormap import COOLWARM, VIRIDIS


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

    def save_assets(self, dest_path):
        """Save plot assets alongside dest_path.

        Some plots may have assets, like bitmap files, which need to be
        saved alongside the rendered plot file.

        :param dest_path: path of the main output file.

        """
        pass

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
        self.save_assets(dest_path)
        self.external_filename = 'externalized-%s' % \
                                 os.path.basename(dest_path).replace(' ', '_')
        dest_path = self._add_extension('tex', dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render())

    def save_as_document(self, dest_path):
        """Save the plot as a stand-alone LaTeX file.

        :param dest_path: path of the file.

        """
        self.save_assets(dest_path)
        self.external_filename = 'externalized-%s' % \
                                 os.path.basename(dest_path).replace(' ', '_')
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
        self.save_assets(build_path)
        with open(build_path, 'w') as f:
            f.write(self.render_as_document())
        pdf_path = self._build_document(build_path)
        self._crop_document(pdf_path)
        shutil.copyfile(pdf_path, dest_path)
        shutil.rmtree(build_dir)

    def _build_document(self, path):
        dir_path = os.path.dirname(path)

        cwd = os.getcwd()
        os.chdir(dir_path)

        try:
            subprocess.check_output(['pdflatex', '-halt-on-error', path],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            output_lines = exc.output.split('\n')
            error_lines = [line for line in output_lines
                           if line and line[0] == '!']
            errors = '\n'.join(error_lines)
            raise RuntimeError('LaTeX compilation failed:\n' + errors +
                               '\nTemp build dir: ' + dir_path)
        finally:
            os.chdir(cwd)

        pdf_path = path.replace('.tex', '.pdf')
        return pdf_path

    def _crop_document(self, path):
        dirname = os.path.dirname(path)
        uncropped_path = os.path.join(dirname, 'uncropped-output.pdf')
        os.rename(path, uncropped_path)
        try:
            subprocess.check_output(['pdfcrop', uncropped_path, path],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError('Cropping PDF failed:\n' + exc.output)

    def _add_extension(self, extension, path):
        root, ext = os.path.splitext(path)
        if not ext:
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

    Provides methods to plot or histogram data, shade regions, add
    labels, pins and titles.  This class is not meant to be used
    directly. Instead, use the Plot class for single plots, or the
    MultiPlot class for plots containing multiple subplots.

    """

    def __init__(self):
        self.shaded_regions_list = []
        self.plot_series_list = []
        self.plot_table_list = []
        self.histogram2d_list = []
        self.bitmap_list = []
        self.pin_list = []
        self.horizontal_lines = []
        self.vertical_lines = []
        self.axis_background = None
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.label = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None,
                       'mmin': None, 'mmax': None,
                       'smin': None, 'smax': None}
        self.xscale = None
        self.yscale = None
        self.ticks = {'x': [], 'y': [],
                      'xlabels': '', 'ylabels': '',
                      'xsuffix': '', 'ysuffix': ''}
        self.axis_equal = False
        self.scalebar = None
        self.colorbar = False
        self.colormap = None
        self.axis_options = None
        self.has_graph_paper = False

    def save_assets(self, dest_path, suffix=''):
        """Save plot assets alongside dest_path.

        Some plots may have assets, like bitmap files, which need to be
        saved alongside the rendered plot file.

        :param dest_path: path of the main output file.
        :param suffix: optional suffix to add to asset names.

        """
        self._write_bitmaps(dest_path, suffix)

    def plot(self, x, y, xerr=[], yerr=[], mark='o',
             linestyle='solid', use_steps=False, markstyle=None, legend=None):
        """Add a data series to the plot.

        :param x: array containing x-values.
        :param y: array containing y-values.
        :param xerr: (optional) array containing errors on the x-values.
        :param yerr: (optional) array containing errors on the y-values.
        :param mark: the symbol used to mark the data point.  May be None,
            or any plot mark accepted by TikZ (e.g. ``*, x, +, o, square,
            triangle``).
        :param linestyle: the line style used to connect the data points.
            May be None, or any line style accepted by TikZ (e.g. solid,
            dashed, dotted, thick, or even combinations like
            "red,thick,dashed").
        :param use_steps: if True, draw a stepped plot.
        :param markstyle: the style of the plot marks (e.g. 'mark
            size=.75pt')

        The dimensions of x, y, xerr and yerr should be equal.  However,
        xerr and yerr may be empty lists.  Each element in xerr and yerr
        may be a single value for symmetric error bars, or a tuple of
        two values for assymetric errors.

        """
        if len(x) != len(y):
            raise RuntimeError(
                'The length of the x and y coordinates should be equal')
        if (len(xerr) and len(xerr) != len(x) or
                len(yerr) and len(yerr) != len(y)):
            raise RuntimeError(
                'The length of the errors and coordinates should be equal')

        # clear the background of the marks
        self._clear_plot_mark_background(x, y, mark, markstyle)
        # draw the plot series over the background
        options = self._parse_plot_options(mark, linestyle, use_steps,
                                           markstyle)
        plot_series = self._create_plot_series_object(x, y, xerr, yerr,
                                                      options, legend)
        self.plot_series_list.append(plot_series)

    def _clear_plot_mark_background(self, x, y, mark, markstyle):
        options = self._create_mark_background_options(mark, markstyle)
        if options:
            plot_series = self._create_plot_series_object(x, y,
                                                          options=options)
            # make sure all background clear operations are performed first
            self.plot_series_list.insert(0, plot_series)

    def _create_plot_series_object(self, x, y, xerr=[], yerr=[], options=None,
                                   legend=None):
        return {'options': options,
                'data': list(izip_longest(x, y, xerr, yerr)),
                'show_xerr': True if len(xerr) else False,
                'show_yerr': True if len(yerr) else False,
                'legend': legend}

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
                'The length of bin_edges should be length of counts + 1')
        x = bin_edges
        y = list(counts) + [counts[-1]]
        self.plot(x, y, mark=None, linestyle=linestyle, use_steps=True)

    def histogram2d(self, counts, x_edges, y_edges, type='bw', style=None,
                    bitmap=False, colormap=None):
        """Plot a two-dimensional histogram.

        The user needs to supply the histogram.  This method only plots
        the results.  You can use NumPy's histogram2d function.

        :param counts: array containing the count values.
        :param x_edges: array containing the x-axis bin edges.
        :param y_edges: array containing the y-axis bin edges.
        :param type: the type of histogram.  Allowed values are 'bw' for
            filled squares with shades from black (minimum value) to white
            (maximum value), 'reverse_bw' for filled squares with the
            shades reversed and, 'color' for color mapped histogram
            which uses the 'coolwarm' colormap by default, but can be
            overwritten with the colormap keyword, and 'area' for
            squares where the area of the square is a measure of the
            count in the bin.
        :param style: optional TikZ styles to apply (e.g. 'red').  Note
            that many color styles are overridden by the 'bw' and
            'reverse_bw' types.
        :param bitmap: Export the histogram as an image for better
            performance. This does expect all bins along an axis to have
            equal width. Can not be used in combination with type 'area'.
        :param colormap: A colormap for the 'color' type, as expected by
            the `Image.putpalette` method.

        Example::

            >>> x = np.random.uniform(low=1, high=1000, size=2000)
            >>> y = np.random.uniform(low=0, high=50, size=2000)
            >>> plot = artist.Plot()
            >>> n, xbins, ybins = np.histogram2d(x, y)
            >>> plot.histogram2d(n, xbins, ybins)

        When you desire logarithmic axes and bitmap is set to True special
        care has to be taken with the binning. This is because the bins along
        an axis have to be equal size in the final result. So use logarithmic
        binning for logarithmic axes.

        Example::

            >>> plot = artist.Plot(axis='semilogx')
            >>> xbins = np.logspace(0, 3, 20)
            >>> ybins = np.linspace(-5, 10, 10)
            >>> n, xbins, ybins = np.histogram2d(x, y, bins=[xbins, ybins])
            >>> plot.histogram2d(n, xbins, ybins, bitmap=True)

        For each bin where the counts are nan the value will be set to the
        minimum value (i.e. `np.nanmin(counts)`).

        """
        if counts.shape != (len(x_edges) - 1, len(y_edges) - 1):
            raise RuntimeError(
                'The length of x_edges and y_edges should match counts')

        if type not in ['bw', 'reverse_bw', 'area', 'color']:
            raise RuntimeError('Histogram type %s not supported' % type)
        if type == 'area' and bitmap:
            raise RuntimeError('Histogram type %s not supported for bitmap '
                               'output' % type)
        if type == 'color' and not bitmap:
            raise RuntimeError('Histogram type %s not supported for '
                               'non-bitmapped output' % type)

        if bitmap:
            normed_counts = self._normalize_histogram2d(counts, type)
            img = Image.fromarray(np.flipud(normed_counts.T))
            if type == 'color':
                if colormap == 'viridis':
                    img.putpalette(VIRIDIS)
                elif colormap in [None, 'coolwarm']:
                    img.putpalette(COOLWARM)
                else:
                    img.putpalette(colormap)
            self.bitmap_list.append({'image': img,
                                     'xmin': min(x_edges),
                                     'xmax': max(x_edges),
                                     'ymin': min(y_edges),
                                     'ymax': max(y_edges)})
        else:
            x_centers = (x_edges[:-1] + x_edges[1:]) / 2
            y_centers = (y_edges[:-1] + y_edges[1:]) / 2

            self.histogram2d_list.append({'x_edges': x_edges,
                                          'y_edges': y_edges,
                                          'x_centers': x_centers,
                                          'y_centers': y_centers,
                                          'counts': counts,
                                          'max': np.nanmax(counts),
                                          'min': np.nanmin(counts),
                                          'type': type,
                                          'style': style})
        # Set limits unless lower/higher limits are already set.
        xmin = min(x for x in (min(x_edges), self.limits['xmin'])
                   if x is not None)
        ymin = min(y for y in (min(y_edges), self.limits['ymin'])
                   if y is not None)
        xmax = max(x for x in (max(x_edges), self.limits['xmax'])
                   if x is not None)
        ymax = max(y for y in (max(y_edges), self.limits['ymax'])
                   if y is not None)
        self.set_xlimits(xmin, xmax)
        self.set_ylimits(ymin, ymax)
        if type != 'area':
            self.set_mlimits(np.nanmin(counts), np.nanmax(counts))
        if type == 'bw':
            self.set_colormap('blackwhite')
        elif type == 'reverse_bw':
            self.set_colormap('whiteblack')
        elif type == 'color':
            if colormap == 'viridis':
                self.set_colormap('viridis')
            elif colormap in [None, 'coolwarm']:
                self.set_colormap('coolwarm')

    def scatter(self, x, y, xerr=[], yerr=[], mark='o', markstyle=None):
        """Plot a series of points.

        Plot a series of points (marks) that are not connected by a
        line. Shortcut for plot with linestyle=None.

        :param x: array containing x-values.
        :param y: array containing y-values.
        :param xerr: array containing errors on the x-values.
        :param yerr: array containing errors on the y-values.
        :param mark: the symbol used to mark the data points. May be
            any plot mark accepted by TikZ (e.g. ``*, x, +, o, square,
            triangle``).
        :param markstyle: the style of the plot marks (e.g. 'mark
            size=.75pt')

        Example::

            >>> plot = artist.Plot()
            >>> x = np.random.normal(size=20)
            >>> y = np.random.normal(size=20)
            >>> plot.scatter(x, y, mark='*')

        """
        self.plot(x, y, xerr=xerr, yerr=yerr, mark=mark, linestyle=None,
                  markstyle=markstyle)

    def scatter_table(self, x, y, c, s, mark='*'):
        """Add a data series to the plot.

        :param x: array containing x-values.
        :param y: array containing y-values.
        :param c: array containing values for the color of the mark.
        :param s: array containing values for the size of the mark.
        :param mark: the symbol used to mark the data point.  May be None,
            or any plot mark accepted by TikZ (e.g. ``*, x, +, o, square,
            triangle``).

        The dimensions of x, y, c and s should be equal. The c values will
        be mapped to a colormap.

        """
        # clear the background of the marks
        # self._clear_plot_mark_background(x, y, mark, markstyle)
        # draw the plot series over the background
        options = self._parse_plot_options(mark)
        s = [sqrt(si) for si in s]
        plot_series = self._create_plot_tables_object(x, y, c, s, options)
        self.plot_table_list.append(plot_series)

    def _create_plot_tables_object(self, x, y, c, s, options=None):
        return {'options': options,
                'data': list(izip_longest(x, y, c, s)),
                'smin': min(s),
                'smax': max(s)}

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
            raise RuntimeError('Unknown label location: %s' % location)

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
            raise RuntimeError(
                'First plot a data series, before using this function')

        data = series['data']
        series_x, series_y = list(zip(*data))[:2]

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

    def draw_image(self, image, xmin=0, ymin=0, xmax=None, ymax=None):
        """Draw an image.

        Do not forget to use :meth:`set_axis_equal` to preserve the
        aspect ratio of the image, or change the aspect ratio of the
        plot to the aspect ratio of the image.

        :param image: Pillow Image object.
        :param xmin,ymin,xmax,ymax: the x, y image bounds.

        Example::

            >>> from PIL import Image
            >>> image = Image.open('background.png')
            >>> height_ratio = (.67 * image.size[1]) / image.size[0]
            >>> plot = artist.Plot(height=r'%.2f\linewidth' % height_ratio)
            >>> plot.draw_image(image)

        """
        if xmax is None:
            xmax = xmin + image.size[0]
        if ymax is None:
            ymax = ymin + image.size[1]
        self.bitmap_list.append({'image': image,
                                 'xmin': xmin,
                                 'xmax': xmax,
                                 'ymin': ymin,
                                 'ymax': ymax})
        # Set limits unless lower/higher limits are already set.
        xmin = min(x for x in (xmin, self.limits['xmin'])
                   if x is not None)
        ymin = min(y for y in (ymin, self.limits['ymin'])
                   if y is not None)
        xmax = max(x for x in (xmax, self.limits['xmax'])
                   if x is not None)
        ymax = max(y for y in (ymax, self.limits['ymax'])
                   if y is not None)
        self.set_xlimits(xmin, xmax)
        self.set_ylimits(ymin, ymax)

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

    def set_axis_background(self, color='white'):
        """Set a fill color for the axis background.

        :param color: TikZ style to color the axis background.

        """
        self.axis_background = 'fill=%s' % color

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

    def set_xscale(self, cm):
        """Set scale of the x-axis.

        :param cm: number of units which equals to 1 cm.

        You can set the absolute scale of units along the x-axis using this
        method. If you specify cm=10, then 1 cm along the axis will equal to 10
        units.  You can use this, for example, to match up graph paper to the
        axis, and make sure that a ruler can easily be used to read your graph.

        """
        self.xscale = cm

    def set_yscale(self, cm):
        """Set scale of the y-axis.

        :param cm: number of units which equals to 1 cm.

        You can set the absolute scale of units along the y-axis using this
        method. If you specify cm=10, then 1 cm along the axis will equal to 10
        units.  You can use this, for example, to match up graph paper to the
        axis, and make sure that a ruler can easily be used to read your graph.

        """
        self.yscale = cm

    def set_mlimits(self, min=None, max=None):
        """Set limits for the point meta (colormap).

        Point meta values outside this range will be clipped.

        :param min: value corresponding to the start of the colormap.
            If None, it will be calculated.
        :param max: value corresponding to the end of the colormap.
            If None, it will be calculated.

        """
        self.limits['mmin'] = min
        self.limits['mmax'] = max

    def set_slimits(self, min, max):
        """Set limits for the size of points in :meth:`scatter_table`.

        If both are None, the size will be the given values.

        :param min: point size for the lowest value.
        :param max: point size for the highest value.

        """
        self.limits['smin'] = sqrt(min)
        self.limits['smax'] = sqrt(max)

    def set_xticks(self, ticks):
        """Set ticks for the x-axis.

        :param ticks: locations for the ticks along the axis.

        """
        self.ticks['x'] = ticks

    def set_yticks(self, ticks):
        """Set ticks for the y-axis.

        :param ticks: locations for the ticks along the axis.

        """
        self.ticks['y'] = ticks

    def set_logxticks(self, logticks):
        """Set ticks for the logarithmic x-axis.

        :param logticks: logarithm of the locations for the ticks along
            the axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        self.ticks['x'] = ['1e%d' % u for u in logticks]

    def set_logyticks(self, logticks):
        """Set ticks for the logarithmic y-axis.

        :param logticks: logarithm of the locations for the ticks along
            the axis.

        For example, if you specify [1, 2, 3], ticks will be placed at 10,
        100 and 1000.

        """
        self.ticks['y'] = ['1e%d' % u for u in logticks]

    def set_xtick_labels(self, labels, style=None):
        """Set tick labels for the x-axis.

        Also set the x-ticks positions to ensure the labels end up on
        the correct place.

        :param labels: list of labels for the ticks along the axis.

        """
        self.ticks['xlabels'] = labels
        self.ticks['xlabel_style'] = style

    def set_ytick_labels(self, labels, style=None):
        """Set tick labels for the y-axis.

        Also set the y-ticks positions to ensure the labels end up on
        the correct place.

        :param labels: list of labels for the ticks along the axis.

        """
        self.ticks['ylabels'] = labels
        self.ticks['ylabel_style'] = style

    def set_xtick_suffix(self, suffix):
        """Set the suffix for the ticks of the x-axis.

        :param suffix: string added after each tick. If the value is
                       `degree` or `precent` the corresponding symbols
                       will be added.

        """
        if suffix == 'degree':
            suffix = '^\circ'
        elif suffix == 'percent':
            suffix = '\%'

        self.ticks['xsuffix'] = suffix

    def set_ytick_suffix(self, suffix):
        """Set ticks for the y-axis.

        :param suffix: string added after each tick. If the value is
                       `degree` or `precent` the corresponding symbols
                       will be added.

        """
        if suffix == 'degree':
            suffix = '^\circ'
        elif suffix == 'percent':
            suffix = '\%'

        self.ticks['ysuffix'] = suffix

    def set_axis_equal(self):
        """Scale the axes so the unit vectors have equal length."""

        self.axis_equal = True

    def set_scalebar(self, location='lower right'):
        """Show marker area scale.

        :param location: the location of the label inside the plot.  May
            be one of 'center', 'upper right', 'lower right', 'upper
            left', 'lower left'.

        """
        if location in RELATIVE_NODE_LOCATIONS:
            scalebar = RELATIVE_NODE_LOCATIONS[location].copy()
            self.scalebar = scalebar
        else:
            raise RuntimeError('Unknown scalebar location: %s' % location)

    def set_colorbar(self, label='', horizontal=False):
        """Show the colorbar.

        This can be used for both histogram2d and scatter_table. If a custom
        colomap is used for histogram2d (i.e. not grayscale, coolwarm, or
        viridis) a matching colormap must be available in PGFPlots or added
        using set_axis_options.

        :param label: axis label for the colorbar.
        :param horizontal: boolean, if True the colobar will be horizontal.

        """
        self.colorbar = {'label': label,
                         'horizontal': horizontal}

    def set_colormap(self, name):
        """Choose a colormap for :meth:`scatter_table`.

        :param name: name of the colormap to use. (e.g. hot, cool, blackwhite,
                     greenyellow). If None a coolwarm colormap is used.

        """
        self.colormap = name

    def set_axis_options(self, text):
        """Set additionnal options as plain text."""

        self.axis_options = text

    def use_graph_paper(self):
        """Draw millimeter graph paper."""

        self.has_graph_paper = True

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

    def _create_mark_background_options(self, mark=None, markstyle=None):
        options = []
        if mark is not None:
            if mark in ['o', 'square', 'triangle', 'diamond', 'pentagon']:
                if mark == 'o':
                    mark = ''
                options.append('mark=%s*,mark options=white,only marks' % mark)
                if markstyle:
                    options.append(',%s' % markstyle)
        options_string = ','.join(options)
        return options_string

    def _calc_position_for_pin(self, x, y, relative_position):
        """Determine position at fraction of x, y path.

        :param x,y: two equal length lists of values describing a path.
        :param relative_position: value between 0 and 1
        :returns: the x, y position of the fraction (relative_position)
                  of the path length.

        """
        try:
            max_idx_x = len(x) - 1
            max_idx_y = len(y) - 1
        except TypeError:
            return x, y
        else:
            assert max_idx_x == max_idx_y, \
                'If x and y are iterables, they must be the same length'

        if relative_position == 0:
            xs, ys = x[0], y[0]
        elif relative_position == 1:
            xs, ys = x[max_idx_x], y[max_idx_y]
        else:
            if self.xmode == 'log':
                x = np.log10(np.array(x))
            if self.ymode == 'log':
                y = np.log10(np.array(y))
            rel_length = [0]
            rel_length.extend(self._calc_relative_path_lengths(x, y))
            idx = np.interp(relative_position, rel_length,
                            range(len(rel_length)))
            frac, idx = modf(idx)
            idx = int(idx)
            if self.xmode == 'log':
                xs = 10 ** (x[idx] + (x[idx + 1] - x[idx]) * frac)
            else:
                xs = x[idx] + (x[idx + 1] - x[idx]) * frac
            if self.ymode == 'log':
                ys = 10 ** (y[idx] + (y[idx + 1] - y[idx]) * frac)
            else:
                ys = y[idx] + (y[idx + 1] - y[idx]) * frac
        return xs, ys

    def _calc_relative_path_lengths(self, x, y):
        """Determine the relative path length at each x,y position."""

        path_lengths = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2)
        total_length = np.sum(path_lengths)
        cummulative_lengths = np.cumsum(path_lengths)
        relative_path_lengths = cummulative_lengths / total_length
        return relative_path_lengths

    def _normalize_histogram2d(self, counts, type):
        """Normalize the values of the counts for a 2D histogram.

        This normalizes the values of a numpy array to the range 0-255.

        :param counts: a NumPy array which is to be rescaled.
        :param type: either 'bw' or 'reverse_bw'.

        """
        counts = (255 * (counts - np.nanmin(counts)) /
                  (np.nanmax(counts) - np.nanmin(counts)))

        if type == 'reverse_bw':
            counts = 255 - counts

        return counts.astype(np.uint8)

    def _write_bitmaps(self, path, suffix=''):
        """Write bitmap file assets.

        :param path: path of the plot file.
        :param suffix: optional suffix to add to asset names.

        The path parameter is used for the dirname, and the filename.
        So if :meth:`save` is called with '/foo/myplot.tex', you can call
        this method with that same path. The assets will then be saved in
        the /foo directory, and have a name like 'myplot_0.png'.

        """
        dir, prefix = os.path.split(path)
        if '.' in prefix:
            prefix = prefix.split('.')[0]
        if prefix == '':
            prefix = 'figure'
        for i, bitmap in enumerate(self.bitmap_list):
            name = '%s%s_%d.png' % (prefix, suffix, i)
            bitmap['name'] = name
            img = bitmap['image']
            # Make the bitmap at least 1000x1000 pixels
            size0 = int(np.ceil(1000. / img.size[0]) * img.size[0])
            size1 = int(np.ceil(1000. / img.size[1]) * img.size[1])
            large_img = img.resize((size0, size1))
            large_img.save(os.path.join(dir, name))


class Plot(SubPlot, BasePlotContainer):

    """Create a plot containing a single subplot.

    This class creates a 2D plot.  Its various methods add data,
    annotations and options which is stored in class variables. Finally,
    the plot can be rendered using the Jinja2 templating engine
    resulting in a LaTeX or PDF file.

    """

    def __init__(self, axis='', width=r'.67\linewidth', height=None):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
            'artist', 'templates'), finalize=self._convert_none)
        self.template = environment.get_template('plot.tex')
        self.document_template = environment.get_template('document.tex')

        self.width = width
        self.height = height
        self.xmode, self.ymode = self._get_axis_modes(axis)
        self.external_filename = None

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
            axis_background=self.axis_background,
            xmode=self.xmode,
            ymode=self.ymode,
            title=self.title,
            width=self.width,
            height=self.height,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            limits=self.limits,
            xscale=self.xscale,
            yscale=self.yscale,
            ticks=self.ticks,
            axis_equal=self.axis_equal,
            scalebar=self.scalebar,
            colorbar=self.colorbar,
            colormap=self.colormap,
            external_filename=self.external_filename,
            axis_options=self.axis_options,
            has_graph_paper=self.has_graph_paper,
            plot=self,
            plot_template=self.template)
        return response


class PolarPlot(Plot):

    """Create a plot containing a single polar subplot.

    Same as the Plot but uses polar axes. The x values are the phi
    coordinates in degrees (or radians). The y values are the r
    coordinates in arbitrary units.

    :param use_radians: If this keyword is set to True the units for x (phi)
        values and x (phi) axis labels are radians.

    """

    def __init__(self, *args, **kwargs):
        self.use_radians = kwargs.pop('use_radians', False)
        super(PolarPlot, self).__init__(*args, **kwargs)
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
            'artist', 'templates'), finalize=self._convert_none)
        self.template = environment.get_template('polar_plot.tex')

        if not self.use_radians:
            self.set_xtick_suffix('degree')
        else:
            self.set_xticks([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300,
                             330])
            self.set_xtick_labels([r'$0$', r'$\frac{1}{6}\pi$',
                                   r'$\frac{2}{6}\pi$', r'$\frac{1}{2}\pi$',
                                   r'$\frac{4}{6}\pi$', r'$\frac{5}{6}\pi$',
                                   r'$\pm\pi$', r'$-\frac{5}{6}\pi$',
                                   r'$-\frac{4}{6}\pi$', r'$-\frac{1}{2}\pi$',
                                   r'$-\frac{2}{6}\pi$', r'$-\frac{1}{6}\pi$'])

    def plot(self, phi, r, **kwargs):
        """Add a data series to the plot.

        :param phi: array containing phi-values, should be in degrees
                    (or radians).
        :param r: array containing r-values.

        For further options see the plot function of the super class.

        """
        if self.use_radians:
            phi = np.degrees(phi)
        super(PolarPlot, self).plot(phi, r, **kwargs)

    def histogram(self, counts, bin_edges, linestyle='solid'):
        """Plot a polar histogram.

        The user needs to supply the histogram.  This method only plots
        the results.  You can use NumPy's histogram function.

        :param counts: array containing the count values.
        :param bin_edges: array containing the bin edges in degrees
                          (or radians).
        :param linestyle: the line style used to connect the data points.
            May be None, or any line style accepted by TikZ (e.g. solid,
            dashed, dotted, thick, or even combinations like
            "red,thick,dashed").

        Example::

            >>> plot = artist.PolarPlot()
            >>> x = np.random.uniform(0, 360, size=1000)
            >>> n, bins = np.histogram(x, bins=np.linspace(0, 360, 37))
            >>> plot.histogram(n, bins)

        """
        if len(bin_edges) - 1 != len(counts):
            raise RuntimeError(
                'The length of bin_edges should be length of counts + 1')

        x = []
        y = []

        if self.use_radians:
            circle = 2 * np.pi
        else:
            circle = 360.

        step = circle / 1800.

        for i in range(len(bin_edges) - 1):
            for bin_edge in np.arange(bin_edges[i], bin_edges[i + 1],
                                      step=step):
                x.append(bin_edge)
                y.append(counts[i])
            x.append(bin_edges[i + 1])
            y.append(counts[i])

        # If last edge is same as first bin edge, connect the ends.
        if bin_edges[-1] % circle == bin_edges[0] % circle:
            x.append(bin_edges[0])
            y.append(counts[0])

        self.plot(x, y, mark=None, linestyle=linestyle)

    def histogram2d(self, *args):
        """Do not allow 2D histograms, it produces undesireable results."""

        warnings.warn('Plotting 2D histograms is not supported for PolarPlot')

    def set_xlimits(self, min=None, max=None):
        """Do not allow setting x limits, it messes with the axes."""

        warnings.warn('Setting x limits is not supported for PolarPlot')
