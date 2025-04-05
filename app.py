import json
import re
from typing import List, Dict
import streamlit as st
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Load enhanced assessments
with open("data/assessments_enhanced.json", 'r') as f:
    ASSESSMENTS = json.load(f)

# Query parsing using Gemini API
def parse_query(query: str) -> Dict:
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""Extract the following from this query for an assessment recommendation system:
                - Skills (e.g., Java, Python, SQL)
                - Maximum duration in minutes (e.g., 40 mins)
                - Test types (e.g., cognitive, personality, skill, behavioral)
                Query: "{query}"
                Return the result as a JSON object with keys: 'skills', 'max_duration', 'test_types'."""
            }]
        }]
    }
    
    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract the generated text (Gemini returns it in a nested structure)
        generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Clean up and parse the JSON from the response
        json_match = re.search(r"```json\n(.*?)\n```", generated_text, re.DOTALL)
        if json_match:
            parsed_result = json.loads(json_match.group(1))
        else:
            parsed_result = json.loads(generated_text)  # Fallback if no ```json``` markers
        
        # Ensure max_duration is a number (default to infinity if not found)
        parsed_result["max_duration"] = float(parsed_result.get("max_duration", "inf")) if parsed_result.get("max_duration") else float("inf")
        return parsed_result
    
    except Exception as e:
        st.error(f"Error parsing query with Gemini API: {str(e)}")
        # Fallback to basic parsing
        query = query.lower()
        skills = [s.strip() for s in re.findall(r"java|python|sql|javascript|cognitive|personality|behavioral", query)]
        duration_match = re.search(r"(\d+)\s*(min(ute)?s?)", query)
        max_duration = int(duration_match.group(1)) if duration_match else float('inf')
        test_types = [t for t in ["cognitive", "personality", "skill", "behavioral"] if t in query]
        return {"skills": skills, "max_duration": max_duration, "test_types": test_types}

# Scoring function
def score_assessment(assessment: Dict, query_info: Dict) -> float:
    score = 0
    name_lower = assessment["name"].lower()
    test_type_lower = assessment["test_type"].lower()

    # Skill match
    for skill in query_info["skills"]:
        if skill in name_lower or skill in test_type_lower:
            score += 2

    # Test type match
    if not query_info["test_types"] or test_type_lower in query_info["test_types"]:
        score += 1

    # Duration match
    duration_str = assessment["duration"].lower()
    if duration_str != "not specified":
        duration = int(re.search(r"\d+", duration_str).group(0))
        if duration <= query_info["max_duration"]:
            score += 1
        else:
            score -= 2

    return score

# Recommendation function
def recommend_assessments(query: str) -> List[Dict]:
    query_info = parse_query(query)
    scored_assessments = [(score_assessment(a, query_info), a) for a in ASSESSMENTS]
    scored_assessments.sort(key=lambda x: x[0], reverse=True)
    top_assessments = [a for _, a in scored_assessments[:10] if _ > 0]  # Min score > 0
    return top_assessments if top_assessments else [scored_assessments[0][1]]  # At least 1

# Streamlit UI
def run_streamlit():
    st.title("SHL Assessment Recommendation System (Powered by Gemini)")
    query = st.text_input("Enter your query (e.g., 'Java developers who collaborate, 40 mins')")
    if query:
        results = recommend_assessments(query)
        st.write("### Recommended Assessments")
        st.table([
            {
                "Name": a["name"],
                "URL": a["url"],
                "Remote Testing": a["remote_testing"],
                "Adaptive/IRT": a["adaptive_irt"],
                "Duration": a["duration"],
                "Test Type": a["test_type"]
            } for a in results
        ])

# FastAPI setup
app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/recommend")
def get_recommendations(query: str):
    results = recommend_assessments(query)
    return {"recommendations": results}

if __name__ == "__main__":
    import uvicorn
    # Run Streamlit in one terminal: `streamlit run this_script.py`
    # Run FastAPI in another: `uvicorn this_script:app --reload`
    run_streamlit()