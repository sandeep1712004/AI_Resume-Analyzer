# AI Resume Analyzer using NLP

An AI-powered Resume Analyzer developed using Python, Flask, and Natural Language Processing (NLP) that analyzes resumes, extracts skills, calculates ATS scores, compares resumes with job descriptions, and ranks candidates intelligently.

## Features

### Resume Parsing
- Upload PDF, DOCX, and TXT resumes
- Extract resume content automatically using PyMuPDF (fitz)
- Detect resume sections:
  - Education
  - Experience
  - Skills
  - Projects
  - Certifications
  - Contact Information

### NLP-Based Analysis
- Keyword extraction using NLP
- Skill identification and categorization
- Resume quality evaluation
- Resume completeness analysis

### ATS Score Calculation
- Calculates Applicant Tracking System (ATS) compatibility score
- Evaluates:
  - Resume structure
  - Contact details completeness
  - Skill coverage
  - Content quality
  - Impact language

### Candidate Ranking System
- Compare resumes with job descriptions
- Match keywords intelligently
- Identify missing skills
- Calculate candidate ranking scores

### AI Recommendations
- Suggest resume improvements
- Identify missing resume sections
- Recommend profile enhancements

### Dashboard Features
- Resume score visualization
- Skill breakdown
- Job match percentage
- Candidate ranking insights
- Resume analytics dashboard

---

## Tech Stack

### Backend
- Python
- Flask
- Flask-CORS

### NLP & AI
- Natural Language Processing (NLP)
- Scikit-Learn
- Custom TF-IDF Keyword Extraction

### PDF Processing
- PyMuPDF (fitz)
- python-docx

### Frontend
- HTML
- CSS
- JavaScript

### Database (Optional)
- SQLite / MySQL

---

## Project Architecture

```
AI_Resume_Analyzer/

│
├── uploads/
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│
├── app.py
├── requirements.txt
├── README.md
│
└── venv/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/sandeep17122004/AI_Resume_Analyzer.git

cd AI_Resume_Analyzer
```

---

### Create Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Install NLP Models

```bash
python -m spacy download en_core_web_sm
```

---

### Run Application

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## Requirements

```
flask>=2.3.0
flask-cors>=4.0.0
pymupdf>=1.23.0
python-docx>=1.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
nltk>=3.8.0
spacy>=3.7.0
```

---

## Resume Evaluation Metrics

The ATS score is calculated based on:

| Metric | Weight |
|----------|---------|
| Contact Information | 10 |
| Resume Structure | 25 |
| Skills Coverage | 30 |
| Content Quality | 15 |
| Impact Language | 20 |

Total Score = 100

---

## NLP Pipeline

1. Resume Upload
2. Text Extraction (PyMuPDF)
3. Text Cleaning
4. Tokenization
5. Skill Extraction
6. Keyword Identification
7. Resume Section Detection
8. ATS Score Generation
9. Candidate Ranking
10. Job Description Matching

---

## Future Improvements

- Deep Learning-based resume ranking
- Semantic similarity using Transformers
- LLM integration
- Multi-resume ranking leaderboard
- Resume PDF report generation
- Admin dashboard authentication
- MongoDB integration

---

## Author

Sandeep A

Bachelor of Technology – Information Technology

Machine Learning and Software Development Enthusiast

LinkedIn:
linkedin.com/in/sandeep1712004

GitHub:
github.com/sandeep1712004

---

## License

This project is developed for educational and learning purposes.
