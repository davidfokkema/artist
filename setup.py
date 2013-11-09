from setuptools import setup, find_packages
setup(
    name = "artist",
    version = "0.10.0",
    packages = find_packages(),
    url = "http://github.com/davidfokkema/artist/",
    author = "David Fokkema",
    author_email = "davidfokkema@icloud.com",
    description = "A plotting library for Python with LaTeX output",

    install_requires = ['jinja2', 'numpy']
)
