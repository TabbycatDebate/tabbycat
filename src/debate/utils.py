def pair_list(ls):
    r = []
    for i in range(len(ls)/2):
        r.append((ls[2*i], ls[2*i+1]))
    return r
