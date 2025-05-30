from p1 import CFG
from p2 import DPDA  # Only DPDA class is needed, as trf is passed directly
from parsing_table import compute_first, compute_follow, build_ll1_parsing_table
from ll1_to_dpda import convert_ll1_to_dpda
from parse_tree import ParseTreeNode


import sys
import os

GRAMMAR_FILE = "grammar.txt"
DPDA_TRANSITIONS_FILE = (
    "dpda_transitions.txt"  # Optional: if you want to save/load transitions
)


def main():
    if not os.path.exists(GRAMMAR_FILE):
        print(f"'{GRAMMAR_FILE}' not found. Creating a sample one.")
        with open(GRAMMAR_FILE, "w", encoding="utf-8") as f:
            f.write("# Sample LL(1) Grammar for arithmetic expressions\n")
            f.write("START=E\n")
            f.write("NON_TERMINALS=E,T,F,E_prime,T_prime\n")
            f.write("TERMINALS=+,*,id,(,),$,eps\n")
            f.write("E -> T E_prime\n")
            f.write("E_prime -> + T E_prime | eps\n")
            f.write("T -> F T_prime\n")
            f.write("T_prime -> * F T_prime | eps\n")
            f.write("F -> ( E ) | id\n")
    else:
        print(f"'{GRAMMAR_FILE}' already exists. Using existing file.")

    cfg = CFG(GRAMMAR_FILE)
    print("\n--- Loaded Grammar ---")
    print(f"Start symbol: {cfg.start_symbol}")
    print(f"Non-terminals: {cfg.non_terminals}")
    print(f"Terminals: {cfg.terminals}")
    print("Productions:")
    for nt, prods in cfg.productions.items():
        for prod in prods:
            print(f"  {nt} -> {' '.join(prod)}")

    print("\n--- Computing FIRST and FOLLOW sets ---")
    cfg.compute_first_sets()
    print("\nFIRST Sets:")
    for symbol, first_set in cfg.first_sets.items():
        print(f"  FIRST({symbol}): {sorted(list(first_set))}")

    cfg.compute_follow_sets()
    print("\nFOLLOW Sets:")
    for symbol, follow_set in cfg.follow_sets.items():
        print(f"  FOLLOW({symbol}): {sorted(list(follow_set))}")

    print("\n--- Building LL(1) Parsing Table ---")
    parsing_table = cfg.build_ll1_table()

    terminals_sorted = sorted(list(cfg.terminals - {"eps"})) + ["$"]
    non_terminals_sorted = sorted(list(cfg.non_terminals))

    header = "Non-Terminal"
    for t in terminals_sorted:
        header += f"{t:10s}"
    print(header)
    print("-" * (len(header) + 10 * len(terminals_sorted)))

    for nt in non_terminals_sorted:
        row_str = f"{nt:12s}"
        for t in terminals_sorted:
            production_rhs = parsing_table.get((nt, t))
            if production_rhs:
                # Format: 'NT->RHS'
                prod_str = f"{nt}->{' '.join(production_rhs)}"
                row_str += f"{prod_str:10s}"
            else:
                row_str += f"{' ':10s}"
        print(row_str)

    print("\n--- Converting LL(1) Table to DPDA Transitions ---")
    dpda_transitions = convert_ll1_to_dpda(cfg, parsing_table)

    print("Generated DPDA Transitions (for non-terminal expansions):")
    for (state, input_sym, stack_sym), (
        next_state,
        push_str,
    ) in dpda_transitions.items():
        print(f"  ({state}, {input_sym}, {stack_sym}) -> ({next_state}, {push_str})")

    while True:
        user_input = input(
            "\nEnter input string (e.g., id + id * id $), or 'q' to quit: "
        )
        user_input = user_input.replace("\n\r", " ")
        user_input = user_input.replace("\r\n", " ")
        user_input = user_input.replace("\n", " ")
        if user_input.lower() == "file":
            file_path = "./input.txt"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    user_input = f.read().strip()
        if user_input.lower() == "q":
            break

        input_tokens = user_input.split()

        dpda = DPDA(dpda_transitions, input_tokens, cfg.start_symbol, cfg.terminals)
        parse_tree_root = dpda.run()

        if parse_tree_root:
            print("\n--- Generated Parse Tree ---")
            parse_tree_root.display()
        else:
            print("Parsing failed. No parse tree generated.")


if __name__ == "__main__":
    main()
