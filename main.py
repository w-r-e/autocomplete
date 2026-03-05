from tkinter import Tk, Entry, Listbox, END
from collections import defaultdict


class TrieNode:
    """Class that represents a Node in the Trie"""
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


def update_suggestions(trie, entry, suggestions_listbox):
    """Updates the suggestions based on the changes from the recent user entry."""
    prefix = entry.get()
    if not prefix:
        suggestions_listbox.delete(0, END)
        return
    suggestions = trie.search(prefix, k=10)  # get top 10 suggestions
    suggestions_listbox.delete(0, END)
    for suggestion in suggestions:
        suggestions_listbox.insert(END, suggestion)


def load_words(filename):
    """Method used to load words from a local CSV."""
    words = dict()
    with open(filename, 'r') as f:
        for line in f:
            word, count = line.strip().split(',', 1)
            words[word] = int(count)
    return words


def main():
    """Main function that packages the Trie setup"""
    # Set the path to the file you'd like to load
    file_path = "unigram_freq.csv"
    trie = Trie()

    words = load_words(file_path)
    for word, count in words.items():
        trie.insert(word, count)

    root = Tk()
    root.config(bg="dark grey")
    root.title("Autocomplete App")

    entry = Entry(root)
    entry.pack(padx=10, pady=10)

    suggestions_listbox = Listbox(root, width=50, bg="black", fg="lime", selectbackground="blue")
    suggestions_listbox.pack(padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
