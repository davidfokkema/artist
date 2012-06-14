"""Utility functions"""

import inspect
import os


# global suffix and prefix for all subsequent graph names
__prefix = ''
__suffix = ''


def set_prefix(prefix):
    """Set global prefix for all graph names"""
    global __prefix
    __prefix = prefix

def set_suffix(suffix):
    """Set global suffix for all graph names"""

    global __suffix
    __suffix = suffix

def get_callers_name(level=2):
    """Return name of caller

    Return the name of the caller, optionally nested multiple levels deep.

    :param level: level of recursion.  level=0 is this method, level=1 is
        the caller, and level=2 is the caller's parent.

    """
    frame_record = inspect.stack()[level]
    function_name = frame_record[3]
    return function_name

def create_graph_name(suffix='', dirname=None):
    """Create a graph name

    :param suffix: optional suffix to add to name
    :param dirname: optional directory name

    """
    if suffix:
        suffix = '-%s' % suffix
    caller = get_callers_name()
    name = '%s%s%s%s' % (__prefix, caller, suffix, __suffix)
    if dirname:
        name = os.path.join(dirname, name)
    return name

def save_graph(graph, suffix='', dirname=None):
    """Save a graph using caller's name

    :type graph: GraphArtist instance
    :param suffix: optional suffix to add to name
    :param dirname: optional directory name

    """
    name = create_graph_name(suffix, dirname)
    graph.save(name)
