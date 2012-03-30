import jinja2


class GraphArtist:
    def __init__(self, axis='', width=r'.67\linewidth'):
        environment = jinja2.Environment(loader=jinja2.PackageLoader(
                                                        'artist', 'templates'),
                                         finalize=self._convert_none)
        self.template = environment.get_template('artist_plot.tex')

        self.shaded_regions_list = []
        self.plot_series_list = []
        self.pin_list = []
        self.axis = axis + 'axis'
        self.width = width
        self.xlabel = None
        self.ylabel = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None}
        self.ticks = {'x': [], 'y': []}

    def plot(self, x, y, mark='o', linestyle='solid'):
        options = self._parse_plot_options(mark, linestyle)
        self.plot_series_list.append({'options': options,
                                      'data': zip(x, y)})

    def add_pin(self, text, location='above right', relative_position=.9,
                use_arrow=True):
        """Add pin to most recent data series"""

        try:
            series = self.plot_series_list[-1]
        except IndexError:
            raise RuntimeError("""
                First plot a data series, before using this function""")

        data = series['data']
        x, y = zip(*data)
        self.add_pin_at_xy(x, y, text, location, relative_position,
                           use_arrow)

    def add_pin_at_xy(self, x, y, text, location='above right',
                relative_position=.9, use_arrow=True):
        """Add pin at x, y location

        If x, y are arrays or lists, relative position is used to pick a
        point from the arrays.  A relative position of zero will be the
        first point from the series, while 1.0 will be the last point.

        """
        x, y = self._calc_position_for_pin(x, y, relative_position)
        self.pin_list.append({'x': x, 'y': y, 'text': text,
                              'location': location,
                              'use_arrow': use_arrow})

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

    def render(self):
        response = self.template.render(axis=self.axis,
                                        width=self.width,
                                        xlabel=self.xlabel,
                                        ylabel=self.ylabel,
                                        limits=self.limits,
                                        ticks=self.ticks,
                                        shaded_regions_list=
                                            self.shaded_regions_list,
                                        series_list=self.plot_series_list,
                                        pin_list=self.pin_list)
        return response

    def save(self, path):
        path = self._add_tex_extension(path)
        with open(path, 'w') as f:
            f.write(self.render())

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

    def _parse_plot_options(self, mark, linestyle):
        options = []
        if mark is not None:
            options.append('mark=%s' % mark)
        else:
            options.append('no markers')

        if linestyle is not None:
            options.append(linestyle)
        else:
            options.append('only marks')

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

    def _add_tex_extension(self, path):
        if not '.' in path:
            return path + '.tex'
        else:
            return path

    def _convert_none(self, variable):
        if variable is not None:
            return variable
        else:
            return ''
