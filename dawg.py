import sys

class DAWGNode:
    """Class that represents a Node in the Directed Acyclic Word Graph (DAWG).

    Instance Attributes:
        - children: A dict containing the children connected to this node.
        - word_grave: A list containing all words that end at this node
        - is_end: A boolean signifying whether the node represents the end of a word.
        - node_id: An integer that denotes a unique identifier for this node.
        - signature: The unique identifier for this node, used to for merging in the DAWG.
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
        
        if self.is_end:
            self.signature = (True, self.node_id)  
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

    This class allows words to be inserted one at a time in lexicographical order,
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

        common = 0
        for a, b in zip(word, self.prev_word):
            if a != b:
                break
            common += 1

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

        results = []
        self._collect(node, prefix, results)

        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in results[:k]]

    def _collect(self, node: DAWGNode, path: str, results: list) -> None:
        """Recursively collects all words that have the prefix 'path'"""
        for word, weight in node.word_grave:
            if word.startswith(path):
                results.append((word, weight))

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
