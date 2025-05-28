def compute_first(productions, terminals, non_terminals):
    """
    Computes the FIRST set for all grammar symbols (terminals and non-terminals).

    Args:
        productions (dict): Dictionary of grammar productions.
        terminals (set): Set of terminal symbols.
        non_terminals (set): Set of non-terminal symbols.

    Returns:
        dict: A dictionary where keys are symbols and values are their FIRST sets.
    """
    first_sets = {symbol: set() for symbol in non_terminals.union(terminals)}

    # Rule 1: For each terminal 't', FIRST(t) = {t}
    for t in terminals:
        first_sets[t].add(t)

    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for production in productions[nt]: # For each production A -> alpha
                # Rule 2: If alpha is epsilon (A -> ε)
                if production == ['ε']:
                    if 'ε' not in first_sets[nt]:
                        first_sets[nt].add('ε')
                        changed = True
                    continue

                # Rule 3: If alpha is Y1 Y2 ... Yk
                # Add FIRST(Y1) - {ε} to FIRST(A)
                # If ε is in FIRST(Y1), add FIRST(Y2) - {ε} to FIRST(A), and so on.
                # If all Yi can derive ε, then add ε to FIRST(A).
                all_symbols_can_derive_epsilon = True
                for symbol in production:
                    old_len = len(first_sets[nt])
                    first_sets[nt].update(first_sets[symbol] - {'ε'})
                    if len(first_sets[nt]) > old_len:
                        changed = True

                    if 'ε' not in first_sets[symbol]:
                        all_symbols_can_derive_epsilon = False
                        break # Stop if a symbol in the production cannot derive epsilon
                
                if all_symbols_can_derive_epsilon:
                    # If all symbols in the RHS can derive epsilon, then NT can also derive epsilon
                    if 'ε' not in first_sets[nt]:
                        first_sets[nt].add('ε')
                        changed = True
    return first_sets

def compute_follow(productions, start_symbol, terminals, non_terminals, first_sets):
    """
    Computes the FOLLOW set for all non-terminal symbols.

    Args:
        productions (dict): Dictionary of grammar productions.
        start_symbol (str): The start symbol of the grammar.
        terminals (set): Set of terminal symbols.
        non_terminals (set): Set of non-terminal symbols.
        first_sets (dict): Pre-computed FIRST sets.

    Returns:
        dict: A dictionary where keys are non-terminals and values are their FOLLOW sets.
    """
    follow_sets = {nt: set() for nt in non_terminals}

    # Rule 1: Add '$' (end-of-input marker) to FOLLOW(Start_Symbol)
    if start_symbol:
        follow_sets[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for production_head, production_list in productions.items():
            for production in production_list: # For each production B -> alpha A beta
                for i, symbol in enumerate(production):
                    if symbol in non_terminals: # Only compute FOLLOW for non-terminals
                        beta = production[i+1:] # The part of the RHS after 'symbol'

                        if beta:
                            # Rule 2: If B -> alpha A beta, then add FIRST(beta) - {ε} to FOLLOW(A)
                            first_of_beta = set()
                            all_beta_can_derive_epsilon = True
                            for beta_symbol in beta:
                                first_of_beta.update(first_sets[beta_symbol])
                                if 'ε' not in first_sets[beta_symbol]:
                                    all_beta_can_derive_epsilon = False
                                    break # Stop if a symbol in beta cannot derive epsilon
                            
                            old_len = len(follow_sets[symbol])
                            follow_sets[symbol].update(first_of_beta - {'ε'})
                            if len(follow_sets[symbol]) > old_len:
                                changed = True

                            # Rule 3: If ε is in FIRST(beta), then add FOLLOW(B) to FOLLOW(A)
                            if all_beta_can_derive_epsilon:
                                old_len = len(follow_sets[symbol])
                                follow_sets[symbol].update(follow_sets[production_head])
                                if len(follow_sets[symbol]) > old_len:
                                    changed = True
                        else:
                            # Rule 3 (continued): If B -> alpha A (A is the last symbol)
                            # Add FOLLOW(B) to FOLLOW(A)
                            # Avoid adding FOLLOW(A) to itself if A -> A (direct recursion)
                            if symbol != production_head: 
                                old_len = len(follow_sets[symbol])
                                follow_sets[symbol].update(follow_sets[production_head])
                                if len(follow_sets[symbol]) > old_len:
                                    changed = True
    return follow_sets

def build_ll1_parsing_table(productions, terminals, non_terminals, FIRST, FOLLOW):
    """
    Constructs the LL(1) parsing table.

    Args:
        productions (dict): Dictionary of grammar productions.
        terminals (set): Set of terminal symbols.
        non_terminals (set): Set of non-terminal symbols.
        FIRST (dict): Pre-computed FIRST sets.
        FOLLOW (dict): Pre-computed FOLLOW sets.

    Returns:
        dict or None: The LL(1) parsing table (keys are (NonTerminal, Terminal),
                      values are the RHS production list), or None if a conflict is found.
    """
    parsing_table = {}

    # Initialize parsing table with empty lists to easily detect conflicts
    all_terminals_with_dollar = terminals.union({'$'}) # Include '$' as an input terminal
    for nt in non_terminals:
        for t in all_terminals_with_dollar:
            parsing_table[(nt, t)] = [] # Use a list to store multiple rules for conflict detection

    for nt, rules in productions.items(): # For each non-terminal and its rules
        for rule in rules: # For each production A -> alpha
            # Compute FIRST(alpha)
            first_alpha = set()
            all_epsilon_possible = True
            if rule == ['ε']:
                first_alpha.add('ε')
            else:
                for symbol in rule:
                    first_alpha.update(FIRST[symbol])
                    if 'ε' not in FIRST[symbol]:
                        all_epsilon_possible = False
                        break
                if all_epsilon_possible and 'ε' not in first_alpha:
                    first_alpha.add('ε')

            for terminal in first_alpha:
                if terminal == 'ε':
                    # Rule 2: If ε is in FIRST(alpha), for each 'b' in FOLLOW(A), add A -> alpha to M[A, b]
                    for follow_terminal in FOLLOW[nt]:
                        if parsing_table[(nt, follow_terminal)]:
                            # Conflict detected: More than one rule for M[NT, Terminal]
                            print(f"LL(1) conflict detected at M[{nt}, {follow_terminal}]:")
                            print(f"  Existing rule: {nt} -> {' '.join(parsing_table[(nt, follow_terminal)][0])}")
                            print(f"  New rule: {nt} -> {' '.join(rule)}")
                            return None # Indicate conflict by returning None
                        parsing_table[(nt, follow_terminal)].append(rule)
                else:
                    # Rule 1: For each terminal 'a' in FIRST(alpha), add A -> alpha to M[A, a]
                    if parsing_table[(nt, terminal)]:
                        # Conflict detected
                        print(f"LL(1) conflict detected at M[{nt}, {terminal}]:")
                        print(f"  Existing rule: {nt} -> {' '.join(parsing_table[(nt, terminal)][0])}")
                        print(f"  New rule: {nt} -> {' '.join(rule)}")
                        return None # Indicate conflict
                    parsing_table[(nt, terminal)].append(rule)
    
    # After populating, flatten the parsing table by taking the single rule from each list.
    # If a cell is empty (no rule), it remains None.
    final_parsing_table = {}
    for (nt, t), rules_list in parsing_table.items():
        if rules_list:
            final_parsing_table[(nt, t)] = rules_list[0] # Take the single rule (since no conflicts)
        else:
            final_parsing_table[(nt, t)] = None # No rule for this cell
            
    return final_parsing_table

