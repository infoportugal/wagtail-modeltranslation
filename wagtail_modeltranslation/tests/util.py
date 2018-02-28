

class PageFactory(object):

    def __init__(self, initial_path=0):
        self.root_path = initial_path

    @property
    def path(self):
        self.root_path += 1
        return self.root_path

    def create_page_tree(self, nodes=None):
        """
        Creates a page tree with a dict of page nodes following the below structure:
         {
            'model': Page,
            'args': [],
            'kwargs': {'title': 'root',},
            'children': {
                'child': {
                    'model': Page,
                    'args': [],
                    'kwargs': {'title': 'child',},
                    'children': {},
                },
            },
        },

        :param nodes: representing a page tree
        :return: site
        """
        if not nodes:
            return None

        try:
            from wagtail.core.models import Site
        except ImportError:
            from wagtail.wagtailcore.models import Site
        root_node = self.create_instance(nodes)
        site = Site.objects.create(root_page=root_node)
        return site

    def create_instance(self, node, parent=None, order=None):
        if parent:
            path = "{}{}".format(parent.path, "%04d" % (order,))
            depth = parent.depth + 1
        else:
            path = "%04d" % (self.path,)
            depth = 1

        args = node.get('args', [])
        kwargs = node.get('kwargs', {})
        kwargs['path'] = kwargs.get('path', path)
        kwargs['depth'] = kwargs.get('depth', depth)

        if parent:
            node_page = parent.add_child(instance=node['model'](*args, **kwargs))
            node_page.save()
        else:
            node_page = node['model'].objects.create(*args, **kwargs)

        node_page.save_revision().publish()
        node['instance'] = node_page

        for n, child in enumerate(node.get('children', {}).values()):
            self.create_instance(child, node_page, n+1)

        return node_page


page_factory = PageFactory()
