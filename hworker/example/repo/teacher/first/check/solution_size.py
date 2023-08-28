def validator(solution, size):
    for content in solution.content.values():
        if len(content.split()) > size:
            return 0.0
    return 1.0
