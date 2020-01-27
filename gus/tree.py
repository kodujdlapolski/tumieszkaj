"""
The module provides methods to work with trees
"""

import anytree as t
from tqdm import tqdm


def build_tree(entries):
    """
    Builds a tree from a list of entries.
    :param entries: list of entries, where each entry is a dictionary with the
                    following fields: id, name, and parentId.
    :return: a tree
    """
    root = t.Node('root', my_name='root', id=-1)
    nodes = {}
    for e in tqdm(entries, desc='Building tree'):
        id = e['id']
        parent_id = e.get('parentId', None)
        if parent_id is None:
            parent = root
        else:
            parent = nodes.get(parent_id, None)
            if parent is None:
                parent = t.Node('', id=parent_id)
                nodes[parent_id] = parent

        assert not parent is None

        node = nodes.get(id, None)
        if node is None:
            node = t.Node('', parent=parent, id=id)
            nodes[id] = node
        else:
            if node.parent is None:
                node.parent = parent
        node.name = e['name']

    return root


def find_subtree_spanning_leaves(leaves):
    """
    Creates the smallest subtree containing given leaf nodes.
    :param leaves: leaf nodes nodes of a tree. Leaves must belong to the same
                   tree.
    :return: the root of the subtree found.
    """
    new_nodes = {}
    for leave in leaves:
        for node in reversed(leave.path):
            id = node.id
            parent = node.parent
            if not parent is None:
                parent_id = parent.id
                new_parent = new_nodes.get(parent_id, None)
                if new_parent is None:
                    new_parent = t.Node('', id=parent_id)
                    new_nodes[parent_id] = new_parent

            new_node = new_nodes.get(id, None)
            if new_node is None:
                new_node = t.Node('', id=id, parent=new_parent)
                new_nodes[id] = new_node
            else:
                if parent is None:
                    subtree_root = new_node
                else:
                    new_node.parent = new_parent
            new_node.name = node.name
    return subtree_root


def render(tree):
    """
    Renders a given tree structure in console.
    """
    for pre, _, node in t.RenderTree(tree):
        print("%s%s (%s)" % (
            pre,
            node.name,
            node.id if hasattr(node, 'id') else ''))


def all_nodes(tree):
    return t.PreOrderIter(tree)
