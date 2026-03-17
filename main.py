from trie import Trie
from radix_tree import RadixTree
from tkinter import Tk, Entry, Listbox, END


def load_words(filename) -> dict[str, int]:
    """Method used to load words from a local CSV."""
    words = dict()
    with open(filename, 'r') as f:
        for line in f:
            word, count = line.strip().split(',', 1)
            words[word] = int(count)
    return words


def trie_setup(words: dict[str, int]) -> Trie:
    """Sets up the Trie with the given words and their weights."""
    t = Trie()
    for word, count in words.items():
        t.insert(word, count)
    return t


def radix_tree_setup(words: dict[str, int]) -> RadixTree:
    """Sets up the RadixTree with the given words and their weights."""
    rt = RadixTree()
    for word, count in words.items():
        rt.insert(word, count)
    return rt


def update_suggestions(structure: Trie | RadixTree, entry: Entry, suggestions_listbox: Listbox) -> None:
    """Updates the suggestions listbox using whichever structure is currently active."""
    prefix = entry.get()
    suggestions_listbox.delete(0, END)
    if not prefix:
        return
    for suggestion in structure.search(prefix, k=10):
        suggestions_listbox.insert(END, suggestion)


def export_tree(structure: Trie | RadixTree, filename: str = "tree_dump.txt") -> None:
    """Exports a ASCII tree visualization of the structure."""

    def write_trie(node, prefix, f, indent="", last=True, char=""):
        """Recursivley traverses a regular Trie in order to create a file that visualises the tree"""
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
        """Recursivley traverses a Radix Trie in order to create a file that visualises the tree"""
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

if __name__ == "__main__":
    words = load_words("unigram_freq.csv")

    choice = input("Which structure? (trie / radix): ").strip().lower()
    if choice == "radix":
        structure = radix_tree_setup(words)
    else:
        structure = trie_setup(words)

    export_tree(structure)

    root = Tk()
    root.config(bg="dark grey")
    root.title(f"Autocomplete App ({choice})")

    entry = Entry(root)
    entry.pack(padx=10, pady=10)

    suggestions_listbox = Listbox(root, width=50, bg="black", fg="light blue", selectbackground="blue")
    suggestions_listbox.pack(padx=10, pady=10)

    entry.bind("<KeyRelease>", lambda event: update_suggestions(structure, entry, suggestions_listbox))
    root.mainloop()
