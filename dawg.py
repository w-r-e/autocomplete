import sys

# TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: Hey Dana... I will be using comments to explain my code! pls text me if theres any bit u dont get
# TODO: What I need from you for the DAWG class is to update the max_weights, since my code doesnt do that yet
# TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class DAWGNode:
    """Class that represents a Node in the Directed Acyclic Word Graph (DAWG).

    Instance Attributes:
        - children: A dict containing the children connected to this node.
        - word_grave: A list containing all words that end at this node
        - is_end: A boolean signifying wheter the node represents the end of a word.
        - signature: The unique identifier for this node, used to for merging in the DAWG
                     minimization algorithm.
    """
    __slots__ = ("children", "word_grave", "is_end", "node_id",  "signature")
    _next_node: int = 0

    def __init__(self):
        self.children = {}
        self.word_grave = []
        self.is_end = False
        self.node_id = DAWGNode._next_node
        DAWGNode._next_node += 1
        self.signature = None

    def gen_signature(self):
        """
        Creates a unique signature for this node: (is_end, weight, sorted children signatures)
        Used to detect identical subtrees for merging.
        Assumes the children have the correct signature as this function will be used in a post order traversal.
        """

        # Generates the signature... Just used so that we can compare nodes and then say "HEY! these two are the same"
        # This way we can merge redundant nodes. EX: for "cats" and "bats", clearly both "t"s have the same children
        # are both not endings of words, and have the same weight of 0 (cause word weights are stored at the end)
        # So we can just merge em!
        # Note: We dont merge the "s"s in this example. This is because they both store different weights, so merging
        # would make it so that merging would combine the weights, which means that they would be considered equually
        # likely event if they aren't.

        # child.signature must already be computed
        # Works since we work post-order in the DAWG
        if self.is_end:
            self.signature = (True, self.node_id)  # Every end node is unique!
        else:
            child_items = []
            for ch, child in sorted(self.children.items()):
                if child.is_end:
                    child_items.append((ch, "end"))
                else:
                    child_items.append((ch, child.signature))
            self.signature = (False, tuple(child_items))
        return self.signature


