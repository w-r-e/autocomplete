from trie import Trie, TrieNode
from tkinter import Tk, Entry, Listbox, END

# TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: Hey Dana... I will be using comments to explain my code! pls text me if theres any bit u dont get
# TODO: What I need from you for the DAWG class is to update the max_weights, since my code doesnt do that yet
# TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class DAWGNode(TrieNode):
    """Class that represents a Node in the Directed Acyclic Word Graph (DAWG).

    Inherited Attributes:
        - children: A defaultdict containing the TrieNode children connected to this node.
        - is_end: A boolean signifying wheter the node represents the end of a word.
        - weight: The associated frequency of a word. Equals 0 unless is_end is true.
        - max_weight: The maximum weight of all the children.

    Instance Attributes:
        - signature: The unique identifier for this node, used to for merging in the DAWG
                     minimization algorithm.
    """
    __slots__ = ("signature",)

    def __init__(self):
        super().__init__()  # Inherits the stuff from the TrieNode class
        self.signature = None

    def gen_signature(self):
        """
        Creates a unique signature for this node: (is_end, weight, sorted children signatures)
        Used to detect identical subtrees for merging.
        Assumes the children ahve the correct signature as this function will be used in a post order traversal.
        """

        # Generates the signature... Just used so that we can compare nodes and then say "HEY! these two are the same"
        # This way we can merge redundant nodes. EX: for "cats" and "bats", clearly both "t"s have the same children
        # are both not endings of words, and have the same weight of 0 (cause word weights are stored at the end)
        # So we can just merge em!
        # Note: We dont merge the "s"s in this example. This is because they both store different weights, so merging
        # would make it so that merging would combine the weights, which means that they would be considered equually
        # likely event if they aren't.

        if self.is_end:
            # Word-end nodes are never merged
            self.signature = (self.is_end,)
        else:
            # Non-end nodes can be merged if children are identical
            children_sig = tuple(sorted((char, child.signature)) for char, child in self.children.items())
            self.signature = (self.is_end, children_sig)


class DAWG:
    """
    Class that represents a Directed Acylic Word Graph (DAWG).

    Instance Attributes:
        - root: The root node, all its children represent the starting letters of words.
        - register: A mapping between a DAWGNode and its corresponding signature.
    """
    root: DAWGNode
    register: dict[tuple, DAWGNode]
    # TODO: You can see in my implementation, I fail to update max_weights, because now that we merge nodes, there are new children

    def __init__(self, trie: Trie):
        self.root = self._copy_node(trie.root)  # Copies the entire Trie Down First
        self.register = {}
        self.root = self._minimize(self.root)  # Then minimizes, i.e. combined nodes that are the same.

    def _copy_node(self, node: TrieNode) -> DAWGNode:
        """Recursively copy a TrieNode into a DAWGNode"""
        new_node = DAWGNode()  # Set up a node
        new_node.is_end = node.is_end
        new_node.weight = node.weight
        new_node.max_weight = node.max_weight  # These 3 lines just copy the properties of the node
        for char, child in node.children.items():
            new_node.children[char] = self._copy_node(child)  # Makes you copy all the children and their children...
        return new_node

    def _minimize(self, node: DAWGNode):
        """Recursively minimize the node's subtrees into the registry by traversing post-order"""
        for char, child in list(node.children.items()):
            node.children[char] = self._minimize(child)  # This traverses to the bottom of the Trie and begins working

        node.gen_signature()  # Generates the signature of a node. We do this here because the signature is only right
        # if we make sure all the children signatures are right, that why its here and not in the DAWGNode class.

        if not node.is_end and node.signature in self.register:  # If we've already seen this node before
            return self.register[node.signature]  # Use the old exisitng node and ignore the current one
        else:
            self.register[node.signature] = node  # Otherwise it's a new node so we save it to the register and continue
            return node

    def search(self, prefix: str, k: int = 10) -> list[str]:
        """Search the minimized DAWG (top-k suggestions)"""
        # This one works the same as the Trie
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        suggestions = []
        self._find_suggestions(node, prefix, suggestions, k, -1)
        return [word for word, _ in suggestions]

    def _find_suggestions(self, node: DAWGNode, prefix: str, suggestions: list, k: int, min_weight: int):
        # This one works the same as the Trie
        """Recursively traverse the DAWG to get top-k suggestions"""
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

    # registry contians the unqiue subtrees already processed, signature: node where signature is the unique marker
    # need to minimise:
    # merge two identical subtrees ->:
    # go to all the children, compute signature, check if it exists in the registry, merge,
    # update max weight so post order processing

# TODO: PLEASE IGNORE THIS ITS A WORK IN FUCKING PROGRESS
# class IncrementalDAWG:
#     root: DAWGNode
#     prev_word: str
#     unchecked: list
#     register: dict
#
#     def __init__(self):
#         self.root = DAWGNode()
#         self.prev_word = ""
#         self.unchecked = []
#         self.register = {}
#
#     def insert(self, word, weight):
#         if word < self.prev_word:
#             raise ValueError("Words must be inserted in lexicographic order")
#
#         # First this bit finds the common prefix yk like if the most recent word was "carp" and the new one is "cat"
#         # it compares the characters to see which ones are common, and stops when it finds a difference
#         # Here for carp and cat it'll compare until it hits the 3rd cahracter, see t =/= r and, then we have "ca"
#         # which is the correct common prefix. Techincally we only store its position,
#         common = 0
#         for a, b in zip(word, self.prev_word):
#             if a != b:
#                 break
#             common += 1
#
#         self._minimize(common)
#
#         node = self.root
#         for char in word[:common]:
#             node = node.children[char]
#
#         for char in word[common:]:
#             new = DAWGNode()
#             node.children[char] = new
#             self.unchecked.append((node, char, new))
#             node = new
#
#         node.is_end = True
#         node.weight = weight
#         self.previous_word = word
#
#     def _minimize(self, down_to):
#         for i in range(len(self.unchecked) - 1, down_to - 1, -1):
#             parent, char, child = self.unchecked[i]
#             sig = child.signature()
#
#             if sig in self.register:
#                 parent.children[char] = self.register[sig]
#             else:
#                 self.register[sig] = child
#
#             self.unchecked.pop()


def update_suggestions(dawg, entry, suggestions_listbox):
    """Updates the suggestions based on the changes from the recent user entry."""
    prefix = entry.get()
    if not prefix:
        suggestions_listbox.delete(0, END)
        return
    suggestions = dawg.search(prefix, k=10)
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

    dawg = DAWG(trie)
    root = Tk()
    root.config(bg="dark grey")
    root.title("Autocomplete App")

    entry = Entry(root)
    entry.pack(padx=10, pady=10)

    suggestions_listbox = Listbox(root, width=50, bg="black", fg="light blue", selectbackground="blue")
    suggestions_listbox.pack(padx=10, pady=10)

    entry.bind("<KeyRelease>", lambda event: update_suggestions(dawg, entry, suggestions_listbox))
    root.mainloop()


if __name__ == "__main__":
    main()
