"""Placement-weighted score fairness simulation.

Standalone script (no Django). Verifies that placement-weighted coefficients
(1st=1.1, 2nd=1.075, 3rd=1.05, 4th=1.0) are fair — speakers who place 4th
in round 1 can still recover and reach the top.

Usage:
    python tabbycat/speakershuffler/simulate_fairness.py
"""

import random
from collections import defaultdict

# ── Parameters ──────────────────────────────────────────────────────────────
NUM_SPEAKERS = 32
NUM_TEAMS = 16
SPEAKERS_PER_TEAM = 2
TEAMS_PER_ROOM = 4
SPEAKERS_PER_ROOM = TEAMS_PER_ROOM * SPEAKERS_PER_TEAM  # 8
NUM_ROOMS = NUM_TEAMS // TEAMS_PER_ROOM  # 4
NUM_ROUNDS = 5
ITERATIONS = 10_000
BREAK_SIZE = 16

SCORE_MIN = 59
SCORE_MAX = 78
TEAM_TOTAL_MIN = SCORE_MIN * SPEAKERS_PER_TEAM  # 118
TEAM_TOTAL_MAX = SCORE_MAX * SPEAKERS_PER_TEAM  # 156

# Placement coefficients: 1st place → 1.1, 2nd → 1.075, 3rd → 1.05, 4th → 1.0
# In the codebase these are keyed by team points (3=1st, 2=2nd, 1=3rd, 0=4th)
COEFFICIENTS = {1: 1.06, 2: 1.04, 3: 1.02, 4: 1.0}


