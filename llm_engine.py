import json
import re
import ollama


MODEL_NAME = "llama3"


def call_llm(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a senior QA engineer. Always return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.2,
            "num_ctx": 8192
        }
    )

    return response["message"]["content"]


def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass

    raise ValueError("LLM did not return valid JSON")


def normalize_requirements(requirements):
    normalized = []

    for index, req in enumerate(requirements, start=1):
        normalized.append({
            "requirement_id": (
                req.get("requirement_id")
                or req.get("id")
                or req.get("req_id")
                or req.get("Requirement ID")
                or f"REQ_{index:03}"
            ),
            "requirement_text": (
                req.get("requirement_text")
                or req.get("requirement")
                or req.get("description")
                or req.get("text")
                or req.get("Requirement")
                or ""
            ),
            "requirement_type": (
                req.get("requirement_type")
                or req.get("type")
                or "Functional"
            ),
            "priority": (
                req.get("priority")
                or "Medium"
            )
        })

    return normalized


# def extract_requirements(brd_text):
#     prompt = f"""
# Extract atomic software requirements from the following BRD.

# BRD:
# {brd_text}

# Rules:
# - Break large requirements into smaller atomic requirements.
# - Each requirement should describe only one behavior or rule.
# - Do not skip validation rules.
# - Do not skip business rules.
# - Do not skip security rules.
# - Do not skip error conditions.
# - Return ONLY valid JSON.
# - Do not include markdown.
# - Do not include explanation.

# Return format:

# [
#   {{
#     "requirement_id": "REQ_001",
#     "requirement_text": "The system shall ...",
#     "requirement_type": "Functional",
#     "priority": "High"
#   }}
# ]
# """

#     raw = call_llm(prompt)
#     parsed = safe_json_parse(raw)
#     return normalize_requirements(parsed)
# <<<< -     --- Single pass to multipass update----->>>>>

def extract_requirements_by_category(brd_text, category):
    prompt = f"""
You are a senior business analyst and QA architect.

Extract ONLY {category} requirements from this BRD.

BRD:
{brd_text}

Rules:
- Extract as many atomic requirements as possible.
- One requirement = one behavior, rule, validation, condition, or constraint.
- Include implicit requirements if strongly implied.
- Do not combine multiple rules into one requirement.
- Return ONLY valid JSON.
- Do not include markdown or explanation.

Return format:

[
  {{
    "requirement_id": "TEMP_001",
    "requirement_text": "The system shall ...",
    "requirement_type": "{category}",
    "priority": "High"
  }}
]
"""

    raw = call_llm(prompt)
    parsed = safe_json_parse(raw)
    return parsed


def deduplicate_requirements(requirements):
    seen = set()
    unique = []

    for req in requirements:
        text = (
            req.get("requirement_text")
            or req.get("requirement")
            or req.get("description")
            or req.get("text")
            or ""
        ).strip().lower()

        if not text:
            continue

        normalized_text = " ".join(text.split())

        if normalized_text not in seen:
            seen.add(normalized_text)
            unique.append(req)

    return unique


def extract_requirements(brd_text):
    categories = [
        "Functional",
        "Validation",
        "Business Rule",
        "Security",
        "Authorization",
        "Authentication",
        "Error Handling",
        "Workflow",
        "Data Persistence",
        "Audit Logging",
        "Notification",
        "API",
        "UI",
        "Performance",
        "Boundary Constraint",
        "Data Quality"
    ]

    all_requirements = []

    for category in categories:
        print(f"Extracting {category} requirements...")

        try:
            extracted = extract_requirements_by_category(brd_text, category)
            all_requirements.extend(extracted)
        except Exception as e:
            print(f"Failed extracting {category}: {e}")

    unique_requirements = deduplicate_requirements(all_requirements)

    normalized = normalize_requirements(unique_requirements)

    for index, req in enumerate(normalized, start=1):
        req["requirement_id"] = f"REQ_{index:03}"

    return normalized

def normalize_test_cases(test_cases):
    normalized = []

    for index, tc in enumerate(test_cases, start=1):
        normalized.append({
            "test_case_id": (
                tc.get("test_case_id")
                or tc.get("id")
                or tc.get("Test Case ID")
                or f"TC_{index:03}"
            ),
            "requirement_id": (
                tc.get("requirement_id")
                or tc.get("req_id")
                or tc.get("Requirement ID")
                or "REQ_UNKNOWN"
            ),
            "scenario": (
                tc.get("scenario")
                or tc.get("test_scenario")
                or tc.get("description")
                or ""
            ),
            "test_type": (
                tc.get("test_type")
                or tc.get("type")
                or "Functional"
            ),
            "preconditions": (
                tc.get("preconditions")
                or tc.get("precondition")
                or "Application is accessible"
            ),
            "steps": (
                tc.get("steps")
                or tc.get("test_steps")
                or []
            ),
            "test_data": (
                tc.get("test_data")
                or tc.get("data")
                or {}
            ),
            "expected_result": (
                tc.get("expected_result")
                or tc.get("expected")
                or tc.get("expected_output")
                or ""
            ),
            "priority": (
                tc.get("priority")
                or "Medium"
            )
        })

    return normalized


def generate_test_cases_for_requirement(req):
    req_id = req["requirement_id"]
    req_text = req["requirement_text"]

    prompt = f"""
You are a senior QA architect.

Generate a large and exhaustive set of test cases for this single requirement.

Requirement ID: {req_id}
Requirement Text: {req_text}

Generate test cases across applicable categories:

1. Positive test cases
2. Negative test cases
3. Boundary value tests
4. Equivalence partition tests
5. Decision table tests
6. Field validation tests
7. Mandatory field tests
8. Format validation tests
9. Duplicate data tests
10. Security tests
11. Authorization tests
12. Error handling tests
13. Workflow tests
14. Data persistence tests
15. API validation tests
16. UI validation tests
17. Edge cases
18. Regression tests

Return ONLY valid JSON.
Do not include markdown.
Do not include explanation.

Format:

[
  {{
    "test_case_id": "TC_001",
    "requirement_id": "{req_id}",
    "scenario": "Test scenario",
    "test_type": "Positive",
    "preconditions": "Required setup",
    "steps": ["Step 1", "Step 2"],
    "test_data": {{}},
    "expected_result": "Expected result",
    "priority": "High"
  }}
]

Generate 15 to 25 test cases if possible.
"""

    raw = call_llm(prompt)
    parsed = safe_json_parse(raw)
    return normalize_test_cases(parsed)


def generate_exhaustive_llm_test_cases(requirements):
    all_test_cases = []

    for index, req in enumerate(requirements, start=1):
        print(f"Generating test cases for {req['requirement_id']} ({index}/{len(requirements)})")

        try:
            cases = generate_test_cases_for_requirement(req)
            all_test_cases.extend(cases)
        except Exception as e:
            print(f"Failed for {req['requirement_id']}: {e}")

    return all_test_cases