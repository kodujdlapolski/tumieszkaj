import anytree as t


def build_tree(entries):
    root = t.Node('root', my_name='root', id=-1)
    nodes = {}
    for e in entries:
        id = e['id']
        parent_id = e.get('parentId', None)
        if parent_id is None:
            parent = root
        else:
            parent = nodes.get(parent_id, None)
            if parent is None:
                parent = t.Node('', id=parent_id)
                nodes[parent_id]  = parent

        assert not parent is None

        node = nodes.get(id, None)
        if node is None:
            node = t.Node('', parent=parent, id=id)
            nodes[id]  = node
        else:
            if node.parent is None:
                node.parent = parent
        node.name = e['name']

    return root

def find_subtree_spanning_leaves(leaves):
    new_nodes = {}
    for leave in leaves:
        for node in reversed(leave.path):
            id = node.id
            parent = node.parent
            if not parent is None:
                parent_id = parent.id
                new_parent = new_nodes.get(parent_id, None)
                if new_parent is None:
                    new_parent = t.Node('', id = parent_id)
                    new_nodes[parent_id] = new_parent

            new_node = new_nodes.get(id, None)
            if new_node is None:
                new_node = t.Node('', id = id, parent=new_parent)
                new_nodes[id] = new_node
            else:
                if parent is None:
                    subtree_root = new_node
                else:
                    new_node.parent = new_parent
            new_node.name = node.name
    return subtree_root

def render_tree(tree):
    for pre, _, node in t.RenderTree(tree):
        print("%s%s (%s)" % (
            pre,
            node.name,
            node.id if hasattr(node, 'id') else ''))

def all_nodes(tree):
    return t.PreOrderIter(tree)