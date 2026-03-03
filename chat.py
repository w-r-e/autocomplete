import heapq
import kagglehub
from kagglehub import KaggleDatasetAdapter

class TrieNode:
    __slots__ = ("children", "is_end", "weight", "max_weight")

    def __init__(self):
        self.children = {}        # char -> TrieNode
        self.is_end = False       # True if node represents a complete word
        self.weight = 0           # weight of word if is_end == True
        self.max_weight = 0       # maximum weight in this subtree


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, weight: int):
        """
        Insert a word with a given weight.
        """
        node = self.root
        node.max_weight = max(node.max_weight, weight)

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.max_weight = max(node.max_weight, weight)

        node.is_end = True
        node.weight = weight

    def search(self, word: str) -> bool:
        """
        Return True if the word exists in the trie.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def find_prefix_node(self, prefix: str):
        """
        Return the node corresponding to the prefix,
        or None if prefix does not exist.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def autocomplete(self, prefix: str, k: int = 5):
        """
        Return top-k words starting with prefix,
        ordered by highest weight.
        """
        start_node = self.find_prefix_node(prefix)
        if not start_node:
            return []

        heap = [(-start_node.max_weight, prefix, start_node)]
        results = []

        while heap and len(results) < k:
            _, current_word, node = heapq.heappop(heap)

            if node.is_end:
                results.append((current_word, node.weight))

            for char, child in node.children.items():
                heapq.heappush(
                    heap,
                    (-child.max_weight, current_word + char, child)
                )

        return results

    @classmethod
    def from_dataframe(cls, df):
        file_path = "unigram_freq.csv"
        trie = cls

        # Load the latest version
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "rtatman/english-word-frequency",
            file_path,
            # Provide any additional arguments like 
            # sql_query or pandas_kwargs. See the 
            # documenation for more information:
            # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
        )

        # Optional: sort by descending weight for slightly better heap behavior
        df_sorted = df.sort_values("count", ascending=False)

        for word, count in zip(df_sorted["word"], df_sorted["count"]):
            trie.insert(str(word), int(count))

        return trie
    
