def wc(s):
    d = {}
    for w in s.split():
        w = w.strip(".,!?;:").lower()
        if w == "":
            continue
        if w in d:
            d[w] = d[w] + 1
        else:
            d[w] = 1
    return d
