# coding: utf-8
import inspect


def compare_class_tree_depth(a, b):
    """
     Function to sort a list of class objects, where subclasses
    have lower indices than their superclasses
    """

    return len(inspect.getmro(b)) - len(inspect.getmro(a))
