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
            if production_rhs == ['ε']:
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

