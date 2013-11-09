"""Utility functions."""

import inspect
import os

import numpy as np


# global suffix and prefix for all subsequent graph names
__prefix = ''
__suffix = ''


def set_prefix(prefix):
    """Set global prefix for all graph names.

    :param prefix: prefix for all plot names
    :type prefix: string

    """
    global __prefix
    __prefix = prefix


def set_suffix(suffix):
    """Set global suffix for all graph names.

    :param prefix: suffix for all plot names
    :type prefix: string

    """

    global __suffix
    __suffix = suffix


def get_callers_name(level=2):
    """Return name of caller.

    Return the name of the caller, optionally nested multiple levels deep.

    :param level: level of recursion.  level=0 is this method, level=1 is
        the caller, and level=2 is the caller's parent.

    """
    frame_record = inspect.stack()[level]
    function_name = frame_record[3]
    return function_name


def create_graph_name(suffix='', dirname=None):
    """Create a graph name using the name of the caller.

    :param suffix: optional suffix to add to name
    :param dirname: optional directory name

    :return: path for the named graph
    :rtype: string

    """
    if suffix:
        suffix = '-%s' % suffix
    caller = get_callers_name(level=3)
    name = '%s%s%s%s' % (__prefix, caller, suffix, __suffix)
    if dirname:
        name = os.path.join(dirname, name)
    return name


def save_graph(graph, suffix='', dirname=None, pdf=False):
    """Save a graph using caller's name.

    :type graph: GraphArtist instance
    :param suffix: optional suffix to add to name
    :param dirname: optional directory name
    :param pdf: if True, the saved graph is additionally rendered and
        saved as a pdf, alongside the LaTeX file.

    """
    name = create_graph_name(suffix, dirname)
    graph.save(name)
    if pdf:
        graph.save_as_pdf(name)


def save_data(data, suffix='', dirname=None):
    """Save a dataset using caller's name.

    :param data: a list or numpy array containing the data
    :param suffix: optional suffix to add to name
    :param dirname: optional directory name

    """
    if type(data) == list:
        data = np.array(data).T

    name = create_graph_name(suffix, dirname) + '.txt'
    np.savetxt(name, data)
