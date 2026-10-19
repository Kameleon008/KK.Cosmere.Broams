#!/usr/bin/env python3
"""Naprawa schematu KiCad po serwerze MCP.

Bug: kicad_place_symbol_from_library nie zamyka nawiasu wpisu w (lib_symbols),
gdy w pliku jest juz inny symbol -> kolejne wpisy zagniezdzaja sie w poprzednich
(np. "Device:C" staje sie dzieckiem "Device:R"), przez co KiCad odrzuca plik.

Naprawa: wpisy `symbol` o nazwie z dwukropkiem (lib_id), zagniezdzone w innym
wpisie `symbol`, wyciagamy na poziom (lib_symbols) jako rodzenstwo.

Uzycie: python fix_sch.py <plik.kicad_sch>
"""
import sys


def tokenize(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in "()":
            toks.append(c); i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            while j < n:
                if s[j] == "\\":
                    j += 2
                elif s[j] == '"':
                    break
                else:
                    j += 1
            toks.append(s[i:j + 1]); i = j + 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in "()":
                j += 1
            toks.append(s[i:j]); i = j
    return toks


def parse(toks):
    it = iter(toks)

    def walk():
        node = []
        for t in it:
            if t == "(":
                node.append(walk())
            elif t == ")":
                return node
            else:
                node.append(t)
        return node

    assert next(it) == "("
    return walk()


def emit(node, level=0):
    ind = "\t" * level
    if not isinstance(node, list):
        return ind + str(node)
    if all(not isinstance(c, list) for c in node):
        return ind + "(" + " ".join(str(c) for c in node) + ")"
    out = ind + "(" + str(node[0])
    i = 1
    while i < len(node) and not isinstance(node[i], list):
        out += " " + str(node[i]); i += 1
    for c in node[i:]:
        out += "\n" + emit(c, level + 1)
    return out + "\n" + ind + ")"


def is_entry(n):
    return (isinstance(n, list) and n and n[0] == "symbol"
            and isinstance(n[1], str) and ":" in n[1])


def fix_lib_symbols(ls):
    result, queue = ["lib_symbols"], list(ls[1:])
    while queue:
        node = queue.pop(0)
        if isinstance(node, list) and node and node[0] == "symbol":
            keep = [node[0]]
            for c in node[1:]:
                if is_entry(c):
                    queue.append(c)          # wynies na poziom lib_symbols
                else:
                    keep.append(c)
            result.append(keep)
        else:
            result.append(node)
    return result


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        root = parse(tokenize(f.read()))
    fixed = 0
    for idx, c in enumerate(root):
        if isinstance(c, list) and c and c[0] == "lib_symbols":
            before = len(c)
            root[idx] = fix_lib_symbols(c)
            fixed = len(root[idx]) - before
            break
    with open(path, "w", encoding="utf-8") as f:
        f.write(emit(root) + "\n")
    print(f"naprawiono, przeniesionych wpisow: {fixed}")


if __name__ == "__main__":
    main()
