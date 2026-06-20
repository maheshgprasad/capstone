def get_requirement_id(req, count=None):
    return (
        req.get("requirement_id")
        or req.get("id")
        or req.get("req_id")
        or req.get("Requirement ID")
        or req.get("requirementId")
        or (f"REQ_{count:03}" if count else None)
    )


def requirement_coverage(requirements, test_cases):
    total = len(requirements)

    covered = set(
        tc.get("requirement_id")
        or tc.get("req_id")
        or tc.get("id")
        for tc in test_cases
        if tc.get("requirement_id") or tc.get("req_id") or tc.get("id")
    )

    uncovered = []

    for index, req in enumerate(requirements, start=1):
        req_id = get_requirement_id(req, index)

        if req_id not in covered:
            uncovered.append(req_id)

    coverage = round(((total - len(uncovered)) / total) * 100, 2) if total else 0

    return {
        "total_requirements": total,
        "covered_requirements": total - len(uncovered),
        "coverage_percentage": coverage,
        "uncovered_requirements": uncovered
    }


def hallucination_check(requirements, test_cases):
    valid_req_ids = {
        get_requirement_id(req, index)
        for index, req in enumerate(requirements, start=1)
    }

    hallucinated = []

    for tc in test_cases:
        tc_req_id = (
            tc.get("requirement_id")
            or tc.get("req_id")
            or tc.get("id")
        )

        if tc_req_id not in valid_req_ids:
            hallucinated.append(tc)

    return {
        "hallucinated_test_cases": len(hallucinated),
        "hallucination_risk": "High" if hallucinated else "Low"
    }