# SHL Assessment Recommendation System

This project is a recommendation system for SHL assessments, designed to suggest relevant assessments based on natural language queries (e.g., "Java developers, 40 mins"). It uses the **Gemini API** for intelligent query parsing and is deployed as a Streamlit UI and FastAPI endpoint.

## Features
- **Query Parsing**: Extracts skills, duration, and test types from user queries using Google's Gemini API.
- **Recommendation Engine**: Scores and ranks assessments from a curated dataset (`assessments_enhanced.json`).
- **Deployment**:
  - **Streamlit UI**: Interactive web app for users to input queries and view recommendations.
  - **FastAPI API**: API returning JSON recommendations for programmatic access.


## Setup and Installation (Local)
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shailly-450/SHL-assessment.git
   cd SHL-assessment
2. **Set Up Virtual Environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Mac/Linux
  # venv\Scripts\activate  # On Windows
```
3. **Add Gemini API Key:
Create a .env file:
GEMINI_API_KEY=your_api_key_here

4. **Get your key from Google AI Studio.
5. **Run Locally:
Streamlit UI:
```bash
streamlit run app.py
```
FastAPI:
```bash
uvicorn app:app --reload
```

Author
Shailly Yadav

