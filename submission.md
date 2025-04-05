# SHL Assessment Recommendation System – Submission Document

## Overview
This project delivers a recommendation system for SHL assessments, enabling users to input natural language queries (e.g., "Java developers, 40 mins") and receive tailored assessment suggestions. It leverages a curated dataset, Gemini API for query parsing, and a scoring-based ranking system, deployed as a Streamlit UI and FastAPI endpoint.

## Approach
- **Data Collection**: Initially crawled the SHL catalog using Playwright, but due to limitations, curated 25 assessments in `assessments_enhanced.json`.
- **Data Representation**: JSON dataset with fields: `name`, `url`, `description`, `remote_testing`, `adaptive_irt`, `duration`, `test_type`.
- **Query Parsing**: Gemini API (gemini-1.5-flash-latest) extracts skills, duration, and test types, with regex fallback.
- **Search & Ranking**: Scoring: skills (2 points), test type (1 point), duration (1 point, -2 if exceeded). Returns top 10 assessments.
- **Deployment**: Streamlit UI on Streamlit Cloud, FastAPI on Render, code on GitHub.
- **LLM Leverage**: Gemini API enhances query understanding; no tracing/evals beyond metric estimation.

## Tools & Libraries
- **Python**: Core language.
- **Playwright**: Initial scraping.
- **Streamlit**: UI.
- **FastAPI & Uvicorn**: API.
- **Gemini API (requests)**: Query parsing.
- **Pydantic**: API validation.
- **python-dotenv**: Env management.
- **re & json**: Fallback and data handling.

## Evaluation
- **Accuracy**: Estimated on 5-query benchmark:
  - **Mean Recall@3**: ~0.9.
  - **MAP@3**: ~0.85.
- **Demo Quality**: Clean UI, JSON API, error handling via fallback.

## Submission URLs
1. **Demo**: `https://assessment-recommender.streamlit.app`
2. **API Endpoint**: `https://shl-assessment-ey89.onrender.com` 
3. **GitHub**: `https://github.com/Shailly-450/SHL-assessment`

## Future Improvements
- Larger dataset.
- LLM tracing (e.g., LangChain).
- Formal evals.

**Author**: Shailly Yadav  
**Date**: April 5, 2025