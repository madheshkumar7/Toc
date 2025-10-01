# part3_regex2dfa.py
# Program to convert a given regular expression into its equivalent DFA
# Example: (a|b)*abb

import string
from collections import defaultdict

# -------------------------------
# Step 1: Add explicit concatenation
# -------------------------------
def add_concat(regex: str) -> str:
    result = ""
    for i in range(len(regex)):
        c1 = regex[i]
        result += c1
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            if (c1 in string.ascii_lowercase or c1 == ')' or c1 == '*') and (c2 in string.ascii_lowercase or c2 == '('):
                result += '.'
    return result

# -------------------------------
# Step 2: Convert to postfix
# -------------------------------
def precedence(op: str) -> int:
    if op == '*': return 3
    if op == '.': return 2
    if op == '|': return 1
    return 0

def regex_to_postfix(regex: str) -> str:
    stack = []
    output = []
    for c in regex:
        if c in string.ascii_lowercase:  # operand
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:  # operator
            while stack and precedence(stack[-1]) >= precedence(c):
                output.append(stack.pop())
            stack.append(c)
    while stack:
        output.append(stack.pop())
    return "".join(output)

# -------------------------------
# Step 3: Thompson construction → NFA
# -------------------------------
class State:
    def __init__(self):
        self.edges = defaultdict(list)

def postfix_to_nfa(postfix: str):
    stack = []
    for c in postfix:
        if c in string.ascii_lowercase:
            s0, s1 = State(), State()
            s0.edges[c].append(s1)
            stack.append((s0, s1))
        elif c == '.':  # concatenation
            n2 = stack.pop()
            n1 = stack.pop()
            n1[1].edges['ε'].append(n2[0])
            stack.append((n1[0], n2[1]))
        elif c == '|':  # alternation
            n2 = stack.pop()
            n1 = stack.pop()
            s0, s1 = State(), State()
            s0.edges['ε'] += [n1[0], n2[0]]
            n1[1].edges['ε'].append(s1)
            n2[1].edges['ε'].append(s1)
            stack.append((s0, s1))
        elif c == '*':  # Kleene star
            n1 = stack.pop()
            s0, s1 = State(), State()
            s0.edges['ε'] += [n1[0], s1]
            n1[1].edges['ε'] += [n1[0], s1]
            stack.append((s0, s1))
    return stack.pop()

# -------------------------------
# Step 4: Subset construction → DFA
# -------------------------------
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for nxt in s.edges.get('ε', []):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure

def move(states, symbol):
    result = set()
    for s in states:
        for nxt in s.edges.get(symbol, []):
            result.add(nxt)
    return result

def nfa_to_dfa(start, end):
    dfa_states = {}
    unmarked = []
    start_closure = frozenset(epsilon_closure({start}))
    dfa_states[start_closure] = "q0"
    unmarked.append(start_closure)

    transitions = {}
    state_id = 1

    while unmarked:
        curr = unmarked.pop()
        curr_name = dfa_states[curr]
        transitions[curr_name] = {}
        symbols = set()
        for s in curr:
            symbols.update([c for c in s.edges.keys() if c != 'ε'])

        for sym in symbols:
            new_set = frozenset(epsilon_closure(move(curr, sym)))  # ✅ make frozenset
            if not new_set:
                continue
            if new_set not in dfa_states:
                dfa_states[new_set] = f"q{state_id}"
                state_id += 1
                unmarked.append(new_set)
            transitions[curr_name][sym] = dfa_states[new_set]

    accepting = {dfa_states[s] for s in dfa_states if end in s}
    return transitions, accepting


# -------------------------------
# Step 5: Print DFA transition table
# -------------------------------
def print_dfa(transitions, accepting):
    # Collect all symbols
    symbols = set()
    for t in transitions.values():
        symbols.update(t.keys())
    symbols = sorted(symbols)

    # Compute column widths
    col_widths = []
    header = ["State"] + list(symbols) + ["Accepting?"]
    for i, h in enumerate(header):
        max_len = len(h)
        for state, trans in transitions.items():
            if i == 0:  # State column
                max_len = max(max_len, len(state))
            elif i <= len(symbols):  # symbol columns
                sym = symbols[i-1]
                max_len = max(max_len, len(trans.get(sym, "-")))
            else:  # Accepting?
                max_len = max(max_len, 3)
        col_widths.append(max_len + 2)  # add padding

    # Print header
    for i, h in enumerate(header):
        print(h.ljust(col_widths[i]), end="")
    print()

    # Print each row
    for state in sorted(transitions.keys()):
        print(state.ljust(col_widths[0]), end="")
        for i, sym in enumerate(symbols):
            val = transitions[state].get(sym, "-")
            print(val.ljust(col_widths[i+1]), end="")
        print(("Yes" if state in accepting else "No").ljust(col_widths[-1]))


# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    regex = "(a|b)*abb"
    print("Regex:", regex)

    concat = add_concat(regex)
    postfix = regex_to_postfix(concat)
    print("Postfix:", postfix)

    nfa_start, nfa_end = postfix_to_nfa(postfix)
    dfa, accepting = nfa_to_dfa(nfa_start, nfa_end)

    print_dfa(dfa, accepting)
