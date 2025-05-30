from parse_tree import ParseTreeNode
import re


class DPDA:
    def __init__(self, trf, input_tokens, start_symbol, terminals):
        self.head = 0
        self.trf = trf
        self.state = "q0"

        self.input = list(input_tokens)
        if not self.input or self.input[-1] != "$":
            self.input.append("$")

        self.root_node = ParseTreeNode(start_symbol)
        self.stack = [("Z", None), (start_symbol, self.root_node)]
        self._terminals = terminals

    def _print_status(self):
        current_input_display = " ".join(self.input[self.head :])
        stack_symbols_display = "".join([s for s, _ in self.stack])
        print(
            f"{current_input_display:20s} ['{stack_symbols_display}'] {self.state:5s}"
        )

    def run(self):
        print("\n--- Running DPDA (with Parse Tree Building) ---")
        self._print_status()

        while True:
            current_input_symbol = self.input[self.head]

            if not self.stack:
                print("Rejected: Stack is empty prematurely.")
                return None

            stack_top_symbol, stack_top_node = self.stack[-1]

            if stack_top_symbol == "Z" and current_input_symbol == "$":
                print("Accepted")
                return self.root_node

            if stack_top_symbol in self._terminals and (
                stack_top_symbol == current_input_symbol
                or re.match(stack_top_symbol, current_input_symbol)
            ):
                self.stack.pop()
                stack_top_node.token = current_input_symbol
                self.head += 1
                self._print_status()
                continue

            transition_key = (self.state, current_input_symbol, stack_top_symbol)
            next_state, push_string_rhs = self.trf.get(transition_key, (None, None))
            print("\n\nNice one")
            print(self.trf.get(transition_key, (None, None)))
            temp_dict = {
                key: value
                for key, value in self.trf.items()
                if re.fullmatch(key[1], current_input_symbol)
                and key[0] == self.state
                and key[2] == stack_top_symbol
            }
            if next_state is None and len(temp_dict) != 0:
                print("does not work like normal , probably regex")
                next_state, push_string_rhs = list(temp_dict.values())[0]
            print(
                {
                    key: value
                    for key, value in self.trf.items()
                    if re.fullmatch(key[1], current_input_symbol)
                    and key[0] == self.state
                    and key[2] == stack_top_symbol
                }
            )

            if next_state is not None:
                popped_symbol, popped_node = self.stack.pop()

                if push_string_rhs != "eps":
                    rhs_symbols = push_string_rhs.split()

                    for symbol in reversed(rhs_symbols):
                        child_node = ParseTreeNode(symbol)
                        popped_node.add_child(child_node)
                        self.stack.append((symbol, child_node))

                self._print_status()
            else:
                print(
                    f"Rejected: No valid transition for ({self.state}, {current_input_symbol}, {stack_top_symbol})."
                )
                return None


def load_transitions(filename):
    trf = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 5:
                print(f"Warning: Skipping malformed transition line: {line}")
                continue
            current_state, input_symbol, pop_symbol, next_state, push_string = parts
            trf[(current_state, input_symbol, pop_symbol)] = (next_state, push_string)
    return trf
