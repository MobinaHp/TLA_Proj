class CFG:
    def __init__(self, filepath):
        self.productions = {}         
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self._read_grammar(filepath)

    def _read_grammar(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or '->' not in line:
                    continue

                left, right = line.split('->')
                left = left.strip()
                rights = [r.strip().split() for r in right.strip().split('|')]

                if self.start_symbol is None:
                    self.start_symbol = left

                self.non_terminals.add(left)

                if left not in self.productions:
                    self.productions[left] = []

                for prod in rights:
                    self.productions[left].append(prod)

        all_symbols = set()
        for rhs_list in self.productions.values():
            for rhs in rhs_list:
                all_symbols.update(rhs)
        
        self.terminals = all_symbols - self.non_terminals - {'ε'}

    def display(self):
        print(f"Start Symbol: {self.start_symbol}")
        print("Non-terminals:", self.non_terminals)
        print("Terminals:", self.terminals)
        print("Productions:")
        for nt, rules in self.productions.items():
            for rule in rules:
                print(f"  {nt} -> {' '.join(rule)}")


if __name__ == "__main__":
    grammar = CFG("grammar.txt")
    grammar.display()

