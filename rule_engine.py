def get_requirement_text(req):
    return (
        req.get("requirement_text")
        or req.get("requirement")
        or req.get("description")
        or req.get("text")
        or req.get("Requirement")
        or ""
    )


def get_requirement_id(req, count):
    return req.get("requirement_id") or req.get("id") or f"REQ_{count:03}"


def get_priority(req):
    return req.get("priority") or "Medium"


def generate_boundary_tests(requirements):
    test_cases = []
    count = 1

    for req in requirements:
        text = get_requirement_text(req).lower()
        req_id = get_requirement_id(req, count)

        if "at least" in text or "minimum" in text or "min" in text or "maximum" in text or "length" in text:
            test_cases.append({
                "test_case_id": f"BVA_{count:03}",
                "requirement_id": req_id,
                "scenario": "Boundary value validation",
                "test_type": "Boundary",
                "preconditions": "User is on the relevant input screen",
                "steps": [
                    "Enter value below boundary",
                    "Enter value at boundary",
                    "Enter value above boundary"
                ],
                "test_data": {
                    "below_boundary": "invalid",
                    "at_boundary": "valid",
                    "above_boundary": "valid"
                },
                "expected_result": "System should reject invalid boundary and accept valid boundary values",
                "priority": get_priority(req)
            })
            count += 1

    return test_cases


def generate_decision_table_tests(requirements):
    test_cases = []
    count = 1

    for req in requirements:
        text = get_requirement_text(req).lower()
        req_id = get_requirement_id(req, count)

        if "if" in text or "when" in text or "condition" in text or "then" in text:
            test_cases.append({
                "test_case_id": f"DT_{count:03}",
                "requirement_id": req_id,
                "scenario": "Decision table business rule validation",
                "test_type": "Decision Table",
                "preconditions": "Business rule conditions are available",
                "steps": [
                    "Identify condition combinations",
                    "Execute each condition combination",
                    "Verify expected business outcome"
                ],
                "test_data": {
                    "condition_1": "true",
                    "condition_2": "false"
                },
                "expected_result": "System should follow the defined business rule correctly",
                "priority": get_priority(req)
            })
            count += 1

    return test_cases


def generate_negative_tests(requirements):
    test_cases = []
    count = 1

    for req in requirements:
        req_id = get_requirement_id(req, count)

        test_cases.append({
            "test_case_id": f"NEG_{count:03}",
            "requirement_id": req_id,
            "scenario": "Negative validation for requirement",
            "test_type": "Negative",
            "preconditions": "Application is accessible",
            "steps": [
                "Provide invalid or missing input",
                "Submit the request",
                "Observe validation response"
            ],
            "test_data": {
                "invalid_input": "null / blank / invalid format"
            },
            "expected_result": "System should reject invalid input and show proper error message",
            "priority": get_priority(req)
        })
        count += 1

    return test_cases