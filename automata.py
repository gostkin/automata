#!/usr/bin/python3

class SimpleAutomata:
    def __init__(self):
        self.state_count = 0
        self.edges = {}

        self.initial_state = None
        self.final_states = None

    def add_state(self):
        self.state_count += 1
        return self.state_count

    def add_edge(self, _from, _to, _val):
        assert (1 <= _from <= self.state_count)
        assert (1 <= _to <= self.state_count)

        if (_from, _to) in self.edges:
            self.edges[(_from, _to)] = '+'.join(i for i in [self.edges[(_from, _to)], _val] if i != '0') or '0'
        else:
            self.edges[(_from, _to)] = _val

    def accepts(self, word):
        def dfs(state, word):
            if len(word) == 0:
                if state in self.final_states:
                    return True
                else:
                    return False
            else:
                return dfs(self.edges[(state, word[0])], word[1:])

        return dfs(self.initial_state, word)


class ComplexAutomata:
    def __init__(self):
        self.state_number = 0
        self.eps_reachable = dict()
        self.edges = dict()
        self.symbols = list()
        self.final_states = set()
        self.initial_state = 0
        
    def add_state(self):
        self.state_number += 1
        self.eps_reachable[self.state_number] = {self.state_number}
        return self.state_number

    def add_edge(self, _from, _to, symbol):
        assert (1 <= _from <= self.state_number)
        assert (1 <= _to <= self.state_number)
        if symbol == '1':
            self.eps_reachable[_from].add(_to)
        elif not symbol == '.':
            self.edges.setdefault((_from, symbol), list()).append(_to)
        else:
            for sym in self.symbols:
                self.edges.setdefault((_from, sym), list()).append(_to)

    def p_plus(self, expr):
        if not expr:
            return '', None, None

        if expr[0] == ')':
            return expr, None, None

        first = second = -1
        mid = list()

        while first is not None:
            expr, first, second = self.p_concatenation(expr)
            if first is not None:
                mid.append((first, second))
            if expr and expr[0] == '+':
                expr = expr[1:]
        if len(mid) == 1:
            return expr, mid[0][0], mid[0][1]

        fs = self.add_state()
        ss = self.add_state()

        for first, second in mid:
            self.add_edge(fs, first, '1')
            self.add_edge(second, ss, '1')

        return expr, fs, ss

    def p_single(self, expr):
        if not expr:
            return '', None, None

        if expr[0] == ')':
            return expr, None, None

        if expr[0] == '(':
            expr, first, second = self.p_plus(expr[1:])
            return expr[1:], first, second

        if expr[0] == '+':
            return expr, None, None

        first = second = self.add_state()

        while expr and (expr[0].isalpha() or expr[0] in '01'):
            if expr[0] == '0':
                expr = expr[1:]
                temp = second
                second = self.add_state()

                if expr and expr[0] == '*':
                    self.add_edge(temp, second, '1')
                    expr = expr[1:]
            elif expr[0] == '1':
                expr = expr[1:]
                if expr and expr[0] == '*':
                    expr = expr[1:]
            else:
                temp = self.add_state()
                q = expr[0]
                expr = expr[1:]
                if expr and expr[0] == '*':
                    t1 = self.add_state()
                    self.add_edge(second, temp, '1')
                    self.add_edge(t1, temp, '1')
                    self.add_edge(temp, t1, q)
                    expr = expr[1:]
                else:
                    self.add_edge(second, temp, q)

                second = temp

        return expr, first, second

    def p_concatenation(self, expr):
        if not expr:
            return '', None, None

        if expr[0] == ')':
            return expr, None, None

        first = second = -1
        mid = list()

        while first is not None:
            expr, first, second = self.p_single(expr)
            if expr and expr[0] == '*':
                temp = self.add_state()

                expr = expr[1:]

                self.add_edge(second, temp, '1')
                self.add_edge(temp, first, '1')

                mid.append((temp, temp))

            elif first is not None:
                mid.append((first, second))

        if not mid:
            return expr, None, None

        for i in range(len(mid) - 1):
            self.add_edge(mid[i][1], mid[i + 1][0], '1')

        return expr, mid[0][0], mid[-1][1]

    def parse_polish(self, expr):
        stack = list()
        s = ""
        for i in expr:
            if i == '.':
                last = stack[-1]
                stack.pop()
                prevlast = stack[-1]
                stack.pop()
                stack.append(prevlast + last)
            elif i == '*':
                last = stack[-1]
                stack.pop()
                stack.append('(' + last + ')*')
            elif i == '+':
                last = stack[-1]
                stack.pop()
                prevlast = stack[-1]
                stack.pop()
                stack.append('(' + prevlast + '+' + last + ')')
            elif i == '1':
                stack.append('1')
            else:
                stack.append(i)

        s = stack[0]
        return s

    def get(self, states, symbol):
        res = set()
        for state in states:
            for temp in self.edges.get((state, symbol), list()):
                res |= self.eps_reachable[temp]

        return tuple(sorted(res))

    def minimize(self):
        def reorder():
            count = 0
            nncl = dict()

            def dfs(state):
                if state in nncl:
                    return
                nonlocal count
                count += 1
                nncl[state] = count
                for symbol in self.symbols:
                    dfs(classes[self.get(r_classes[state], symbol)])

            dfs(classes[tuple(sorted(self.eps_reachable[self.initial_state]))])
            return nncl

        for i in range(mauto.state_number):
            for state in mauto.eps_reachable:
                for temp in list(mauto.eps_reachable[state]):
                    mauto.eps_reachable[state] |= mauto.eps_reachable[temp]

        m_states = list()
        m_edges = dict()
        m_final_states = set()

        m_states.append(tuple(sorted(self.eps_reachable[self.initial_state])))
        if self.eps_reachable[self.initial_state] & self.final_states:
            m_final_states.add(tuple(sorted(self.eps_reachable[self.initial_state])))

        for i in range(2 ** self.state_number):
            if len(m_states) <= i:
                break
            for symbol in self.symbols:
                w = self.get(m_states[i], symbol)
                if w not in m_states:
                    m_states.append(w)
                if set(w) & self.final_states:
                    m_final_states.add(w)
                m_edges[(m_states[i], symbol)] = w

        classes = {state: int(state in m_final_states) for state in m_states}

        fromcl = 0
        while len(set(classes.values())) != fromcl:
            fromcl = len(set(classes.values()))
            new_classes = dict()
            for st in m_states:
                new_classes[st] = (classes[st],) + tuple(classes[self.get(st, symbol)] for i, symbol in
                                                         enumerate(self.symbols))

            classes_set = {symbol: iter for iter, symbol in enumerate(sorted(set(new_classes.values())))}
            classes = {st: classes_set[new_classes[st]] for st in m_states}
        classes = {cl: classes[cl] + 1 for cl in classes}
        r_classes = {classes[cl]: cl for cl in classes}

        new_classes = reorder()
        r_new_classes = {new_classes[cl]: cl for cl in new_classes}

        auto = SimpleAutomata()
        auto.state_count = fromcl
        auto.initial_state = new_classes[classes[tuple(sorted(self.eps_reachable[self.initial_state]))]]
        auto.final_states = sorted({new_classes[classes[f]] for f in m_final_states})

        for cl in sorted(r_new_classes):
            for symbol in self.symbols:
                auto.edges[(cl, symbol)] = new_classes[classes[self.get(r_classes[r_new_classes[cl]], symbol)]]
                # print(str(cl) + ' ' + symbol + ' >> ' +
                # str(new_classes[classes[self.get(r_classes[r_new_classes[cl]], symbol)]]))

        return auto


if __name__ == "__main__":
    mauto = ComplexAutomata()

    raw_expr, raw_word = input("Enter expression in polish notation and a word: ").split()
    tmp = []
    regexpr = "".join(raw_expr.split())
    for i in regexpr:
        if i not in '.*+1':
            tmp.append(i)

    if raw_word.count("1") == len(raw_word) or len(tmp) == 0:
        print(0)
        exit(0)

    mauto.symbols = "".join(sorted(list(set(tmp + ["a", "b", "c"]))))
    # mauto.symbols = "abc"

    regexp = mauto.parse_polish(regexpr)
    # print(regexp)
    s, initial, final = mauto.p_plus(regexp)
    mauto.initial_state = initial
    mauto.final_states = {final}

    auto = mauto.minimize()

    # print(auto.initial_state, *auto.final_states)
    word = raw_word

    if auto.accepts(word):
        print("OK")
    else:
        print("Not accepted")
