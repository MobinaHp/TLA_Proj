def compute_first(productions, terminals, non_terminals):
    first_sets = {symbol: set() for symbol in non_terminals.union(terminals)}

    for t in terminals:
        first_sets[t].add(t)

    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for production in productions[nt]:
                if production == ["ε"]:
                    if "ε" not in first_sets[nt]:
                        first_sets[nt].add("ε")
                        changed = True
                    continue

                all_symbols_can_derive_epsilon = True
                for symbol in production:
                    old_len = len(first_sets[nt])
                    first_sets[nt].update(first_sets[symbol] - {"ε"})
                    if len(first_sets[nt]) > old_len:
                        changed = True

                    if "ε" not in first_sets[symbol]:
                        all_symbols_can_derive_epsilon = False
                        break

                if all_symbols_can_derive_epsilon:
                    if "ε" not in first_sets[nt]:
                        first_sets[nt].add("ε")
                        changed = True
    return first_sets


def compute_follow(productions, start_symbol, terminals, non_terminals, first_sets):
    follow_sets = {nt: set() for nt in non_terminals}

    if start_symbol:
        follow_sets[start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for production_head, production_list in productions.items():
            for production in production_list:
                for i, symbol in enumerate(production):
                    if symbol in non_terminals:
                        beta = production[i + 1 :]

                        if beta:
                            first_of_beta = set()
                            all_beta_can_derive_epsilon = True
                            for beta_symbol in beta:
                                first_of_beta.update(first_sets[beta_symbol])
                                if "ε" not in first_sets[beta_symbol]:
                                    all_beta_can_derive_epsilon = False
                                    break

                            old_len = len(follow_sets[symbol])
                            follow_sets[symbol].update(first_of_beta - {"ε"})
                            if len(follow_sets[symbol]) > old_len:
                                changed = True

                            if all_beta_can_derive_epsilon:
                                old_len = len(follow_sets[symbol])
                                follow_sets[symbol].update(follow_sets[production_head])
                                if len(follow_sets[symbol]) > old_len:
                                    changed = True
                        else:
                            if symbol != production_head:
                                old_len = len(follow_sets[symbol])
                                follow_sets[symbol].update(follow_sets[production_head])
                                if len(follow_sets[symbol]) > old_len:
                                    changed = True
    return follow_sets


def build_ll1_parsing_table(productions, terminals, non_terminals, FIRST, FOLLOW):
    parsing_table = {}

    all_terminals_with_dollar = terminals.union({"$"})
    for nt in non_terminals:
        for t in all_terminals_with_dollar:
            parsing_table[(nt, t)] = []

    for nt, rules in productions.items():
        for rule in rules:
            first_alpha = set()
            all_epsilon_possible = True
            if rule == ["ε"]:
                first_alpha.add("ε")
            else:
                for symbol in rule:
                    first_alpha.update(FIRST[symbol])
                    if "ε" not in FIRST[symbol]:
                        all_epsilon_possible = False
                        break
                if all_epsilon_possible and "ε" not in first_alpha:
                    first_alpha.add("ε")

            for terminal in first_alpha:
                if terminal == "ε":
                    for follow_terminal in FOLLOW[nt]:
                        if parsing_table[(nt, follow_terminal)]:
                            print(
                                f"LL(1) conflict detected at M[{nt}, {follow_terminal}]:"
                            )
                            print(
                                f"  Existing rule: {nt} -> {' '.join(parsing_table[(nt, follow_terminal)][0])}"
                            )
                            print(f"  New rule: {nt} -> {' '.join(rule)}")
                            return None
                        parsing_table[(nt, follow_terminal)].append(rule)
                else:
                    if parsing_table[(nt, terminal)]:
                        print(f"LL(1) conflict detected at M[{nt}, {terminal}]:")
                        print(
                            f"  Existing rule: {nt} -> {' '.join(parsing_table[(nt, terminal)][0])}"
                        )
                        print(f"  New rule: {nt} -> {' '.join(rule)}")
                        return None  # Indicate conflict
                    parsing_table[(nt, terminal)].append(rule)

    final_parsing_table = {}
    for (nt, t), rules_list in parsing_table.items():
        if rules_list:
            final_parsing_table[(nt, t)] = rules_list[0]
        else:
            final_parsing_table[(nt, t)] = None

    return final_parsing_table
