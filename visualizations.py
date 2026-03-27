import networkx as nx
import matplotlib.pyplot as plt
from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG, DAWGNode
from collections import deque, defaultdict

def hierarchical_layout(G, root):
    """Create a cleaner, more structured layout for DAWG visualization"""

    tiers = defaultdict(list)
    # to group each node by depth
    visited = set()

    queue = deque([(root, 0)])
    # starting with root note (depth 0)
    while queue:
        node, depth = queue.popleft()
        # next node and depth
        if node in visited:
            continue
        visited.add(node)

        tiers[depth].append(node)
        # group nodes by how far their depth is from root

        for neighbor in G.successors(node):
            queue.append((neighbor, depth + 1))
        # add their children to queue as well

    pos = {}
    for depth, nodes in tiers.items():
        # one row at a time
        width = len(nodes)
        for i, node in enumerate(nodes):
            # use enumerate to keep track of index
            x = i - width / 2
            # center node at 0
            y = -depth
            # depth must increase downward
            pos[node] = (x, y)
            # store position

    return pos

def visualize_dawg(dawg: IncrementalDAWG, prefix: str, k: int = 10) -> None:
    """Visualize the IncrementalDAWG subgraph of top-k autocorrrect results using NetworkX."""
    G = nx.DiGraph()
    # creates direct graph G (direct to show direction duh)
    visited = set()
    top_words = dawg.search(prefix, k)

    def add_nodes_and_edges(word):
        """Add top-n nodes and edges to graph G"""
        node = dawg.root
        id = f"id{node.node_id}"
        G.add_node(id, is_end=node.is_end)

        for c in word:
            child = node.children[c]
            par_id = f"id{node.node_id}"
            child_id = f"id{child.node_id}"

            G.add_node(child_id, is_end=child.is_end)
            G.add_edge(par_id, child_id, label=c)

            node = child
    for word in top_words:
        add_nodes_and_edges(word)
    colors = ['lightgreen' if G.nodes[n]['is_end'] else 'lightgray' for n in G.nodes]
    # diff colors whether the node is an end-of-the-word node or just a node
    # pos = nx.spring_layout(G, seed=41)
    pos = hierarchical_layout(G, list(G.nodes)[0])
    # position of nodes 
    plt.figure(figsize=(14, 10))
    # well we're gonna need a space for this visualization
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1500, font_size=10)
    # visualizes the dawg yup
    plt.title("Incremental DAWG Visualization")
    plt.axis('off')
    # we dont need x or y axis
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    # dictionary mapping edges to labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    # adds edge labels to visualization
    plt.show()


def export_tree(structure: Trie | RadixTree, filename: str) -> None:
    """Exports a ASCII tree visualization of the structure."""

    def write_trie(node, prefix, f, indent="", last=True, char=""):
        connector = "└── " if last else "├── "

        if char:
            label = char
            if node.is_end:
                label += f" ({prefix}, w={node.weight})"
            f.write(indent + connector + label + "\n")

        children = list(node.children.items())

        for i, (c, child) in enumerate(children):
            is_last = i == len(children) - 1
            new_indent = indent + ("    " if last else "│   ")
            write_trie(child, prefix + c, f, new_indent, is_last, c)

    def write_radix(node, prefix, f, indent="", last=True, label=""):
        connector = "└── " if last else "├── "

        if label:
            display = label
            if node.is_end:
                display += f" ({prefix}, w={node.weight})"
            f.write(indent + connector + display + "\n")

        children = list(node.children.items())

        for i, (edge, child) in enumerate(children):
            is_last = i == len(children) - 1
            new_indent = indent + ("    " if last else "│   ")
            write_radix(child, prefix + edge, f, new_indent, is_last, edge)

    with open(filename, "w") as f:

        if isinstance(structure, Trie):
            f.write("TRIE STRUCTURE\n")
            f.write("root\n")
            children = list(structure.root.children.items())

            for i, (c, child) in enumerate(children):
                write_trie(child, c, f, "", i == len(children) - 1, c)

        else:
            f.write("RADIX TREE STRUCTURE\n")
            f.write("root\n")
            children = list(structure.root.children.items())

            for i, (edge, child) in enumerate(children):
                write_radix(child, edge, f, "", i == len(children) - 1, edge)

    print(f"Tree exported to {filename}")
