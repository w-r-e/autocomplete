import networkx as nx
import matplotlib.pyplot as plt
from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG

def visualize_dawg(dawg: IncrementalDAWG) -> None:
    """Visualize the IncrementalDAWG using NetworkX."""


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