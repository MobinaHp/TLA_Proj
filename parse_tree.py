class ParseTreeNode:
    def __init__(self, symbol, token=None):
        self.symbol = symbol  # Grammar symbol (e.g., 'E', 'id', '+')
        self.children = []    # List of child ParseTreeNode objects
        self.token = token    # For terminal nodes, the actual input token (e.g., 'id', '123')

    def add_child(self, child_node):
        self.children.insert(0, child_node) # Insert at beginning to maintain left-to-right order

    def __repr__(self):
        return f"Node({self.symbol}{f':{self.token}' if self.token else ''})"

    def display(self, level=0):
        indent = "  " * level
        print(f"{indent}{self.symbol}{f' ({self.token})' if self.token else ''}")
        for child in self.children:
            child.display(level + 1)