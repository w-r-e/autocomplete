"""Main Function

Module Description
==================

Includes all functions and uses different files to visualize the autocomplete by mimicking a search
engine through the tkinter library. The user can use this interactive visualization to see a
demonstration of how an autocomplete algorithm would work and the efficiency of them.

Instructions
=============

All libraries used are part of the Python standard library, so no external library installation is required.
The two datasets used by the program are contained in the compressed folder datasets.zip uploaded to
MarkUs. Please unzip the folder and move the two dataset files to the same folder as the other program
files. Running this file starts the graphical interface described in Graphical Interface, including the button
to generate visualizations as described in Structural Visualization and NetworkX.

"""
import sys
import time
from trie import Trie
from radix_tree import RadixTree
from dawg import IncrementalDAWG, DAWGNode
import visualizations
from typing import Any
from tkinter import Tk, Entry, Listbox, Button, Frame, Label, END


def load_words(filename) -> list[Any]:
    """Method used to load words from a local CSV."""
    words = []

    with open(filename, 'r') as f:
        for line in f:
            word, count = line.strip().split(',', 1)
            words.append((word, int(count)))
    return sorted(words, key=lambda x: x[0])


def trie_setup(words: list[Any]) -> Trie:
    """Sets up the Trie with the given words and their weights."""
    t = Trie()
    for word, count in words:
        t.insert(word, count)
    return t


def radix_tree_setup(words: list[Any]) -> RadixTree:
    """Sets up the RadixTree with the given words and their weights."""
    rt = RadixTree()
    for word, count in words:
        rt.insert(word, count)
    return rt


def dawg_setup(words: list[Any]) -> IncrementalDAWG:
    """Sets up the IncrementalDAWG with the given words and their weights."""
    DAWGNode._next_node = 0
    dawg = IncrementalDAWG()
    for word, count in words:
        dawg.insert(word, count)
    return dawg


def update_suggestions(structure: Trie | RadixTree | IncrementalDAWG, entry: Entry, listbox: Listbox) -> None:
    """Updates the suggestions listbox using whichever structure is currently active."""
    prefix = entry.get()
    listbox.delete(0, END)
    if not prefix:
        return
    for suggestion in structure.search(prefix, k=10):
        listbox.insert(END, suggestion)

