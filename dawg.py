from black.trans import defaultdict


class DawgNode:
    is_end: bool
    weight: int
    max_weight: int
    children: defaultdict

class DAWG:
    root: DawgNode
    register: defaultdict

    # registry contians the unqiue subtrees already processed, signature: node where signature is the unique marker
    # need to minimise:
    # merge two identical subtrees ->:
    # go to all the children, compute signature, check if it exists in the registry, merge,
    # update max weight so post order processing
