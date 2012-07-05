import subprocess
import os
import tempfile
import shutil
from itertools import izip_longest

import jinja2
import numpy as np


RELATIVE_NODE_LOCATIONS = {'upper right': {'node_location': 'below left',
                                           'x': 1, 'y': 1},
                           'upper left': {'node_location': 'below right',
                                          'x': 0, 'y': 1},
                           'lower left': {'node_location': 'above right',
                                          'x': 0, 'y': 0},
                           'lower right': {'node_location': 'above left',
                                          'x': 1, 'y': 0}}


class GraphArtist:
    def __init__(self, axis='', width=r'.67\linewidth', height=None):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
                                                        'artist', 'templates'),
                                         finalize=self._convert_none)
        self.template = environment.get_template('artist_plot.tex')
        self.document_template = environment.get_template(
                                    'document_artist_plot.tex')

        self.shaded_regions_list = []
        self.plot_series_list = []
        self.pin_list = []
        self.horizontal_lines = []
        self.vertical_lines = []
        self.title = None
        self.axis = axis + 'axis'
        self.width = width
        self.height = height
        self.xlabel = None
        self.ylabel = None
        self.label = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None}
        self.ticks = {'x': [], 'y': []}

    def plot(self, x, y, xerr=[], yerr=[], mark='o',
             linestyle='solid', use_steps=False):
        self._clear_plot_mark_background(x, y, mark)
        options = self._parse_plot_options(mark, linestyle, use_steps)
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
        if len(bin_edges) - 1 != len(counts):
            raise RuntimeError(
                "The length of bin_edges should be length of counts + 1")
        x = bin_edges
        y = list(counts) + [counts[-1]]
        self.plot(x, y, mark=None, linestyle=linestyle, use_steps=True)

    def set_title(self, text):
        self.title = text

    def set_label(self, text, location='upper right'):
        if location in RELATIVE_NODE_LOCATIONS:
            label = RELATIVE_NODE_LOCATIONS[location].copy()
            label['text'] = text
            self.label = label
        else:
            raise RuntimeError("Unknown label location: %s" % location)

    def add_pin(self, text, location='left', x=None, use_arrow=False,
                relative_position=None, style=None):
        """Add pin to most recent data series"""

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
        """Add pin at x, y location

        If x, y are arrays or lists, relative position is used to pick a
        point from the arrays.  A relative position of zero will be the
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
        self.horizontal_lines.append({'value': yvalue,
                                      'options': linestyle})

    def draw_vertical_line(self, xvalue, linestyle=None):
        self.vertical_lines.append({'value': xvalue,
                                    'options': linestyle})

    def render(self, template=None):
        if not template:
            template = self.template

        response = template.render(axis=self.axis, title=self.title,
                                   width=self.width, height=self.height,
                                   xlabel=self.xlabel, ylabel=self.ylabel,
                                   label=self.label,
                                   limits=self.limits,
                                   ticks=self.ticks,
                                   shaded_regions_list=
                                        self.shaded_regions_list,
                                   series_list=self.plot_series_list,
                                   pin_list=self.pin_list,
                                   horizontal_lines=self.horizontal_lines,
                                   vertical_lines=self.vertical_lines)
        return response

    def render_as_document(self):
        return self.render(self.document_template)

    def save(self, dest_path):
        dest_path = self._add_extension('tex', dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render())

    def save_as_document(self, dest_path):
        dest_path = self._add_extension('tex', dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render_as_document())

    def save_as_pdf(self, dest_path):
        dest_path = self._add_extension('pdf', dest_path)
        build_dir = tempfile.mkdtemp()
        build_path = os.path.join(build_dir, 'document.tex')
        with open(build_path, 'w') as f:
            f.write(self.render_as_document())
        pdf_path = self._build_document(build_path)
        self._crop_document(pdf_path)
        os.rename(pdf_path, dest_path)
        shutil.rmtree(build_dir)

    def _build_document(self, path):
        dir_path = os.path.dirname(path)
        try:
            subprocess.check_output(['pdflatex', '-halt-on-error',
                                     '-output-directory', dir_path, path])
        except subprocess.CalledProcessError as exc:
            output_lines = exc.output.split('\n')
            error_lines = [line for line in output_lines if
                           line and line[0] == '!']
            errors = '\n'.join(error_lines)
            raise RuntimeError("LaTeX compilation failed:\n" + errors)

        pdf_path = path.replace('.tex', '.pdf')
        return pdf_path

    def _crop_document(self, path):
        output_path = 'crop-output.pdf'
        try:
            subprocess.check_output(['pdfcrop', path, output_path])
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("Cropping PDF failed:\n" + exc.output)
        os.rename(output_path, path)

    def set_xlabel(self, text):
        self.xlabel = text

    def set_ylabel(self, text):
        self.ylabel = text

    def set_xlimits(self, min=None, max=None):
        self.limits['xmin'] = min
        self.limits['xmax'] = max

    def set_ylimits(self, min=None, max=None):
        self.limits['ymin'] = min
        self.limits['ymax'] = max

    def set_xticks(self, ticks):
        self.ticks['x'] = ticks

    def set_logxticks(self, logticks):
        self.ticks['x'] = ['1e%d' % u for u in logticks]

    def set_yticks(self, ticks):
        self.ticks['y'] = ticks

    def set_logyticks(self, logticks):
        self.ticks['y'] = ['1e%d' % u for u in logticks]

    def _parse_plot_options(self, mark=None, linestyle=None,
                            use_steps=False):
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
            index = int(round(max_idx_x * relative_position))
            return x[index], y[index]

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