if __name__ == "__main__":
    sys.setrecursionlimit(2950)
    print("Loading datasets...")
    words333333 = load_words("unigram_freq.csv")
    words955213 = load_words("en_full.txt")
    print("Datasets loaded successfully.")

    # Building, timing, and recording memory usage for each structure and dataset
    print("Building structures...")
    # Trie with 333,333 word dataset
    trie_setup_time_words333333 = time.time()
    trie_words333333 = trie_setup(words333333)
    trie_setup_time_words333333 = time.time() - trie_setup_time_words333333
    trie_space_words333333 = trie_words333333.get_total_memory()

    # Trie with 955,213 word dataset
    trie_setup_time_words955213 = time.time()
    trie_words955213 = trie_setup(words955213)
    trie_setup_time_words955213 = time.time() - trie_setup_time_words955213
    trie_space_words955213 = trie_words955213.get_total_memory()
    # visualizations.export_tree(trie_words333333, "trie.txt")

    # Radix Tree with 333,333 word dataset
    radix_setup_time_words333333 = time.time()
    radix_words333333 = radix_tree_setup(words333333)
    radix_setup_time_words333333 = time.time() - radix_setup_time_words333333
    radix_space_words333333 = radix_words333333.get_total_memory()

    # Radix Tree with 955,213 word dataset
    radix_setup_time_words955213 = time.time()
    radix_words955213 = radix_tree_setup(words955213)
    radix_setup_time_words955213 = time.time() - radix_setup_time_words955213
    radix_space_words955213 = radix_words955213.get_total_memory()
    # visualizations.export_tree(radix_words333333, "radix.txt")

    # DAWG with 333,333 word dataset
    dawg_setup_time_words333333 = time.time()
    dawg_words333333 = dawg_setup(words333333)
    dawg_setup_time_words333333 = time.time() - dawg_setup_time_words333333
    dawg_space_words333333 = dawg_words333333.get_total_memory()

    # DAWG with 955,213 word dataset
    dawg_setup_time_words955213 = time.time()
    dawg_words955213 = dawg_setup(words955213)
    dawg_setup_time_words955213 = time.time() - dawg_setup_time_words955213
    dawg_space_words955213 = dawg_words955213.get_total_memory()

    print("Structures built successfully.")

    # Default structure
    current_structure = {"obj": trie_words333333, "name": "trie", "dataset": "333,333 words", "time": trie_setup_time_words333333, "space": trie_space_words333333}

    # Set up the GUI
    root = Tk()
    root.config(bg="dark grey")
    root.title("Autocomplete App (trie, 333,333 words)")

    info_label = Label(root, text="", bg="dark grey", fg="black")
    info_label.pack(pady=10)

    def update_info_labels():
        """Updates the info label with the current structure's setup time and memory usage."""
        text = (f"{current_structure['name']} setup time: {current_structure['time']:.4f} seconds | "
                f"memory: {current_structure['space'] / (1024 ** 2):.4f} MB")
        info_label.config(text=text)

    def switch_structure(structure_name, dataset_name):
        """Switches the current structure and dataset, updating the info label and clearing suggestions."""
        current_structure["name"] = structure_name
        current_structure["dataset"] = dataset_name
        root.title(f"Autocomplete App ({structure_name}, {dataset_name})")
        if dataset_name == "333,333 words":
            if structure_name == "trie":
                current_structure["obj"] = trie_words333333
                current_structure["time"] = trie_setup_time_words333333
                current_structure["space"] = trie_space_words333333

            elif structure_name == "radix":
                current_structure["obj"] = radix_words333333
                current_structure["time"] = radix_setup_time_words333333
                current_structure["space"] = radix_space_words333333

            else:
                current_structure["obj"] = dawg_words333333
                current_structure["time"] = dawg_setup_time_words333333
                current_structure["space"] = dawg_space_words333333
        else:
            if structure_name == "trie":
                current_structure["obj"] = trie_words955213
                current_structure["time"] = trie_setup_time_words955213
                current_structure["space"] = trie_space_words955213

            elif structure_name == "radix":
                current_structure["obj"] = radix_words955213
                current_structure["time"] = radix_setup_time_words955213
                current_structure["space"] = radix_space_words955213

            else:
                current_structure["obj"] = dawg_words955213
                current_structure["time"] = dawg_setup_time_words955213
                current_structure["space"] = dawg_space_words955213

        # Clear word and suggestions when switching
        suggestions_listbox.delete(0, END)
        entry.delete(0, END)

        # Update entry box with setup time
        update_info_labels()

    def on_key_release(event):
        """Handles key release events in the entry box, updating suggestions and timing the search."""
        suggestion_time = time.time()
        update_suggestions(current_structure["obj"], entry, suggestions_listbox)
        suggestion_time = time.time() - suggestion_time
        text = (f"{current_structure['name']} setup time: {current_structure['time']:.4f} seconds | "
                f"memory: {current_structure['space'] / (1024 ** 2):.4f} MB\n"
                f"suggestion time: {suggestion_time:.4f} seconds")
        info_label.config(text=text)

    def export_visualization(entry: str):
        """Exports a visualization of the current structure.
        For the Trie and Radix Tree, it exports a text file with the tree structure.
        For the DAWG, produces a graph using NetworkX."""
        if current_structure["name"] == "trie" or current_structure["name"] == "radix":
            visualizations.export_tree(current_structure["obj"], "trie.txt")
        elif current_structure["name"] == "dawg":
            visualizations.visualize_dawg(current_structure["obj"], entry, 10)

    # Structure buttons
    structure_button_frame = Frame(root, bg="dark grey")
    structure_button_frame.pack(pady=5)
    Button(structure_button_frame, text="Trie", command=lambda: switch_structure("trie", current_structure["dataset"])).pack(side="left", padx=5)
    Button(structure_button_frame, text="Radix", command=lambda: switch_structure("radix", current_structure["dataset"])).pack(side="left", padx=5)
    Button(structure_button_frame, text="DAWG", command=lambda: switch_structure("dawg", current_structure["dataset"])).pack(side="left", padx=5)

    # Dataset buttons
    dataset_button_frame = Frame(root, bg="dark grey")
    dataset_button_frame.pack(pady=5)
    Button(dataset_button_frame, text="333,333 words", command=lambda: switch_structure(current_structure["name"], "333,333 words")).pack(side="left", padx=5)
    Button(dataset_button_frame, text="955,213 words", command=lambda: switch_structure(current_structure["name"], "955,213 words")).pack(side="left", padx=5)
    
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

    update_info_labels()

    entry.bind("<KeyRelease>", on_key_release)

    visualizations_button_frame = Frame(root, bg="dark grey")
    visualizations_button_frame.pack(pady=5)
    Button(visualizations_button_frame, text="Visualize structure", command=lambda: export_visualization(entry.get())).pack(side="left", padx=5)

    root.mainloop()