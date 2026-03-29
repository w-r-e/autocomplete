"""
Trie Implementation

Module Description 
==================

This python file includes classes and functions that store the suffixes of a prefix
the user types into the interactive visualization throughout multiple connected
nodes in a tree, one letter in each node. 
"""

from collections import defaultdict
import sys


class TrieNode:
    """
    Class that represents a Node in the Trie.

    Instance Attributes:
        - children: A defaultdict containing the TrieNode children connected to this node.
        - is_end: A boolean signifying wheter the node represents the end of a word.
        - weight: The associated frequency of a word. Equals 0 unless is_end is true.
        - max_weight: The maximum weight of all the children.
    """
    __slots__ = ("children", "is_end", "weight", "max_weight")

    def __init__(self):
        self.children = defaultdict(TrieNode)        # char -> TrieNode
        self.is_end = False                          # True if node represents a complete word
        self.weight = 0                              # weight of word if is_end == True
        self.max_weight = 0                          # maximum weight in this subtree


class Trie:
    """Class that represents a Trie"""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, weight: int) -> None:
        """Inserts the characters of a word into the Trie."""
        node = self.root
        node.max_weight = max(node.max_weight, weight)

        for char in word:
            node = node.children[char]
            node.max_weight = max(node.max_weight, weight)
        node.is_end = True      # corrected from is_word
        node.weight = weight

    def search(self, prefix: str, k: int = 10) -> list[str]:
        """Returns list of top k (default 10) suggested words that match the prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        suggestions = []
        self._find_suggestions(node, prefix, suggestions, k, -1)

        return [word for word, _ in suggestions]

    def _find_suggestions(self, node: TrieNode, prefix: str, suggestions: list, k: int, min_weight: int):
        """
        Recursively traverse the Trie to get the top-k suggestions.
        Prune branches whose max_weight <= current minimum.
        """
        if node.is_end:
            suggestions.append((prefix, node.weight))
            suggestions.sort(key=lambda x: x[1], reverse=True)
            if len(suggestions) > k:
                suggestions.pop()
            if len(suggestions) == k:
                min_weight = suggestions[-1][1]

        for char, child in node.children.items():
            if child.max_weight <= min_weight:
                continue
            self._find_suggestions(child, prefix + char, suggestions, k, min_weight)

    def get_total_memory(self):
        """Calculate total memory usage of this Trie."""
        seen = set()
        return self._measure(self.root, seen)

    def _measure(self, node, seen):
        """Recursive helper to measure memory of node and all children."""
        if node in seen:
            return 0
        seen.add(node)

        total = sys.getsizeof(node)

        # Size of the children defaultdict
        total += sys.getsizeof(node.children)

        # Size of each child and its key
        for char, child in node.children.items():
            total += sys.getsizeof(char)  # The character key
            total += self._measure(child, seen)

        total += sys.getsizeof(node.is_end)
        total += sys.getsizeof(node.weight)
        total += sys.getsizeof(node.max_weight)

        return total
