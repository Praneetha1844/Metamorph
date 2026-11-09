def calc(p, c, q):
    t = 0
    if c == "gold":
        if q > 10:
            t = p * q * 0.8
        else:
            t = p * q * 0.9
    elif c == "silver":
        if q > 10:
            t = p * q * 0.9
        else:
            t = p * q * 0.95
    else:
        t = p * q
    return round(t, 2)
