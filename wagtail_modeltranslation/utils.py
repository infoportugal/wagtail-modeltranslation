# coding: utf-8
import inspect


def compare_class_tree_depth(model_class):
    """
     Function to sort a list of class objects, where subclasses
    have lower indices than their superclasses
    """

    return -len(inspect.getmro(model_class))
