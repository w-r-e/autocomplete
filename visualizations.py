import networkx as nx
import matplotlib.pyplot as plt
from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG
def visualize_dawg(dawg):
    """Visualize the IncrementalDAWG using NetworkX."""

    G = nx.DiGraph()
    visited = set()

    def traverse(node):
        if node.node_id in visited:
            return
        visited.add(node.node_id)

        # Create node label
        label = f"id={node.node_id}"
        if node.word_grave:
            words = "\n".join([f"{w} ({wt})" for w, wt in node.word_grave])
            label += f"\n{words}"

        G.add_node(node.node_id, label=label)

        for ch, child in node.children.items():
            G.add_edge(node.node_id, child.node_id, label=ch)
            traverse(child)

    traverse(dawg.root)

    # Layout
    pos = nx.spring_layout(G, seed=42)

    node_labels = nx.get_node_attributes(G, "label")
    edge_labels = nx.get_edge_attributes(G, "label")

    plt.figure(figsize=(12, 8))

    nx.draw(
        G,
        pos,
        with_labels=False,
        node_size=1800,
        node_color="lightblue",
        arrows=True
    )

    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Incremental DAWG Visualization")
    plt.show()