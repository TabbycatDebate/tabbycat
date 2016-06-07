

def gather_adj_feedback(adj, all_rounds, adj_feedbacks, all_debate_adjudicators):

    # Start off with their test scores
    feedback_data = [{'x': 0, 'y': adj.test_score, 'position': "Test Score"}]

    for r in all_rounds:
        # Filter all the feedback to focus on this particular rouond
        adj_round_feedbacks = [f for f in adj_feedbacks if (f.source_adjudicator and f.source_adjudicator.debate.round == r)]
        adj_round_feedbacks.extend([f for f in adj_feedbacks if (f.source_team and f.source_team.debate.round == r)])

        if len(adj_round_feedbacks) > 0:
            debates = [fb.source_team.debate for fb in adj_round_feedbacks if fb.source_team]
            debates.extend([fb.source_adjudicator.debate for fb in adj_round_feedbacks if fb.source_adjudicator])
            adj_da = next((da for da in all_debate_adjudicators if (da.adjudicator == adj and da.debate == debates[0])), None)
            if adj_da:
                if adj_da.type == adj_da.TYPE_CHAIR:
                    adj_type = "Chair"
                elif adj_da.type == adj_da.TYPE_PANEL:
                    adj_type = "Panellist"
                elif adj_da.type == adj_da.TYPE_TRAINEE:
                    adj_type = "Trainee"

                total_score = [f.score for f in adj_round_feedbacks]
                average_score = round(sum(total_score) / len(total_score), 2)

                # Creating the object list for the graph
                feedback_data.append({
                    'x': r.seq,
                    'y': average_score,
                    'position': adj_type,
                })

    return feedback_data


def gather_adj_scores(adj, adj_scores, debate_adjudications):
    # Processing scores to get average margins
    adj.debates = len(debate_adjudications)

    if len(adj_scores) > 0:
        adj.avg_score = sum(s.score for s in adj_scores) / len(adj_scores)

        # ballot_ids = [score.ballot_submission for score in adj_scores]
        # ballot_ids = sorted(set([b.id for b in ballot_ids])) # Deduplication of ballot IDS
        # ballot_margins = []
        #
        # for ballot_id in ballot_ids:
        #     # For each unique ballot id total its scores
        #     print(ballot_id)
        #     print([a.id for a in adj_scores])
        #     single_round = adj_scores.filter(ballot_submission=ballot_id)
        #     scores = [s.score for s in single_round] # TODO this is slow - should be prefetched
        #     slice_end = len(scores)
        #     teamA = sum(scores[:len(scores)/2])
        #     teamB = sum(scores[len(scores)/2:])
        #     ballot_margins.append(max(teamA, teamB) - min(teamA, teamB))
        #
        # adj.avg_margin = sum(ballot_margins) / len(ballot_margins)
        return adj

    else:
        adj.avg_score = None
        adj.avg_margin = None
        return adj
