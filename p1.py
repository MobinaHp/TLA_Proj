class Grammar:
    def __init__(self, filename):
        self.start_symbol = None
        self.non_terminals = set()
        self.terminals = set()
        self.productions = {}

        self.read_grammar(filename)

    def read_grammar(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        for idx, line in enumerate(lines):
            # تقسیم سمت چپ و راست قاعده تولید
            if '->' not in line:
                raise ValueError(f"Invalid grammar line: {line}")
            left, right = line.split('->')
            left = left.strip()
            self.non_terminals.add(left)
            if idx == 0:
                self.start_symbol = left

            # تقسیم سمت راست به قواعد جداگانه با '|'
            right_parts = right.strip().split('|')
            productions = []
            for part in right_parts:
                symbols = part.strip().split()
                productions.append(symbols)
                for symbol in symbols:
                    if not symbol.isupper() and symbol != 'ε' and symbol not in self.non_terminals:
                        self.terminals.add(symbol)

            if left not in self.productions:
                self.productions[left] = []
            self.productions[left].extend(productions)

    def show(self):
        print("Start Symbol:", self.start_symbol)
        print("Non-terminals:", self.non_terminals)
        print("Terminals:", self.terminals)
        print("Productions:")
        for head, rules in self.productions.items():
            for rule in rules:
                print(f"  {head} -> {' '.join(rule)}")


# 🧪 استفاده:
if __name__ == "__main__":
    grammar = Grammar("grammar.txt")
    grammar.show()
