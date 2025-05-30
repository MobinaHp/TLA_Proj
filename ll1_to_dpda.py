def convert_ll1_to_dpda(cfg_instance, parsing_table):
    trf = {}
    q0 = "q0"

    for (non_terminal, lookahead_terminal), production_rhs in parsing_table.items():
        if production_rhs:
            if production_rhs == ["ε"]:
                push_string_for_dpda = "eps"
            else:
                push_string_for_dpda = " ".join(production_rhs)

            trf[(q0, lookahead_terminal, non_terminal)] = (q0, push_string_for_dpda)

    return trf
