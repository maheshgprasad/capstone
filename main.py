import os
import json
import pandas as pd

#from llm_engine import extract_requirements, generate_llm_test_cases
from llm_engine import extract_requirements, generate_exhaustive_llm_test_cases
from rule_engine import (
    generate_boundary_tests,
    generate_decision_table_tests,
    generate_negative_tests
)
from metrics import requirement_coverage, hallucination_check


os.makedirs("outputs", exist_ok=True)


def read_brd(path="brd.txt"):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def save_json(name, data):
    with open(f"outputs/{name}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_csv(name, data):
    pd.DataFrame(data).to_csv(f"outputs/{name}.csv", index=False)


def create_traceability_matrix(requirements, test_cases):
    matrix = []

    for req in requirements:
        linked = [
            tc["test_case_id"]
            for tc in test_cases
            if tc.get("requirement_id") == req["requirement_id"]
        ]

        matrix.append({
            "requirement_id": req["requirement_id"],
            "requirement_text": req["requirement_text"],
            "linked_test_cases": ", ".join(linked),
            "coverage_status": "Covered" if linked else "Not Covered"
        })

    return matrix


def main():
    print("Reading BRD...")
    brd_text = read_brd()

    print("Extracting requirements using local LLM...")
    requirements = extract_requirements(brd_text)

    print("Generating LLM-based test cases...")
    #llm_tests = generate_llm_test_cases(requirements)
    llm_tests = generate_exhaustive_llm_test_cases(requirements)

    print("Generating rule-based BVA tests...")
    bva_tests = generate_boundary_tests(requirements)

    print("Generating decision table tests...")
    decision_tests = generate_decision_table_tests(requirements)

    print("Generating negative tests...")
    negative_tests = generate_negative_tests(requirements)

    all_test_cases = llm_tests + bva_tests + decision_tests + negative_tests

    traceability = create_traceability_matrix(requirements, all_test_cases)

    coverage_report = requirement_coverage(requirements, all_test_cases)
    hallucination_report = hallucination_check(requirements, all_test_cases)

    final_report = {
        "coverage_report": coverage_report,
        "hallucination_report": hallucination_report,
        "total_test_cases": len(all_test_cases)
    }

    save_json("requirements", requirements)
    save_json("test_cases", all_test_cases)
    save_json("traceability_matrix", traceability)
    save_json("validation_report", final_report)

    save_csv("requirements", requirements)
    save_csv("test_cases", all_test_cases)
    save_csv("traceability_matrix", traceability)

    print("\nCompleted successfully.")
    print(json.dumps(final_report, indent=4))


if __name__ == "__main__":
    main()