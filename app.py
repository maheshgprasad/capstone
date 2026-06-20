import streamlit as st
import pandas as pd
from llm_engine import extract_requirements, generate_exhaustive_llm_test_cases
#from llm_engine import extract_requirements, generate_llm_test_cases
from rule_engine import (
    generate_boundary_tests,
    generate_decision_table_tests,
    generate_negative_tests
)
from metrics import requirement_coverage, hallucination_check

import json


def make_dataframe_safe(data):
    safe_data = []

    for row in data:
        safe_row = {}

        for key, value in row.items():
            if isinstance(value, (dict, list)):
                safe_row[key] = json.dumps(value, ensure_ascii=False)
            elif value is None:
                safe_row[key] = ""
            else:
                safe_row[key] = str(value)

        safe_data.append(safe_row)

    return safe_data

st.title("BRD-Based Test Case Generator")
st.write("Local LLM-powered test case generator using Ollama")

uploaded_file = st.file_uploader("Upload BRD text file", type=["txt"])

if uploaded_file:
    brd_text = uploaded_file.read().decode("utf-8")

    st.subheader("Uploaded BRD")
    st.text_area("BRD Content", brd_text, height=200)

    if st.button("Generate Test Cases"):
        requirements = extract_requirements(brd_text)
        st.write("Raw extracted requirements:", requirements)

        #llm_tests = generate_llm_test_cases(requirements)
        llm_tests = generate_exhaustive_llm_test_cases(requirements)
        bva_tests = generate_boundary_tests(requirements)
        decision_tests = generate_decision_table_tests(requirements)
        negative_tests = generate_negative_tests(requirements)

        all_tests = llm_tests + bva_tests + decision_tests + negative_tests

        coverage = requirement_coverage(requirements, all_tests)
        hallucination = hallucination_check(requirements, all_tests)

        st.subheader("Extracted Requirements")
        #st.dataframe(pd.DataFrame(requirements))
        st.dataframe(pd.DataFrame(make_dataframe_safe(requirements)))

        st.subheader("Generated Test Cases")
        #st.dataframe(pd.DataFrame(all_tests))
        st.dataframe(pd.DataFrame(make_dataframe_safe(all_tests)))

        st.subheader("Coverage Report")
        st.json(coverage)

        st.subheader("Hallucination Check")
        st.json(hallucination)

        st.download_button(
            "Download Test Cases CSV",
            #pd.DataFrame(all_tests).to_csv(index=False),
            pd.DataFrame(make_dataframe_safe(all_tests)).to_csv(index=False),
            "test_cases.csv",
            "text/csv"
        )