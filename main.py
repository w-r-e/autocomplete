from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG
from tkinter import Tk, Entry, Listbox, Button, Frame, END

def load_words(filename):
    """Method used to load words from a local CSV."""
    words = []
    with open(filename, 'r') as f:
        for line in f:
            word, count = line.strip().split(',', 1)
            words.append((word, int(count)))
    return sorted(words, key=lambda x: x[0])


def trie_setup(words: dict[str, int]) -> Trie:
    """Sets up the Trie with the given words and their weights."""
    t = Trie()
    for word, count in words:
        t.insert(word, count)
    return t


def radix_tree_setup(words: dict[str, int]) -> RadixTree:
    """Sets up the RadixTree with the given words and their weights."""
    rt = RadixTree()
    for word, count in words:
        rt.insert(word, count)
    return rt

def dawg_setup(words: dict[str, int]) -> IncrementalDAWG:
    """Sets up the IncrementalDAWG with the given words and their weights."""
    dawg = IncrementalDAWG()
    for word, count in words:
        dawg.insert(word, count)
    return dawg

def update_suggestions(structure: Trie | RadixTree | IncrementalDAWG, entry: Entry, suggestions_listbox: Listbox) -> None:
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

    # Pre-build all structures
    trie = trie_setup(words)
    radix = radix_tree_setup(words)
    dawg = dawg_setup(words)

    # Default structure
    current_structure = {"obj": trie, "name": "trie"}

    root = Tk()
    root.config(bg="dark grey")
    root.title("Autocomplete App")

    def switch_structure(name):
        if name == "trie":
            current_structure["obj"] = trie
        elif name == "radix":
            current_structure["obj"] = radix
        else:
            current_structure["obj"] = dawg

        current_structure["name"] = name
        root.title(f"Autocomplete App ({name})")

        # Clear suggestions when switching
        suggestions_listbox.delete(0, END)

    def on_key_release(event):
        update_suggestions(current_structure["obj"], entry, suggestions_listbox)

    # Buttons
    button_frame = Frame(root, bg="dark grey")
    button_frame.pack(pady=5)

    Button(button_frame, text="Trie", command=lambda: switch_structure("trie")).pack(side="left", padx=5)
    Button(button_frame, text="Radix", command=lambda: switch_structure("radix")).pack(side="left", padx=5)
    Button(button_frame, text="DAWG", command=lambda: switch_structure("dawg")).pack(side="left", padx=5)

    # Entry + suggestions
    entry = Entry(root)
    entry.pack(padx=10, pady=10)

    suggestions_listbox = Listbox(
        root,
        width=50,
        bg="black",
        fg="light blue",
        selectbackground="blue"
    )
    suggestions_listbox.pack(padx=10, pady=10)

    entry.bind("<KeyRelease>", on_key_release)

    root.mainloop()
