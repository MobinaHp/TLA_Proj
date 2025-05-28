from parse_tree import ParseTreeNode
class DPDA:
    """
    Represents a Deterministic Pushdown Automaton (DPDA) for LL(1) parsing
    with parse tree generation capabilities.

    Attributes:
        head (int): Current position of the input head.
        trf (dict): Transition function dictionary. Keys are (state, input_symbol, stack_top_symbol),
                    values are (next_state, push_string_rhs).
        state (str): Current state of the DPDA (fixed to 'q0' for LL(1) parsing).
        input (list): List of input tokens to be parsed.
        stack (list): The DPDA's stack, now storing (grammar_symbol, ParseTreeNode) tuples.
        _terminals (set): A reference to the CFG's terminal set.
        root_node (ParseTreeNode): The root of the parse tree.
    """
    def __init__(self, trf, input_tokens, start_symbol, terminals):
        self.head = 0
        self.trf = trf
        self.state = 'q0' # LL(1) parsers typically operate in a single state 'q0'
        
        # Ensure input_tokens is always a list and ends with '$'
        self.input = list(input_tokens)
        if not self.input or self.input[-1] != '$':
            # Add end-of-input marker if not present. This is crucial for parsing.
            self.input.append('$') 
        
        # Initialize the root node for the parse tree
        self.root_node = ParseTreeNode(start_symbol)
        # Stack now holds (grammar_symbol, parse_tree_node) tuples
        # Initial stack configuration: Bottom marker 'Z' and Start Symbol's node
        self.stack = [('Z', None), (start_symbol, self.root_node)]
        self._terminals = terminals # Store the terminals set

    def _print_status(self):
        """
        Prints the current state of the DPDA (remaining input, stack symbols, and current state).
        """
        current_input_display = ' '.join(self.input[self.head:])
        # Only display the grammar symbols from the stack for readability
        stack_symbols_display = ''.join([s for s, _ in self.stack])
        print(f'{current_input_display:20s} [\'{stack_symbols_display}\'] {self.state:5s}')

    def run(self):
        """
        Executes the DPDA to parse the input string and build a parse tree.
        Returns the root of the parse tree if accepted, otherwise None.
        """
        print("\n--- Running DPDA (with Parse Tree Building) ---")
        self._print_status()

        while True:
            current_input_symbol = self.input[self.head]
            
            if not self.stack:
                print("Rejected: Stack is empty prematurely.")
                return None

            # Get the top of the stack: (grammar_symbol, associated_node)
            stack_top_symbol, stack_top_node = self.stack[-1]

            # 1. Acceptance Condition: Input exhausted and only 'Z' (bottom marker) left on stack
            if stack_top_symbol == 'Z' and current_input_symbol == '$':
                print("Accepted")
                return self.root_node # Return the completed parse tree root

            # 2. Terminal Matching (Shift Action): If stack top is a terminal and matches current input
            if stack_top_symbol in self._terminals and stack_top_symbol == current_input_symbol: 
                self.stack.pop() # Pop the matching terminal and its node
                stack_top_node.token = current_input_symbol # Assign the actual token value to the node
                self.head += 1 # Consume the input symbol
                self._print_status()
                continue

            # 3. Non-terminal Expansion (Reduce Action): If stack top is a non-terminal
            # Look up the parsing table (represented by self.trf) for the appropriate production.
            transition_key = (self.state, current_input_symbol, stack_top_symbol)
            next_state, push_string_rhs = self.trf.get(transition_key, (None, None))

            if next_state is not None:
                # Pop the non-terminal and its associated node from the stack
                popped_symbol, popped_node = self.stack.pop()

                if push_string_rhs != 'eps': # If it's not an epsilon production
                    # Split the RHS string into individual symbols (e.g., 'T E_prime' -> ['T', 'E_prime'])
                    rhs_symbols = push_string_rhs.split()
                    
                    # Push symbols onto the stack in reverse order of the RHS
                    # Create a new ParseTreeNode for each symbol and add it as a child
                    for symbol in reversed(rhs_symbols):
                        child_node = ParseTreeNode(symbol)
                        popped_node.add_child(child_node) # Add this new node as a child to the popped_node
                        self.stack.append((symbol, child_node)) # Push (symbol, node) tuple onto DPDA stack
                
                # State remains 'q0'. Input head is NOT advanced.
                self._print_status()
            else:
                # No valid transition found - syntax error.
                print(f"Rejected: No valid transition for ({self.state}, {current_input_symbol}, {stack_top_symbol}).")
                return None # Indicate parsing failure

def load_transitions(filename):
    """
    Loads DPDA transitions from a file.
    (This function remains unchanged from previous versions)
    """
    trf = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 5:
                print(f"Warning: Skipping malformed transition line: {line}")
                continue
            current_state, input_symbol, pop_symbol, next_state, push_string = parts
            trf[(current_state, input_symbol, pop_symbol)] = (next_state, push_string)
    return trf
