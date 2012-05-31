import jinja2
import tempfile
import os
import subprocess
import shutil

from graph_artist import GraphArtist


class MultiPlot:
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
        self.axis = axis
        self.width = width
        self.height = height

        self.subplots = []
        for i in range(rows):
            for j in range(columns):
                self.subplots.append(SubPlot(i, j))

    def plot(self, row, column, *args, **kwargs):
        subplot = self._get_subplot_at(row, column)
        subplot.plot.plot(*args, **kwargs)

    def histogram(self, row, column, *args, **kwargs):
        subplot = self._get_subplot_at(row, column)
        subplot.plot.histogram(*args, **kwargs)

    def add_pin(self, row, column, *args, **kwargs):
        subplot = self._get_subplot_at(row, column)
        subplot.plot.add_pin(*args, **kwargs)

    def add_pin_at_xy(self, row, column, *args, **kwargs):
        subplot = self._get_subplot_at(row, column)
        subplot.plot.add_pin_at_xy(*args, **kwargs)

    def shade_region(self, row, column, *args, **kwargs):
        subplot = self._get_subplot_at(row, column)
        subplot.plot.shade_region(*args, **kwargs)

    def _get_subplot_at(self, row, column):
        idx = row * self.columns + column
        return self.subplots[idx]

    def render(self, template=None):
        if not template:
            template = self.template

        response = template.render(rows=self.rows, columns=self.columns,
                                   width=self.width, height=self.height,
                                   subplots=self.subplots)
        return response

    def render_as_document(self):
        return self.render(self.document_template)

    def save(self, dest_path):
        dest_path = self._add_tex_extension(dest_path)
        with open(dest_path, 'w') as f:
            f.write(self.render())

    def save_as_pdf(self, dest_path):
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


class SubPlot:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.plot = GraphArtist()
