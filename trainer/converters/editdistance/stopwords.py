
class Stopwords(object):
    # Since we remove by substring, this list must be sorted such that
    # longer forms are taken out first. (e.g. if "Co" is before "Corp",
    # we end up with "rp" being left.)
    words = [
        "Companies",
        "Company",
        "Corporation",
        "Corp",
        "Co",
        "Cos",
        "Group",
        "Incorporated",
        "Inc",
        "Limited",
        "Ltd",
        "LLLP",
        "LP",
        "The",
        "Holding",
        "and"
    ]