def generate_room_scores():
    """Generate scores for one room (4 teams of 2 speakers).

    Returns list of 4 tuples: (placement, score1, score2)
    where placement is 1..4 (1=first, 4=last).
    """
    # Pick 4 distinct team totals in [118, 156], sort descending
    totals = sorted(random.sample(range(TEAM_TOTAL_MIN, TEAM_TOTAL_MAX + 1), 4),
                    reverse=True)

    results = []
    for placement, total in enumerate(totals, start=1):
        # Split total into 2 individual scores in [59, 78] with |s1-s2| ≤ 5
        # s1 bounds: [59, 78], s2=T-s1 in [59, 78], |2*s1-T| ≤ 5
        lo = max(SCORE_MIN, total - SCORE_MAX, -(-((total - 5)) // 2))
        hi = min(SCORE_MAX, total - SCORE_MIN, (total + 5) // 2)
        s1 = random.randint(lo, hi)
        s2 = total - s1
        assert SCORE_MIN <= s1 <= SCORE_MAX and SCORE_MIN <= s2 <= SCORE_MAX, \
            f"Bad split: {s1}, {s2} from total {total}"
        results.append((placement, s1, s2))

    return results


def simulate_once():
    """Run one full 5-round simulation. Returns per-speaker stats."""

    # Track cumulative scores and R1 placement per speaker
    raw_totals = [0.0] * NUM_SPEAKERS
    weighted_totals = [0.0] * NUM_SPEAKERS
    r1_placement = [0] * NUM_SPEAKERS  # 1..4

    for rnd in range(NUM_ROUNDS):
        if rnd == 0:
            # Round 1: random assignment
            order = list(range(NUM_SPEAKERS))
            random.shuffle(order)
        else:
            # Rounds 2–5: rank by cumulative weighted score, chunk into rooms
            order = sorted(range(NUM_SPEAKERS),
                           key=lambda s: weighted_totals[s], reverse=True)

        # Process each room
        for room_idx in range(NUM_ROOMS):
            room_speakers = order[room_idx * SPEAKERS_PER_ROOM:
                                  (room_idx + 1) * SPEAKERS_PER_ROOM]

            # Random pairing within the room
            random.shuffle(room_speakers)
            teams = []
            for i in range(0, SPEAKERS_PER_ROOM, SPEAKERS_PER_TEAM):
                teams.append(room_speakers[i:i + SPEAKERS_PER_TEAM])

            # Generate scores for this room
            room_scores = generate_room_scores()

            # Randomly assign placements to teams
            placements = list(range(TEAMS_PER_ROOM))
            random.shuffle(placements)

            for team_idx, team in enumerate(teams):
                placement, s1, s2 = room_scores[placements[team_idx]]
                coeff = COEFFICIENTS[placement]

                for speaker, score in zip(team, [s1, s2]):
                    raw_totals[speaker] += score
                    weighted_totals[speaker] += score * coeff

                    if rnd == 0:
                        r1_placement[speaker] = placement

    return raw_totals, weighted_totals, r1_placement


def rank_speakers(totals):
    """Return 1-based ranks (1=best). Ties broken arbitrarily."""
    indexed = sorted(enumerate(totals), key=lambda x: x[1], reverse=True)
    ranks = [0] * len(totals)
    for rank, (idx, _) in enumerate(indexed, start=1):
        ranks[idx] = rank
    return ranks


def spearman_correlation(xs, ys):
    """Spearman rank correlation between two lists of ranks."""
    n = len(xs)
    d_sq = sum((x - y) ** 2 for x, y in zip(xs, ys))
    return 1.0 - (6.0 * d_sq) / (n * (n * n - 1))


def main():
    # Accumulators per R1 placement (1..4)
    raw_rank_sums = defaultdict(float)
    weighted_rank_sums = defaultdict(float)
    raw_break_counts = defaultdict(int)
    weighted_break_counts = defaultdict(int)
    placement_counts = defaultdict(int)
    best_raw_rank = defaultdict(lambda: NUM_SPEAKERS + 1)
    worst_raw_rank = defaultdict(lambda: 0)
    best_weighted_rank = defaultdict(lambda: NUM_SPEAKERS + 1)
    worst_weighted_rank = defaultdict(lambda: 0)

    # For Spearman correlation
    all_raw_ranks = []
    all_weighted_ranks = []

    for _ in range(ITERATIONS):
        raw_totals, weighted_totals, r1_placement = simulate_once()
        raw_ranks = rank_speakers(raw_totals)
        weighted_ranks = rank_speakers(weighted_totals)

        all_raw_ranks.append(raw_ranks[:])
        all_weighted_ranks.append(weighted_ranks[:])

        for speaker in range(NUM_SPEAKERS):
            p = r1_placement[speaker]
            placement_counts[p] += 1

            rr = raw_ranks[speaker]
            wr = weighted_ranks[speaker]

            raw_rank_sums[p] += rr
            weighted_rank_sums[p] += wr

            if rr <= BREAK_SIZE:
                raw_break_counts[p] += 1
            if wr <= BREAK_SIZE:
                weighted_break_counts[p] += 1

            best_raw_rank[p] = min(best_raw_rank[p], rr)
            worst_raw_rank[p] = max(worst_raw_rank[p], rr)
            best_weighted_rank[p] = min(best_weighted_rank[p], wr)
            worst_weighted_rank[p] = max(worst_weighted_rank[p], wr)

    # Spearman correlation between raw and weighted rankings
    correlations = []
    for raw_r, weighted_r in zip(all_raw_ranks, all_weighted_ranks):
        corr = spearman_correlation(raw_r, weighted_r)
        correlations.append(corr)
    avg_spearman = sum(correlations) / len(correlations)

    # ── Print results ───────────────────────────────────────────────────────
    print(f"Simulation: {ITERATIONS:,} iterations, {NUM_SPEAKERS} speakers, "
          f"{NUM_ROUNDS} rounds, break = top {BREAK_SIZE}")
    print(f"Coefficients: {COEFFICIENTS}")
    print()

    header = (f"{'R1 Place':>10} │ {'Count':>8} │ "
              f"{'Avg Rank (raw)':>15} │ {'Avg Rank (wtd)':>15} │ "
              f"{'Break % (raw)':>14} │ {'Break % (wtd)':>14} │ "
              f"{'Best/Worst (raw)':>17} │ {'Best/Worst (wtd)':>17}")
    print(header)
    print("─" * len(header))

    for p in sorted(COEFFICIENTS.keys()):
        n = placement_counts[p]
        avg_rr = raw_rank_sums[p] / n
        avg_wr = weighted_rank_sums[p] / n
        brk_rr = 100.0 * raw_break_counts[p] / n
        brk_wr = 100.0 * weighted_break_counts[p] / n
        bw_rr = f"{best_raw_rank[p]}–{worst_raw_rank[p]}"
        bw_wr = f"{best_weighted_rank[p]}–{worst_weighted_rank[p]}"

        label = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}[p]
        print(f"{label:>10} │ {n:>8,} │ {avg_rr:>15.2f} │ {avg_wr:>15.2f} │ "
              f"{brk_rr:>13.1f}% │ {brk_wr:>13.1f}% │ "
              f"{bw_rr:>17} │ {bw_wr:>17}")

    print()
    print(f"Avg Spearman correlation (raw vs weighted rankings): {avg_spearman:.4f}")

    # Fairness check
    r4_break_pct = 100.0 * weighted_break_counts[4] / placement_counts[4]
    r1_avg = weighted_rank_sums[1] / placement_counts[1]
    r4_avg = weighted_rank_sums[4] / placement_counts[4]
    gap = r4_avg - r1_avg

    print()
    if r4_break_pct > 20.0:
        print(f"✓ R1-4th break rate ({r4_break_pct:.1f}%) exceeds 20% threshold")
    else:
        print(f"✗ R1-4th break rate ({r4_break_pct:.1f}%) below 20% threshold")

    print(f"  R1-1st vs R1-4th avg weighted rank gap: {gap:.2f}")


if __name__ == "__main__":
    main()
