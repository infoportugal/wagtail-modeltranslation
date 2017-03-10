# coding: utf-8
import inspect


def compare_class_tree_depth(model_class):
    """
     Function to sort a list of class objects, where subclasses
    have lower indices than their superclasses
    """

    return -len(inspect.getmro(model_class))


def import_from_string(name):
    """
    Returns a module from a string path
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod