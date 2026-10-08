def opposite_side(side: int, teams_in_debate: int) -> int:
    """Returns the side that is the "opposite" of the given side, for the
    purpose of side-balancing tools. For 2-team formats this swaps
    affirmative/negative (0<->1). For BP (4-team) formats this swaps
    opening government with closing opposition, and opening opposition
    with closing government (0<->3, 1<->2) — i.e. government-role sides
    swap with opposition-role sides, and opening swaps with closing.
    """
    return teams_in_debate - 1 - side
