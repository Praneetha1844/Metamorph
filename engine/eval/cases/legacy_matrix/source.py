def transpose(m):
    if len(m) == 0:
        return []
    r = []
    for j in range(len(m[0])):
        row = []
        for i in range(len(m)):
            row.append(m[i][j])
        r.append(row)
    return r
