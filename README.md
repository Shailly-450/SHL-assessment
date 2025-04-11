# 🧠 SHL Assessment Recommendation System

A smart recommendation system for SHL assessments that suggests relevant assessments based on natural language job descriptions like:

> _"Java developers, 40 mins"_  
> _"Frontend role with React and TypeScript"_  

Built using Google's **Gemini API** for intelligent query understanding, and deployed with **Streamlit** for an interactive UI and **FastAPI** for API access.

---

## 🚀 Features

### 🔍 Intelligent Query Parsing
- Uses **Gemini API** to extract skills, duration, and assessment types from natural language queries.

### 📊 Recommendation Engine
- Ranks and scores assessments from a curated dataset.
- If fewer than 10 relevant assessments are found, Gemini generates additional suggestions based on the query.

### 🕸️ Web Scraping for Assessment Data
- Assessments are **scraped from the SHL website**.
- Extracted assessments are enhanced and stored in `assessments_enhanced.json`, used during recommendation.

### 🌐 Dual Deployment
- **Streamlit Web App**: User-friendly interface to input job descriptions and get recommendations.
- **FastAPI Endpoint**: REST API for programmatic access to the recommendations.

---

## 🔧 Setup & Installation (Local)

### 1. Clone the Repository
```bash
git clone https://github.com/Shailly-450/SHL-assessment.git
cd SHL-assessment
```
2. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate   # On Windows
```
3. Add Gemini API Key
Create a .env file in the root directory and add:
```bash
GEMINI_API_KEY=your_api_key_here
```
Get your key from Google AI Studio.

🖥️ Run Locally

Streamlit UI
```bash
streamlit run app.py
```
FastAPI Server
```bash
uvicorn app:app --reload
```
🌐 Working Model

Try it live:
(https://assessment-recommender.streamlit.app)

📁 File Overview

File/Folder	Description
app.py	Main Streamlit frontend
api/	FastAPI backend and routing logic
assessment_scraper.py	Web scraper to extract assessment data from SHL
assessments_enhanced.json	Enriched dataset used for recommendation logic
.env	Environment variables (API keys etc.)

👩‍💻 Author
Shailly Yadav
