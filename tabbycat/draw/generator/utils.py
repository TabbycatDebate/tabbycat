"""Miscellaneous utilities for the draw."""


def ispow2(n):
    """Returns True if n is a power of 2. Works for positive integers only."""
    return n & (n - 1) == 0


def nextpow2(n):
    return 1 << (n-1).bit_length()


def partial_break_round_split(break_size):
    """Returns a tuple `(debates, bypassing)`, where `debating` is how many
    debates there is in the first break round, and `bypassing` is how many
    teams will bypass the first break round, qualifying directly for the
    second."""

    assert break_size > 1, "break rounds only make sense for break_size > 1 (found %d)" % (break_size,)

    teams_in_second_break_round = nextpow2(break_size) // 2
    debates = break_size - teams_in_second_break_round
    bypassing = teams_in_second_break_round - debates

    assert 2*debates + bypassing == break_size, "2 * %d teams debating + %d teams bypassing doesn't add to break size %d" % (debates, bypassing, break_size)
    assert debates > 0, "%d <= 0 debates in first break round (%d teams bypassing)" % (debates, bypassing)
    assert bypassing >= 0, "%d < 0 teams bypassing (%d debates)" % (bypassing, debates)
    return debates, bypassing
