"""
Radix Tree Implementation

Module Description
==================

Contains a file of classes and functions that implements the Radix Tree data
sturcture that is a more space optimized way to store multiple letters (suffix)
in a singular node.

"""

import sys


class RadixNode:
    """
    Class that represents a Node in the Radix Tree.

    Unlike a TrieNode — whose edges are single characters — each edge in a
    radix tree carries a *string* label, compressing chains of single-child
    nodes into one hop.

    Instance Attributes:
        - children: A plain dict mapping an edge label (str) to a RadixNode.
                    Only the first character of each label is unique among
                    siblings (the radix-tree invariant).
        - is_end: True if this node represents the end of an inserted word.
        - weight: Frequency of the word ending here; 0 when is_end is False.
        - max_weight: Maximum weight in the entire subtree rooted at this node
                      (used to prune unpromising branches during search).
    """
    __slots__ = ("children", "is_end", "weight", "max_weight")

    def __init__(self):
        self.children: dict[str, "RadixNode"] = {}  # edge_label -> RadixNode
        self.is_end: bool = False
        self.weight: int = 0
        self.max_weight: int = 0


class RadixTree:
    """
    Radix Tree (Patricia Trie) for weighted-word autocomplete.

    Compared to a character-level Trie, a Radix Tree merges chains of
    single-child nodes into one edge, reducing both node count and memory.
    The public interface (insert / search) is identical to the Trie class in
    trie.py, so the two are drop-in replacements for each other.
    """

    def __init__(self):
        self.root = RadixNode()

    def search(self, prefix: str, k: int = 10) -> list[str]:
        """Return the top-k words (by weight) that start with *prefix*."""
        node, remainder = self._find_prefix_node(self.root, prefix)
        if node is None:
            return []

        # *remainder* is the portion of the last matched edge label that
        # extends beyond the query prefix — we carry it as part of the
        # accumulated word string so suggestions are reconstructed correctly.
        suggestions: list[tuple[str, int]] = []
        self._find_suggestions(node, prefix + remainder, suggestions, k, -1)
        return [word for word, _ in suggestions]

    def _common_prefix_len(self, a: str, b: str) -> int:
        """Return the length of the longest common prefix of *a* and *b*."""
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i

    def insert(self, word: str, weight: int) -> None:
        """
        Iterative insert of *word* / *weight* starting from *root*.

        Walks through the tree looking for a child whose edge label shares a prefix
        with the remaining word. Four cases arise at each step:

        1. No matching child  →  add a new leaf with the full remaining word.
        2. Full edge consumed, full word consumed  →  mark node as end.
        3. Full edge consumed, word has more chars  →  descend and repeat.
        4. Partial match  →  split the edge at the common-prefix boundary,
           creating an intermediate node and (up to) two children.
        """
        node = self.root
        node.max_weight = max(node.max_weight, weight)
        remaining = word

        while remaining:
            first_char = remaining[0]

            edge_label, _ = None, None
            for label, ch in node.children.items():
                if label[0] == first_char:
                    edge_label, _ = label, ch
                    break

            # Case 1 — no matching edge
            if edge_label is None:
                leaf = RadixNode()
                leaf.is_end = True
                leaf.weight = weight
                leaf.max_weight = weight
                node.children[remaining] = leaf
                return

            # There is an edge whose label starts with first_char.
            edge_label, child = None, None
            for label, ch in node.children.items():
                if label[0] == first_char:
                    edge_label, child = label, ch
                    break

            cp = self._common_prefix_len(edge_label, remaining)

            if cp == len(edge_label) == len(remaining):
                # Case 2 — edge and word are identical: mark end.
                child.is_end = True
                child.weight = weight
                child.max_weight = max(child.max_weight, weight)
                return

            if cp == len(edge_label):
                # Case 3 — edge fully consumed but word has more characters:
                # update max_weight and descend.
                child.max_weight = max(child.max_weight, weight)
                node = child
                remaining = remaining[cp:]
                continue

            # Case 4 — partial match: split the existing edge.
            #
            # Before:  node --edge_label--> child
            # After:
            #   node --common_prefix--> split_node --edge_suffix--> child
            #                                      \--word_suffix--> new_leaf  (if any)
            common = edge_label[:cp]
            edge_suffix = edge_label[cp:]
            word_suffix = remaining[cp:]

            # Create the intermediate split node.
            split_node = RadixNode()
            split_node.max_weight = max(child.max_weight, weight)

            # Re-attach the existing child under the shorter suffix.
            split_node.children[edge_suffix] = child

            # Replace the old edge with the common-prefix edge.
            del node.children[edge_label]
            node.children[common] = split_node

            if word_suffix:
                # The new word diverges here — add a fresh leaf.
                new_leaf = RadixNode()
                new_leaf.is_end = True
                new_leaf.weight = weight
                new_leaf.max_weight = weight
                split_node.children[word_suffix] = new_leaf
            else:
                # The new word ends exactly at the split point.
                split_node.is_end = True
                split_node.weight = weight

            return

    def _find_prefix_node(self, root: RadixNode, prefix: str) -> tuple[RadixNode | None, str]:
        """
        Walk the tree consuming *prefix*.

        Returns ``(node, remainder)`` where *node* is the deepest node reached
        and *remainder* is the unmatched tail of the last edge label (i.e. the
        part of the edge that lies *beyond* the prefix).  If the prefix is not
        present in the tree, returns ``(None, "")``.

        Example — tree has edge "hello", query prefix is "hel":
            returns (node_for_hello_end, "lo")
        """
        node = root
        remaining = prefix

        while remaining:
            first_char = remaining[0]

            # Find the child whose edge starts with first_char.
            matched_label, child = None, None
            for label, ch in node.children.items():
                if label[0] == first_char:
                    matched_label, child = label, ch
                    break

            if matched_label is None:
                return None, ""

            cp = self._common_prefix_len(matched_label, remaining)

            if cp < len(remaining):
                if cp < len(matched_label):
                    # Prefix diverges inside the edge — not in tree.
                    return None, ""
                # Edge fully consumed; continue with the rest of the prefix.
                node = child
                remaining = remaining[cp:]
            else:
                # Prefix fully consumed somewhere inside (or at the end of) the edge.
                # The "remainder" is whatever is left of the edge label after the prefix.
                return child, matched_label[cp:]

        # Prefix was empty to begin with — start suggestions from root.
        return node, ""

    def _find_suggestions(
        self,
        node: RadixNode,
        accumulated: str,
        suggestions: list[tuple[str, int]],
        k: int,
        min_weight: int) -> None:
        """
        Depth-first search from *node*, collecting the top-k words by weight.

        *accumulated* holds the full word string built up so far (prefix +
        all edge labels traversed).  Branches whose "max_weight" cannot
        beat the current k-th best are pruned early.
        """
        if node.is_end:
            suggestions.append((accumulated, node.weight))
            suggestions.sort(key=lambda x: x[1], reverse=True)
            if len(suggestions) > k:
                suggestions.pop()
            if len(suggestions) == k:
                min_weight = suggestions[-1][1]

        for label, child in node.children.items():
            if child.max_weight <= min_weight:
                continue
            self._find_suggestions(child, accumulated + label, suggestions, k, min_weight)

    def get_total_memory(self):
        """Calculate total memory usage of this Radix Tree."""
        seen = set()
        return self._measure(self.root, seen)

    def _measure(self, node, seen):
        """Recursive helper to measure memory of node and all children."""
        if node in seen:
            return 0
        seen.add(node)

        total = sys.getsizeof(node)
        total += sys.getsizeof(node.children)

        for label, child in node.children.items():
            total += sys.getsizeof(label)  # The edge label string
            total += self._measure(child, seen)

        total += sys.getsizeof(node.weight)
        total += sys.getsizeof(node.max_weight)

        return total