class IncrementalDAWG:
    """
    Incremental construction of a Directed Acyclic Word Graph (DAWG).

    This class allows words to be inserted one at a time in !!!!lexicographical order!!!!,
    maintaining a minimal DAWG at all times. It is based on the algorithm by Daciuk et al. (2000).

    Instance Attributes:
        - root: The root node of the DAWG. All words are reachable from this node.
        - prev_word: The previously inserted word. Used to compute the common prefix
          between consecutive insertions.
        - unchecked: A stack of nodes representing the "unprocessed" part of the
          last inserted word. Each element is a tuple of (parent_node, character, child_node).
          These nodes may be merged during minimization.
        - register: A mapping from node signatures to DAWGNode instances. Used to detect
          identical subtrees for merging in order to maintain minimality.
    """
    root: DAWGNode
    prev_word: str
    unchecked: list[tuple[DAWGNode, str, DAWGNode]]
    register: dict

    def __init__(self):
        self.root = DAWGNode()
        self.prev_word = ""
        self.unchecked = []
        self.register = {}

    def insert(self, word, weight):
        """Inserts the characters of a word into the DAWG."""
        if word < self.prev_word:
            raise ValueError("Words must be inserted in lexicographic order")

        # First this bit finds the common prefix yk like if the most recent word was "carp" and the new one is "cat"
        # it compares the characters to see which ones are common, and stops when it finds a difference
        # Here for carp and cat it'll compare until it hits the 3rd character, see t =/= r and, then we have "ca"
        # which is the correct common prefix. Techincally we only store its position,
        common = 0
        for a, b in zip(word, self.prev_word):
            if a != b:
                break
            common += 1

        # Calls this to minimize the new nodes in the suffix, i.e. compare them with exisiting nodes and merge
        self._minimize_suffix(common)

        node = self.root
        for char in word[:common]:
            node = node.children[char]

        for char in word[common:]:
            new = DAWGNode()
            node.children[char] = new
            self.unchecked.append((node, char, new))
            node = new

        node.is_end = True
        node.word_grave.append((word, weight))
        self.prev_word = word

    def _minimize_suffix(self, down_to):
        """Recursivly minimises the suffix of a word"""
        for i in range(len(self.unchecked) - 1, down_to - 1, -1):
            parent, char, child = self.unchecked[i]

            sig = child.gen_signature()

            if sig in self.register:
                stored = self.register[sig]
                parent.children[char] = stored

                if child.word_grave:
                    stored.word_grave.extend(child.word_grave)
                    child.word_grave = []

            else:
                self.register[sig] = child

            self.unchecked.pop()

    def search(self, prefix: str, k: int = 10) -> list[str]:
        """Return the top 10 words starting with prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        # Now collect all completions
        results = []
        self._collect(node, prefix, results)

        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in results[:k]]

    def _collect(self, node: DAWGNode, path: str, results: list) -> None:
        """Recursively collects all words that have the prefix 'path'"""
        for word, weight in node.word_grave:
            # verify the word starts with our path :)
            if word.startswith(path):
                results.append((word, weight))

        # recurse into the children
        for ch, child in sorted(node.children.items()):
            self._collect(child, path + ch, results)

    def get_total_memory(self):
        """Calculate total memory usage of this DAWG."""
        seen = set()
        return self._measure(self.root, seen)

    def _measure(self, node, seen):
        """Recursive helper function to find the size of the node and all its children"""
        if node in seen:
            return 0
        seen.add(node)

        total = sys.getsizeof(node)
        total += sys.getsizeof(node.children)

        for char, child in node.children.items():
            total += sys.getsizeof(char)
            total += self._measure(child, seen)

        total += sys.getsizeof(node.word_grave)
        for word, weight in node.word_grave:
            total += sys.getsizeof(word) + sys.getsizeof(weight)

        return total

# THE MESS
# class DAWG:
#     """
#     Class that represents a Directed Acylic Word Graph (DAWG).
#
#     Instance Attributes:
#         - root: The root node, all its children represent the starting letters of words.
#         - register: A mapping between a DAWGNode and its corresponding signature.
#     """
#     root: DAWGNode
#     register: dict[tuple, DAWGNode]
#
#     def __init__(self, trie: Trie):
#         self.root = self._copy_node(trie.root)  # Copies the entire Trie Down First
#         self.register = {}
#         self.root = self._minimize(self.root)  # Then minimizes, i.e. combined nodes that are the same.
#
#     def _copy_node(self, node: TrieNode) -> DAWGNode:
#         """Recursively copy a TrieNode into a DAWGNode"""
#         new_node = DAWGNode()  # Set up a node
#         new_node.is_end = node.is_end
#         new_node.weight = node.weight
#         new_node.max_weight = node.max_weight  # These 3 lines just copy the properties of the node
#
#         for char, child in node.children.items():
#             new_node.children[char] = {self._copy_node(child)}
# Makes you copy all the children and their children...
#
#         return new_node
#
#     def _minimize(self, node: DAWGNode):
#         """Recursively minimize the node's subtrees into the registry by traversing post-order"""
#         # This traverses to the bottom of the Trie and begins working
#         for char, nodes in list(node.children.items()):
#             minimized_nodes = set()
#             for child in nodes:
#                 minimized = self._minimize(child)
#                 minimized_nodes.add(minimized)  # Set handles duplicates automatically
#             node.children[char] = minimized_nodes
#
#         node.gen_signature()  # Generates the signature of a node. We do this here because the signature is only right
#         # if we make sure all the children signatures are right, that why its here and not in the DAWGNode class.
#
#         if not node.is_end and node.signature in self.register:  # If we've already seen this node before
#             return self.register[node.signature]  # Use the old exisitng node and ignore the current one
#         else:
#             self.register[node.signature] = node
# Otherwise it's a new node so we save it to the register and continue
#             return node
#
#     def search(self, prefix: str, k: int = 10) -> list[str]:
#         """Search the minimized DAWG (top-k suggestions)"""
#         # Start with a set containing the root
#         current_nodes = {self.root}
#
#         for char in prefix:
#             next_nodes = set()
#             for node in current_nodes:
#                 if char in node.children:
#                     # Add ALL possible nodes for this character
#                     next_nodes.update(node.children[char])
#
#             if not next_nodes:  # No valid paths
#                 return []
#             current_nodes = next_nodes
#
#         # Now collect suggestions from all possible paths
#         suggestions = []
#
#         for node in current_nodes:
#             self._find_suggestions(node, prefix, suggestions, k, -1, set())
#
#         # sort final suggestions
#         suggestions.sort(key=lambda x: x[1], reverse=True)
#         return [word for word, _ in suggestions]
#
#     def _find_suggestions(self, node: DAWGNode, prefix: str, suggestions: list,
#                           k: int, min_weight: int, seen_words: set):
#         """Recursively traverse the DAWG to get top-k suggestions"""
#         if node.is_end and prefix not in seen_words:
#             seen_words.add(prefix)
#             suggestions.append((prefix, node.weight))
#             suggestions.sort(key=lambda x: x[1], reverse=True)
#             if len(suggestions) > k:
#                 suggestions.pop()
#             if len(suggestions) == k:
#                 min_weight = suggestions[-1][1]
#
#         for char, child_nodes in node.children.items():
#             for child in child_nodes:
#                 if child.max_weight <= min_weight:
#                     continue
#                 self._find_suggestions(child, prefix + char, suggestions, k, min_weight, seen_words)
#
#     # registry contians the unqiue subtrees already processed, signature: node where signature is the unique marker
#     # need to minimise:
#     # merge two identical subtrees ->:
#     # go to all the children, compute signature, check if it exists in the registry, merge,
#     # update max weight so post order processing
