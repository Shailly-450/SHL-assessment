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

# Query parsing (unchanged)
def parse_query(query: str) -> Dict:
    headers = {"Content-Type": "application/json"}
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
        generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
        json_match = re.search(r"```json\n(.*?)\n```", generated_text, re.DOTALL)
        parsed_result = json.loads(json_match.group(1)) if json_match else json.loads(generated_text)
        parsed_result["max_duration"] = float(parsed_result.get("max_duration", "inf")) if parsed_result.get("max_duration") else float("inf")
        return parsed_result
    except Exception as e:
        st.error(f"Error parsing query: {str(e)}")
        query = query.lower()
        skills = [s.strip() for s in re.findall(r"java|python|sql|javascript|cognitive|personality|behavioral", query)]
        duration_match = re.search(r"(\d+)\s*(min(ute)?s?)", query)
        max_duration = int(duration_match.group(1)) if duration_match else float('inf')
        test_types = [t for t in ["cognitive", "personality", "skill", "behavioral"] if t in query]
        return {"skills": skills, "max_duration": max_duration, "test_types": test_types}

# Scoring function (unchanged)
def score_assessment(assessment: Dict, query_info: Dict) -> float:
    score = 0
    name_lower = assessment["name"].lower()
    test_type_lower = assessment["test_type"].lower()
    for skill in query_info["skills"]:
        if skill in name_lower or skill in test_type_lower:
            score += 2
    if not query_info["test_types"] or test_type_lower in query_info["test_types"]:
        score += 1
    duration_str = assessment["duration"].lower()
    if duration_str != "not specified":
        duration = int(re.search(r"\d+", duration_str).group(0))
        if duration <= query_info["max_duration"]:
            score += 1
        else:
            score -= 2
    return score

# Generate assessments and recommendation with required attributes
def generate_assessments_and_recommendation(query: str, retrieved_assessments: List[Dict], query_info: Dict) -> tuple[str, List[Dict]]:
    headers = {"Content-Type": "application/json"}
    context = "\n".join([f"- {a['name']} ({a['test_type']}, {a['duration']}): {a['description']}" for a in retrieved_assessments]) if retrieved_assessments else "No matching assessments found in the catalog."
    num_to_generate = max(10 - len(retrieved_assessments), 0)  # Ensure at least 10 total
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""Given the user query: "{query}"
                And the following retrieved assessments from the SHL catalog:
                {context}
                Your task is to:
                1. If fewer than 10 assessments are provided, generate {num_to_generate} additional hypothetical assessments not more than 5. For each, include:
                   - Assessment Name
                   - URL (use "N/A (Generated)" since these are hypothetical)
                   - Remote Testing Support (Yes/No)
                   - Adaptive/IRT Support (Yes/No)
                   - Duration (in minutes)
                   - Test Type (e.g., Cognitive, Skill, Behavioral)
                   - Brief Description
                2. Provide a consise recommendation explaining the relevance of all assessments (retrieved and generated) to the query, assigning each a relevance score (0-100) based on how well it matches the query's skills, duration, and test types.
                Format the output as:
                ### Generated Assessments
                - Assessment Name (Test Type, Duration): Description [URL: N/A (Generated), Remote: Yes/No, Adaptive: Yes/No, Relevance: X]
                ### Recommendation
                [Your recommendation text]"""
            }]
        }]
    }
    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Parse generated assessments
        generated_assessments = []
        recommendation = ""
        in_generated_section = False
        in_recommendation_section = False
        
        for line in generated_text.split("\n"):
            if line.startswith("### Generated Assessments"):
                in_generated_section = True
                in_recommendation_section = False
                continue
            elif line.startswith("### Recommendation"):
                in_generated_section = False
                in_recommendation_section = True
                continue
            
            if in_generated_section:
                match = re.search(r"-\s*(.+?)\s*\((\w+),\s*(\d+\s*mins?)\):\s*(.+?)\s*\[URL:\s*N/A \(Generated\), Remote:\s*(Yes|No), Adaptive:\s*(Yes|No), Relevance:\s*(\d+)\]", line)
                if match:
                    name, test_type, duration, description, remote, adaptive, relevance = match.groups()
                    generated_assessments.append({
                        "name": name.strip(),
                        "url": "N/A (Generated Suggestion)",
                        "remote_testing": remote.strip(),
                        "adaptive_irt": adaptive.strip(),
                        "duration": duration.strip(),
                        "test_type": test_type.strip(),
                        "description": description.strip(),
                        "relevance": int(relevance)
                    })
            elif in_recommendation_section:
                recommendation += line + "\n"
        
        # Combine retrieved and generated assessments
        all_assessments = retrieved_assessments + generated_assessments
        if retrieved_assessments:
            # Assign relevance to retrieved assessments
            for a in retrieved_assessments:
                a["relevance"] = int(score_assessment(a, query_info) * 20)  # Scale score (0-5) to 0-100
        
        return recommendation.strip(), all_assessments[:10]  # Limit to 10
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        fallback_assessments = retrieved_assessments or []
        if len(fallback_assessments) < 10:
            for i in range(10 - len(fallback_assessments)):
                fallback_assessments.append({
                    "name": f"Custom {query_info['skills'][0] if query_info['skills'] else 'Generic'} Assessment {i+1}",
                    "url": "N/A (Generated)",
                    "remote_testing": "Yes",
                    "adaptive_irt": "No",
                    "duration": "30 mins",
                    "test_type": "Skill",
                    "description": f"Generated assessment for {query}.",
                    "relevance": 50
                })
        return f"Fallback recommendation for '{query}' with {len(retrieved_assessments)} catalog matches.", fallback_assessments[:10]

# Updated recommendation function
def recommend_assessments(query: str) -> Dict:
    query_info = parse_query(query)
    scored_assessments = [(score_assessment(a, query_info), a) for a in ASSESSMENTS]
    scored_assessments.sort(key=lambda x: x[0], reverse=True)
    top_assessments = [a for _, a in scored_assessments[:10] if _ > 0]  # Try to get up to 10
    
    # Generate response and additional assessments if needed
    recommendation, all_assessments = generate_assessments_and_recommendation(query, top_assessments, query_info)
    
    return {"assessments": all_assessments, "recommendation": recommendation}

# Updated Streamlit UI
def run_streamlit():
    st.title("SHL RAG Assessment Recommendation Tool (Powered by Gemini)")
    query = st.text_input("Enter your query (e.g., 'Java developers, 20 mins or Provide JD')")
    if query:
        result = recommend_assessments(query)
        st.write("### Recommendation")
        st.markdown(result["recommendation"])
        st.write("### Assessments")
        st.table([
            {
                "Name": a["name"],
                "URL": a["url"],
                "Remote Testing": a["remote_testing"],
                "Adaptive/IRT": a["adaptive_irt"],
                "Duration": a["duration"],
                "Test Type": a["test_type"],
                "Relevance": a["relevance"],
                "Description": a["description"]
            }
            for a in result["assessments"]
        ])

# FastAPI setup
app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/recommend")
def get_recommendations(query: str):
    result = recommend_assessments(query)
    return {"recommendation": result["recommendation"], "assessments": result["assessments"]}

if __name__ == "__main__":
    run_streamlit()