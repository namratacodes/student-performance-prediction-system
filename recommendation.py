def recommend(attendance, study_hours, test_score):

    suggestions = []

    if attendance < 75:
        suggestions.append("Increase attendance above 75%")

    if study_hours < 3:
        suggestions.append("Study at least 3 hours daily")

    if test_score < 50:
        suggestions.append("Focus on weak subjects")

    return suggestions