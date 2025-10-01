# part4_validator.py
# Convert RE = (0|1)*01 to DFA and validate strings

import string
from collections import defaultdict

# -------------------------------
# Helpers from Part 3
# -------------------------------
def add_concat(regex: str) -> str:
    result = ""
    for i in range(len(regex)):
        c1 = regex[i]
        result += c1
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            if (c1 in string.ascii_lowercase + "01" or c1 == ')' or c1 == '*') and (c2 in string.ascii_lowercase + "01" or c2 == '('):
                result += '.'
    return result

def precedence(op: str) -> int:
    if op == '*': return 3
    if op == '.': return 2
    if op == '|': return 1
    return 0

def regex_to_postfix(regex: str) -> str:
    stack = []
    output = []
    for c in regex:
        if c in string.ascii_lowercase + "01":
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence(stack[-1]) >= precedence(c):
                output.append(stack.pop())
            stack.append(c)
    while stack:
        output.append(stack.pop())
    return "".join(output)

class State:
    def __init__(self):
        self.edges = defaultdict(list)

def postfix_to_nfa(postfix: str):
    stack = []
    for c in postfix:
        if c in string.ascii_lowercase + "01":
            s0, s1 = State(), State()
            s0.edges[c].append(s1)
            stack.append((s0, s1))
        elif c == '.':
            n2 = stack.pop()
            n1 = stack.pop()
            n1[1].edges['ε'].append(n2[0])
            stack.append((n1[0], n2[1]))
        elif c == '|':
            n2 = stack.pop()
            n1 = stack.pop()
            s0, s1 = State(), State()
            s0.edges['ε'] += [n1[0], n2[0]]
            n1[1].edges['ε'].append(s1)
            n2[1].edges['ε'].append(s1)
            stack.append((s0, s1))
        elif c == '*':
            n1 = stack.pop()
            s0, s1 = State(), State()
            s0.edges['ε'] += [n1[0], s1]
            n1[1].edges['ε'] += [n1[0], s1]
            stack.append((s0, s1))
    return stack.pop()

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
            new_set = frozenset(epsilon_closure(move(curr, sym)))
            if not new_set:
                continue
            if new_set not in dfa_states:
                dfa_states[new_set] = f"q{state_id}"
                state_id += 1
                unmarked.append(new_set)
            transitions[curr_name][sym] = dfa_states[new_set]

    accepting = {dfa_states[s] for s in dfa_states if end in s}
    return transitions, accepting

def print_dfa(transitions, accepting):
    symbols = set()
    for t in transitions.values():
        symbols.update(t.keys())
    symbols = sorted(symbols)

    col_widths = []
    header = ["State"] + list(symbols) + ["Accepting?"]
    for i, h in enumerate(header):
        max_len = len(h)
        for state, trans in transitions.items():
            if i == 0:
                max_len = max(max_len, len(state))
            elif i <= len(symbols):
                sym = symbols[i-1]
                max_len = max(max_len, len(trans.get(sym, "-")))
            else:
                max_len = max(max_len, 3)
        col_widths.append(max_len + 2)

    # Print header
    for i, h in enumerate(header):
        print(h.ljust(col_widths[i]), end="")
    print()

    # Print rows
    for state in sorted(transitions.keys()):
        print(state.ljust(col_widths[0]), end="")
        for i, sym in enumerate(symbols):
            val = transitions[state].get(sym, "-")
            print(val.ljust(col_widths[i+1]), end="")
        print(("Yes" if state in accepting else "No").ljust(col_widths[-1]))

# -------------------------------
# DFA Validation
# -------------------------------
def validate_string(dfa, accepting, alphabet, string):
    current = "q0"
    for ch in string:
        if ch not in alphabet or ch not in dfa[current]:
            return "Rejected"
        current = dfa[current][ch]
    return "Accepted" if current in accepting else "Rejected"

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    regex = "(0|1)*01"
    strings_to_test = ["1101", "111", "0001"]

    concat = add_concat(regex)
    postfix = regex_to_postfix(concat)
    nfa_start, nfa_end = postfix_to_nfa(postfix)
    dfa, accepting = nfa_to_dfa(nfa_start, nfa_end)

    print(f"Regex: {regex}\n")
    print_dfa(dfa, accepting)
    print("\nString validation results:")
    for s in strings_to_test:
        result = validate_string(dfa, accepting, ['0','1'], s)
        print(f"{s}: {result}")
