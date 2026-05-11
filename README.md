# Time and Space Efficient Autocomplete
## Overview

This project explores the design and implementation of efficient query auto-completion (QAC) systems using three different data structures:

Standard Trie (Prefix Tree)
Radix Tree (Patricia Trie)
Directed Acyclic Word Graph (DAWG)

The goal is to compare these structures in terms of time efficiency (setup and query speed) and space efficiency (memory usage), using real-world word-frequency datasets.

An interactive graphical interface allows users to test and visualize autocomplete suggestions in real time.

## Features
- Real-time autocomplete suggestions as you type
- Switch between Trie, Radix Tree, and DAWG implementations

## Displays:
- Setup time
- Query time
- Memory usage
- Pre-generated performance graphs (memory, setup time, query time)
- Structural visualization:
- ASCII trees for Trie and Radix Tree
- Network-based graph visualization for DAWG

## Data Structures
1. Standard Trie
Fast lookup: O(m) where m is prefix length
Simple implementation
High memory usage due to many pointers
2. Radix Tree
Path-compressed Trie
Reduces memory by merging single-child paths
Maintains O(m) lookup
3. DAWG
Merges both prefixes and suffixes
Extremely memory efficient
More complex to implement
Requires lexicographically sorted input
Datasets

This project uses two word-frequency datasets:

English Word Frequency (2017)
~333,000 words
Derived from Google Web Trillion Word Corpus
en_full Dataset (2016)
~955,000 words
Derived from OpenSubtitles corpora

⚠️ Both datasets are included in datasets.zip.

## Installation
1. Clone the repository
```
git clone <repo-url>
cd <repo-folder>
```
2. Install dependencies based on requirements.txt
3. Unzip the dataset
4. Move dataset files into the project root directory.

## Running the Program

Type into the input box to get autocomplete suggestions
Select the Data structure (Trie / Radix Tree / DAWG)
Will display: 
- Suggestions ranked by frequency
- Query time per keystroke
- Memory and setup stats
- Graphs and Benchmarking

Performance graphs are pre-generated and included as HTML files.
To regenerate them (optional), run grapher.py.
⚠️ Note: This may take up to 20 minutes on large datasets.

Use DAWG for memory efficiency
Use Trie for fastest setup
Use Radix Tree for balanced performance

## Project Structure
├── main.py              # GUI entry point
├── trie.py              # Standard Trie implementation
├── radix_tree.py        # Radix Tree implementation
├── dawg.py              # DAWG implementation
├── grapher.py           # Benchmarking and graph generation
├── datasets.zip         # Word-frequency datasets
├── requirements.txt     # Dependencies
├── *.html               # Pre-generated graphs

## Limitations
Dataset contains mostly unique weights, limiting DAWG compression
Memory measurements are approximate (sys.getsizeof)
DAWG implementation is complex and harder to modify dynamically
Full graph visualization is not feasible for large datasets


## Future Work
Use datasets with duplicate weights to improve DAWG compression
Support dynamic updates (insert/delete)
Explore hybrid structures (Radix + DAWG)
Benchmark non-English datasets
Parallelize DAWG construction

## Authors
Liam Evans
Dana Lee
Kyra Park
Shiv Rajeev
