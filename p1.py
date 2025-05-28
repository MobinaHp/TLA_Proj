# cfg_parser.py

class CFG:
    def __init__(self, grammar_file):
        self.grammar_file = grammar_file
        self.start_symbol = None
        self.non_terminals = set()
        self.terminals = set()
        self.productions = {} # {NonTerminal: [[RHS_symbols_1], [RHS_symbols_2]]}
        self.first_sets = {}
        self.follow_sets = {}
        self._load_grammar()

    def _load_grammar(self):
        """
        Loads the grammar from the specified file.
        Expects format:
        START=S
        NON_TERMINALS=A,B,C
        TERMINALS=a,b,c,$,eps
        S -> A B C
        A -> a | eps
        B -> b B | eps
        C -> c
        """
        with open(self.grammar_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith("START="):
                    self.start_symbol = line.split('=')[1].strip()
                elif line.startswith("NON_TERMINALS="):
                    self.non_terminals.update(line.split('=')[1].split(','))
                elif line.startswith("TERMINALS="):
                    self.terminals.update(line.split('=')[1].split(','))
                    # Ensure 'eps' (epsilon) is treated as a special terminal in FIRST sets
                    # but not generally in input terminals, and '$' is also a special terminal.
                    if 'eps' not in self.terminals: # Make sure 'eps' is explicitly in terminals for FIRST calculations
                        self.terminals.add('eps')
                    if '$' not in self.terminals: # Make sure '$' is explicitly in terminals for FOLLOW calculations
                        self.terminals.add('$')
                else:
                    # Production rule: A -> B C D | E F
                    parts = line.split('->')
                    if len(parts) != 2:
                        raise ValueError(f"Invalid production format: {line}")
                    
                    head = parts[0].strip()
                    if head not in self.non_terminals:
                        raise ValueError(f"Production head '{head}' not declared as non-terminal.")
                    
                    bodies = [body.strip().split() for body in parts[1].split('|')]
                    self.productions.setdefault(head, []).extend(bodies)
        
        # Validate that start symbol is a non-terminal
        if self.start_symbol and self.start_symbol not in self.non_terminals:
            raise ValueError(f"Start symbol '{self.start_symbol}' not declared as a non-terminal.")

    def compute_first_sets(self):
        """
        Computes the FIRST set for all non-terminals and terminals.
        """
        # Initialize FIRST sets: terminals have themselves
        self.first_sets = {t: {t} for t in self.terminals}
        # Non-terminals start with empty sets
        for nt in self.non_terminals:
            self.first_sets[nt] = set()

        changed = True
        while changed:
            changed = False
            for head in self.non_terminals:
                for body in self.productions[head]:
                    # Rule 1: If X -> aα, then add 'a' to FIRST(X)
                    # Rule 2: If X -> ε, then add 'ε' to FIRST(X)
                    # Rule 3: If X -> Y1 Y2 ... Yk
                    #         Add FIRST(Y1) \ {ε} to FIRST(X)
                    #         If ε is in FIRST(Y1), add FIRST(Y2) \ {ε} to FIRST(X)
                    #         ...
                    #         If ε is in all FIRST(Yi) for i=1 to k, then add ε to FIRST(X)
                    
                    all_symbols_derive_epsilon = True
                    for symbol in body:
                        # Ensure symbol has an entry in first_sets
                        if symbol not in self.first_sets:
                            # If it's a terminal not yet in first_sets (e.g., if grammar has error)
                            # or if it's a non-terminal not yet initialized, handle gracefully.
                            # For well-formed grammars, this case shouldn't happen.
                            self.first_sets[symbol] = {symbol} if symbol in self.terminals else set()

                        # Add FIRST(symbol) (excluding epsilon) to FIRST(head)
                        old_size = len(self.first_sets[head])
                        self.first_sets[head].update(self.first_sets[symbol] - {'eps'})
                        if len(self.first_sets[head]) != old_size:
                            changed = True

                        # If current symbol doesn't derive epsilon, stop looking at next symbols
                        if 'eps' not in self.first_sets[symbol]:
                            all_symbols_derive_epsilon = False
                            break
                    
                    # If all symbols in the body derive epsilon, then head can also derive epsilon
                    if all_symbols_derive_epsilon and 'eps' not in self.first_sets[head]:
                        self.first_sets[head].add('eps')
                        changed = True

    def compute_follow_sets(self):
        """
        Computes the FOLLOW set for all non-terminals.
        Requires FIRST sets to be computed first.
        """
        if not self.first_sets:
            self.compute_first_sets() # Ensure FIRST sets are available

        # Initialize FOLLOW sets: empty for all non-terminals
        self.follow_sets = {nt: set() for nt in self.non_terminals}
        # Rule 1: Place $ in FOLLOW(Start_Symbol)
        self.follow_sets[self.start_symbol].add('$')

        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    for i, symbol_B in enumerate(body):
                        if symbol_B in self.non_terminals: # Only compute FOLLOW for non-terminals
                            # Rule 2: If A -> αBβ, then everything in FIRST(β) (except ε) is in FOLLOW(B)
                            # Rule 3: If A -> αB or A -> αBβ and ε is in FIRST(β),
                            #         then everything in FOLLOW(A) is in FOLLOW(B)
                            
                            # Case for β (symbols after B)
                            beta_part = body[i+1:]
                            if beta_part:
                                first_of_beta = set()
                                all_beta_derive_epsilon = True
                                for beta_symbol in beta_part:
                                    if beta_symbol not in self.first_sets: # Handle undefined symbols in productions gracefully
                                        # This means grammar is ill-defined, but try to continue
                                        all_beta_derive_epsilon = False
                                        break
                                    
                                    first_of_beta.update(self.first_sets[beta_symbol] - {'eps'})
                                    if 'eps' not in self.first_sets[beta_symbol]:
                                        all_beta_derive_epsilon = False
                                        break
                                
                                old_size = len(self.follow_sets[symbol_B])
                                self.follow_sets[symbol_B].update(first_of_beta)
                                if len(self.follow_sets[symbol_B]) != old_size:
                                    changed = True

                                # If beta can derive epsilon, then FOLLOW(head) also goes to FOLLOW(symbol_B)
                                if all_beta_derive_epsilon:
                                    old_size = len(self.follow_sets[symbol_B])
                                    self.follow_sets[symbol_B].update(self.follow_sets[head])
                                    if len(self.follow_sets[symbol_B]) != old_size:
                                        changed = True
                            else: # Rule 3: A -> αB (B is at the end of production)
                                old_size = len(self.follow_sets[symbol_B])
                                self.follow_sets[symbol_B].update(self.follow_sets[head])
                                if len(self.follow_sets[symbol_B]) != old_size:
                                    changed = True

    def build_ll1_table(self):
        """
        Builds the LL(1) parsing table.
        Returns a dictionary M[(NonTerminal, Terminal)] = [ProductionRHS_list]
        Reports conflicts if not LL(1).
        """
        if not self.first_sets or not self.follow_sets:
            self.compute_first_sets()
            self.compute_follow_sets()

        parsing_table = {}
        ll1_conflict_detected = False

        for head in self.non_terminals:
            for body in self.productions[head]:
                # Calculate FIRST set of the production body
                first_of_body = set()
                all_body_derive_epsilon = True
                
                for symbol in body:
                    if symbol not in self.first_sets: # Should not happen if FIRST sets are computed properly
                        continue 
                    
                    first_of_body.update(self.first_sets[symbol] - {'eps'})
                    if 'eps' not in self.first_sets[symbol]:
                        all_body_derive_epsilon = False
                        break
                
                # Rule 1: For each terminal 'a' in FIRST(body), add M[head, a] = body
                for terminal in first_of_body:
                    if (head, terminal) in parsing_table and parsing_table[(head, terminal)] != body:
                        print(f"LL(1) conflict detected for M[{head}, {terminal}]: "
                              f"Existing: {parsing_table[(head, terminal)]}, New: {body}")
                        ll1_conflict_detected = True
                    parsing_table[(head, terminal)] = body
                
                # Rule 2: If epsilon is in FIRST(body), for each terminal 'b' in FOLLOW(head), add M[head, b] = body
                # Also, if '$' is in FOLLOW(head), add M[head, '$'] = body
                if all_body_derive_epsilon and 'eps' in self.first_sets.get(body[0] if body else 'eps', {}): # Check if the production body itself can derive epsilon
                    # If body is ['eps'], then it derives epsilon.
                    # If body has symbols, check if all symbols can derive epsilon.
                    # This implies 'eps' was added to first_of_body implicitly in the loop above.
                    
                    # Re-evaluate the condition for epsilon deriving productions:
                    # 'eps' is in FIRST(body) if body is ['eps'] OR if all symbols in body derive epsilon.
                    
                    can_derive_epsilon = False
                    if body == ['eps']:
                        can_derive_epsilon = True
                    else:
                        temp_derive_epsilon = True
                        for symbol in body:
                            if 'eps' not in self.first_sets.get(symbol, {}):
                                temp_derive_epsilon = False
                                break
                        if temp_derive_epsilon:
                            can_derive_epsilon = True


                    if can_derive_epsilon:
                        for terminal in self.follow_sets.get(head, set()):
                            if (head, terminal) in parsing_table and parsing_table[(head, terminal)] != body:
                                print(f"LL(1) conflict detected for M[{head}, {terminal}]: "
                                      f"Existing: {parsing_table[(head, terminal)]}, New: {body}")
                                ll1_conflict_detected = True
                            parsing_table[(head, terminal)] = body

        if ll1_conflict_detected:
            print("\nGrammar is NOT LL(1) due to conflicts.")
        else:
            print("\nGrammar is LL(1).")

        return parsing_table


# This function was previously in ll1_to_dpda.py or directly in main.py,
# but main.py's import expects it from cfg_parser.py
def convert_ll1_to_dpda(cfg_instance, parsing_table):
    """
    Converts an LL(1) parsing table into DPDA transitions.

    The DPDA transitions are primarily for non-terminal expansions based on the
    LL(1) parsing table. Terminal matching and final acceptance are handled
    directly within the DPDA's run method for this specific LL(1) parser model.

    Args:
        cfg_instance (CFG): An instance of the CFG class.
        parsing_table (dict): The LL(1) parsing table.

    Returns:
        dict: A dictionary representing the DPDA's transition function (trf).
              Keys are (state, input_symbol, stack_top), values are (next_state, push_string).
    """
    trf = {}
    q0 = 'q0' # The single state for our LL(1) DPDA

    # Generate transitions for non-terminal expansions based on the parsing table.
    # For each entry M[NonTerminal, LookaheadTerminal] = ProductionRHS:
    # DPDA transition: (q0, LookaheadTerminal, NonTerminal) -> (q0, ProductionRHS_as_string)
    for (non_terminal, lookahead_terminal), production_rhs in parsing_table.items():
        if production_rhs: # If there is a production rule for this (NT, T) pair
            if production_rhs == ['eps']: # Use ['eps'] as list for comparison
                # If the production is an epsilon production (e.g., A -> ε),
                # the DPDA should push 'eps' (empty string) onto the stack.
                push_string_for_dpda = 'eps' 
            else:
                # For non-epsilon productions, join the RHS symbols with spaces.
                # IMPORTANT: DO NOT REVERSE HERE. The DPDA's run method will handle
                # pushing them in reverse order onto the stack so the leftmost symbol
                # of the production is at the top.
                push_string_for_dpda = ' '.join(production_rhs)
            
            # Add the transition to the DPDA's transition function
            trf[(q0, lookahead_terminal, non_terminal)] = (q0, push_string_for_dpda)

    return trf