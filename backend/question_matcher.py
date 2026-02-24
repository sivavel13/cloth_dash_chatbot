from difflib import get_close_matches

def match_question(user_message: str, allowed_questions: list):
    matches = get_close_matches(
        user_message.lower(),
        allowed_questions,
        n=1,
        cutoff=0.6
    )
    print(matches)
    print(matches[0] if matches else "No match found")
    return matches[0] if matches else None