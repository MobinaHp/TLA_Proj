class DPDA:
    def __init__(self):
        self.states = set()
        self.input_alphabet = set()
        self.stack_alphabet = set()
        self.transitions = {}  # Dictionary: (state, input, stack_top) -> (new_state, stack_push)
        self.start_state = None
        self.start_stack = None
        self.accept_states = set()

    def read_from_file(self, filename):
        with open(filename, "r") as file:
            self.states = set(file.readline().strip().split())

            self.input_alphabet = set(file.readline().strip().split())

            self.stack_alphabet = set(file.readline().strip().split())

            self.start_state = file.readline().strip()

            self.start_stack = file.readline().strip()

            self.accept_states = set(file.readline().strip().split())

            for line in file:
                if line.strip():
                    parts = line.strip().split()
                    current_state = parts[0]
                    input_symbol = parts[1] if parts[1] != "e" else ""
                    stack_top = parts[2] if parts[2] != "e" else ""

                    new_state = parts[3]
                    stack_push = parts[4] if parts[4] != "e" else ""

                    key = (current_state, input_symbol, stack_top)
                    self.transitions[key] = (new_state, stack_push)

    def process_input(self, input_string):
        """پردازش رشته ورودی و تعیین پذیرفته شدن یا نشدن"""
        stack = [self.start_stack]
        current_state = self.start_state
        input_index = 0

        while True:
            if input_index >= len(input_string) and current_state in self.accept_states:
                return True

            input_symbol = (
                input_string[input_index] if input_index < len(input_string) else ""
            )

            stack_top = stack[-1] if stack else ""

            transition_key = (current_state, input_symbol, stack_top)

            if transition_key in self.transitions:
                new_state, stack_push = self.transitions[transition_key]
                current_state = new_state
                if stack_top:
                    stack.pop()
                if stack_push:
                    stack.extend(list(stack_push[::-1]))
                input_index += 1 if input_symbol else 0
                continue

            transition_key = (current_state, "", stack_top)
            if transition_key in self.transitions:
                new_state, stack_push = self.transitions[transition_key]
                current_state = new_state
                if stack_top:
                    stack.pop()
                if stack_push:
                    stack.extend(list(stack_push[::-1]))
                continue

            return False

    def __str__(self):
        """نمایش رشته‌ای DPDA"""
        result = []
        result.append("States: " + " ".join(self.states))
        result.append("Input Alphabet: " + " ".join(self.input_alphabet))
        result.append("Stack Alphabet: " + " ".join(self.stack_alphabet))
        result.append("Start State: " + self.start_state)
        result.append("Start Stack: " + self.start_stack)
        result.append("Accept States: " + " ".join(self.accept_states))
        result.append("Transitions:")
        for key in self.transitions:
            state, inp, stack = key
            new_state, stack_push = self.transitions[key]
            result.append(
                f"({state}, {inp if inp else 'e'}, {stack if stack else 'e'}) -> ({new_state}, {stack_push if stack_push else 'e'})"
            )
        return "\n".join(result)


def main():
    dpda = DPDA()
    dpda.read_from_file("dpda.txt")
    print("DPDA loaded successfully!")
    print("This DPDA recognizes the language {a^n b^n | n ≥ 1}")

    while True:
        input_str = input("\nEnter a string to test (or 'exit' to quit): ").strip()

        if input_str.lower() == "exit":
            print("Exiting...")
            break

        result = dpda.process_input(input_str)
        print(f"String '{input_str}' is {'ACCEPTED' if result else 'REJECTED'}")


if __name__ == "__main__":
    main()
