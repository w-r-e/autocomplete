from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG
from tkinter import Tk, Entry, Listbox, Button, Frame, END
import visualizations

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

if __name__ == "__main__":
    words = load_words("unigram_freq.csv")

    # Pre-build all structures
    trie = trie_setup(words)
    visualizations.export_tree(trie, "trie.txt")
    radix = radix_tree_setup(words)
    visualizations.export_tree(radix, "radix.txt")
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
    visualizations.visualize_dawg(dawg)