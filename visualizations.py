import networkx as nx
import matplotlib.pyplot as plt
from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG, DAWGNode
import pydot

def visualize_dawg(dawg: IncrementalDAWG) -> None:
    """Visualize the IncrementalDAWG using NetworkX."""
    G = nx.DiGraph()
    # creates direct graph G (direct to show direction duh)
    visited = set()
    def add_nodes_and_edges(node: DAWGNode):
        """Recursively add nodes and edges to graph G"""
        if node in visited:
            return
        visited.add(node)
        # to prevent duplicate traversal
        node_id = f"id{node.node_id}"
        # gives each node a unique id
        G.add_node(node_id, is_end=node.is_end)

        for let, child in node.children.items():
            child_id = f"id{child.node_id}"
            G.add_node(child_id, is_end=child.is_end)
            # to make sure child has an 'is_end' if not code DOESN'T WORK
            G.add_edge(node_id, child_id, label=let)
            # connecting all nodes and its children with edges
            add_nodes_and_edges(child)
            # recursion
    add_nodes_and_edges(dawg.root)
    colors = ['lightgreen' if G.nodes[n]['is_end'] else 'lightgray' for n in G.nodes]
    # diff colors whether the node is an end-of-the-word node or just a node
    pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
    # position of nodes (pydot makes the visualization nice and structured)
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
