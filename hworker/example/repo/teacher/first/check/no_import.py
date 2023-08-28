def validator(solution):
    for content in solution.content.values():
        if "import" in content:
            return 0.0
    return 1.0
