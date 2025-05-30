class ParseTreeNode:
    def __init__(self, symbol, token=None):
        self.symbol = symbol
        self.children = []
        self.token = token

    def add_child(self, child_node):
        self.children.insert(0, child_node)

    def __repr__(self):
        return f"Node({self.symbol}{f':{self.token}' if self.token else ''})"

    def display(self, level=0):
        indent = "  " * level
        print(f"{indent}{self.symbol}{f' ({self.token})' if self.token else ''}")
        for child in self.children:
            child.display(level + 1)
