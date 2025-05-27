class DPDA:
    def __init__(self, trf, input, state):
        self.head = 0
        self.trf = trf
        self.state = str(state)
        self.input = input
        self.stack = ['Z']
        
    def step(self):
        a = self.input[self.head]
        s = self.stack.pop()
        state, ss = self.trf.get((self.state, a, s), (None, None))
        if state is None:
            print("Rejected: No valid transition found.")
            exit(1)
        if ss != 'e':
            for symbol in reversed(ss):
                self.stack.append(symbol)
        self.state = state
        print('{:20s} [{:10s}] {:5s}'.format(self.input[self.head:], ''.join(self.stack), self.state))        
        self.head += 1
    
    def run(self):
        print('{:20s} [{:10s}] {:5s}'.format(self.input[self.head:], ''.join(self.stack), self.state))
        
        while self.head < len(self.input):
            self.step()

        if self.stack:
            s = self.stack.pop()
            if self.trf.get((self.state, 'e', s)):
                state, ss = self.trf.get((self.state, 'e', s))
                if ss != 'e':
                    for symbol in reversed(ss):
                        self.stack.append(symbol)
                self.state = state        
                print('{:20s} [{:10s}] {:5s}'.format('e', ''.join(self.stack), self.state))
            else:
                print("Rejected: Stack not empty and no e-transition.")
                return
        
        print("Accepted")
def load_transitions(filename):
    trf = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            current_state, input_symbol, pop_symbol, next_state, push_string = parts
            trf[(current_state, input_symbol, pop_symbol)] = (next_state, push_string)
    return trf



if __name__ == "__main__":
    trf = load_transitions("dpda.txt")
    input_string = input("Enter input string: ")
    dpda = DPDA(trf, input_string, 'q0') 
    dpda.run()