from tkinter import Tk, Entry, Listbox, END
from collections import defaultdict

class TrieNode:
    __slots__ = ("children", "is_end", "weight", "max_weight")

    def __init__(self):
        self.children = defaultdict(TrieNode)        # char -> TrieNode
        self.is_end = False                          # True if node represents a complete word
        self.weight = 0                              # weight of word if is_end == True
        self.max_weight = 0                          # maximum weight in this subtree

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, weight):
        node = self.root
        node.max_weight = max(node.max_weight, weight)

        for char in word:
            node = node.children[char]
            node.max_weight = max(node.max_weight, weight)
        node.is_end = True      # corrected from is_word
        node.weight = weight

    def search(self, prefix, k=10):
        node = self.root
        for char in prefix:
            node = node.children[char]

        suggestions = []
        self._find_suggestions(node, prefix, suggestions)

        # Sort by weight descending and take top-k
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [word for word, weight in suggestions[:k]]

    def _find_suggestions(self, node, prefix, suggestions):
        if node.is_end:
            suggestions.append((prefix, node.weight))  # add weight
        for char, child in node.children.items():
            self._find_suggestions(child, prefix + char, suggestions)


def update_suggestions(event, trie, entry, suggestions_listbox):
    prefix = entry.get()
    if not prefix:
        suggestions_listbox.delete(0, END)
        return
    suggestions = trie.search(prefix, k=10)  # get top 10 suggestions
    suggestions_listbox.delete(0, END)
    for suggestion in suggestions:
        suggestions_listbox.insert(END, suggestion)


def load_words(filename):
    words = dict()
    with open(filename, 'r') as f:
        for line in f:
            word, count = line.strip().split(',', 1)
            words[word] = int(count)
    return words

def main():
    # Set the path to the file you'd like to load
    file_path = "unigram_freq.csv"
    trie = Trie()
    
    words = load_words(file_path)
    for word, count in words.items():
        trie.insert(word, count)

    root = Tk()
    root.title("Autocomplete App")

    entry = Entry(root)
    entry.pack(padx=10, pady=10)
    entry.bind("<KeyRelease>", lambda e: update_suggestions(e, trie, entry, suggestions_listbox))

    suggestions_listbox = Listbox(root, width=50)
    suggestions_listbox.pack(padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()