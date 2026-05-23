from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import re
import json
from collections import Counter
import math

# ─── FIX 1: Use fitz (PyMuPDF) instead of PyPDF2 ───────────────────────────
# PyPDF2 is outdated and fails on many modern PDFs.
# Install with: pip install pymupdf
try:
    import fitz
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

app = Flask(__name__)
CORS(app)

# ─── FIX 2: Create uploads/ folder at app level, NOT inside __main__ ────────
# Flask's debug reloader forks a child process that skips __main__,
# so the folder never gets created when debug=True.
os.makedirs('uploads', exist_ok=True)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ─── NLP Utilities ──────────────────────────────────────────────────────────

STOPWORDS = set([
    'a','an','the','and','or','but','in','on','at','to','for','of','with',
    'by','from','up','about','into','through','during','is','are','was',
    'were','be','been','being','have','has','had','do','does','did','will',
    'would','could','should','may','might','can','this','that','these',
    'those','i','me','my','myself','we','our','you','your','he','she','it',
    'they','them','their','what','which','who','how','when','where','why',
    'all','both','each','few','more','most','other','some','such','no',
    'not','only','same','so','than','too','very','just','as','if','its'
])

def tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b[a-z][a-z0-9+#.]*\b', text)
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]

# ─── FIX 3: Replaced PyPDF2 extractor with fitz (far more reliable) ─────────
def extract_text_from_pdf(file_path):
    text = ""
    if not PDF_SUPPORT:
        return "Error: PyMuPDF not installed. Run: pip install pymupdf"
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        text = f"Error reading DOCX: {e}"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', errors='ignore') as f:
        return f.read()

# ─── Skill Taxonomies ────────────────────────────────────────────────────────

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python","java","javascript","typescript","c++","c#","ruby","go","golang",
        "rust","swift","kotlin","php","scala","r","matlab","perl","bash","shell",
        "html","css","sql","dart","julia"
    ],
    "Frameworks & Libraries": [
        "react","angular","vue","django","flask","fastapi","spring","express",
        "node","nodejs","tensorflow","pytorch","keras","sklearn","scikit",
        "pandas","numpy","scipy","flutter","nextjs","nuxt","rails","laravel",
        "bootstrap","tailwind","jquery","redux","graphql"
    ],
    "Cloud & DevOps": [
        "aws","azure","gcp","docker","kubernetes","jenkins","terraform","ansible",
        "ci/cd","devops","linux","unix","git","github","gitlab","bitbucket",
        "nginx","apache","heroku","vercel","lambda","s3","ec2","cloudformation"
    ],
    "Data & AI": [
        "machine learning","deep learning","nlp","computer vision","data science",
        "big data","hadoop","spark","kafka","airflow","etl","tableau","power bi",
        "elasticsearch","mongodb","postgresql","mysql","redis","cassandra","data analysis"
    ],
    "Soft Skills": [
        "leadership","communication","teamwork","problem solving","critical thinking",
        "project management","agile","scrum","collaboration","mentoring","presentation",
        "time management","analytical"
    ]
}

SECTION_PATTERNS = {
    "education": r'\b(education|degree|university|college|bachelor|master|phd|diploma|gpa|graduated)\b',
    "experience": r'\b(experience|work|employment|position|role|company|organization|intern|job)\b',
    "skills": r'\b(skills|technologies|tools|proficient|expertise|competencies|tech stack)\b',
    "projects": r'\b(project|built|developed|created|designed|implemented|launched)\b',
    "certifications": r'\b(certification|certified|certificate|credential|license|award)\b',
    "contact": r'\b(email|phone|linkedin|github|portfolio|address|contact)\b',
    "summary": r'\b(summary|objective|profile|about|overview|professional summary)\b',
}

# ─── Analysis Engine ─────────────────────────────────────────────────────────

def extract_contact_info(text):
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phone = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    linkedin = re.findall(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    github = re.findall(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    return {
        "email": email[0] if email else None,
        "phone": phone[0].strip() if phone else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
    }

def extract_skills(text):
    text_lower = text.lower()
    found = {}
    for category, skills in SKILL_CATEGORIES.items():
        found[category] = []
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found[category].append(skill)
    return found

def detect_sections(text):
    text_lower = text.lower()
    present = {}
    for section, pattern in SECTION_PATTERNS.items():
        present[section] = bool(re.search(pattern, text_lower))
    return present

def compute_tfidf_keywords(text, top_n=15):
    tokens = tokenize(text)
    freq = Counter(tokens)
    total = len(tokens)
    if total == 0:
        return []
    scored = []
    for word, count in freq.items():
        tf = count / total
        idf = math.log(1 + 1 / (count / total))
        scored.append((word, round(tf * idf, 5), count))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"word": w, "score": s, "count": c} for w, s, c in scored[:top_n]]

def score_resume(text, sections, skills, contact):
    scores = {}

    contact_score = sum([
        3 if contact.get("email") else 0,
        2 if contact.get("phone") else 0,
        3 if contact.get("linkedin") else 0,
        2 if contact.get("github") else 0,
    ])
    scores["Contact Info"] = {"score": contact_score, "max": 10}

    section_weights = {"summary": 4, "experience": 6, "education": 5,
                       "skills": 5, "projects": 3, "certifications": 2}
    section_score = sum(w for s, w in section_weights.items() if sections.get(s))
    scores["Section Structure"] = {"score": section_score, "max": 25}

    total_skills = sum(len(v) for v in skills.values())
    skill_score = min(30, total_skills * 2)
    scores["Skills & Tech"] = {"score": skill_score, "max": 30}

    word_count = len(text.split())
    if 300 <= word_count <= 700:
        length_score = 15
    elif 200 <= word_count < 300 or 700 < word_count <= 900:
        length_score = 10
    elif word_count < 200:
        length_score = 4
    else:
        length_score = 7
    scores["Content Depth"] = {"score": length_score, "max": 15}

    action_verbs = [
        "led","built","developed","designed","created","managed","launched",
        "improved","reduced","increased","delivered","achieved","implemented",
        "optimized","collaborated","spearheaded","transformed","generated",
        "automated","mentored","scaled","deployed","architected"
    ]
    text_lower = text.lower()
    found_verbs = [v for v in action_verbs if re.search(r'\b' + v + r'\b', text_lower)]
    verb_score = min(20, len(found_verbs) * 2)
    scores["Impact Language"] = {"score": verb_score, "max": 20}

    total = sum(v["score"] for v in scores.values())
    max_total = sum(v["max"] for v in scores.values())

    return scores, round((total / max_total) * 100, 1)

def get_grade(score):
    if score >= 85: return "A+", "Exceptional"
    if score >= 75: return "A", "Strong"
    if score >= 65: return "B+", "Good"
    if score >= 55: return "B", "Average"
    if score >= 45: return "C", "Needs Work"
    return "D", "Major Improvements Needed"

def generate_suggestions(scores, sections, skills, contact, word_count):
    suggestions = []

    if not contact.get("email"):
        suggestions.append({"type": "critical", "text": "Add a professional email address — recruiters need to reach you."})
    if not contact.get("linkedin"):
        suggestions.append({"type": "important", "text": "Include your LinkedIn profile URL to increase visibility."})
    if not contact.get("github") and skills.get("Programming Languages"):
        suggestions.append({"type": "important", "text": "Add your GitHub link to showcase code samples."})

    if not sections.get("summary"):
        suggestions.append({"type": "important", "text": "Add a professional summary at the top — it's the first thing read."})
    if not sections.get("projects"):
        suggestions.append({"type": "tip", "text": "Include a Projects section to demonstrate real-world application of skills."})
    if not sections.get("certifications"):
        suggestions.append({"type": "tip", "text": "Certifications (AWS, Google, etc.) add credibility — include if you have them."})

    if word_count < 250:
        suggestions.append({"type": "critical", "text": f"Resume is too short ({word_count} words). Aim for 400–650 words with detailed experience."})
    elif word_count > 900:
        suggestions.append({"type": "important", "text": f"Resume may be too long ({word_count} words). Try to keep it concise (under 700 words)."})

    total_skills = sum(len(v) for v in skills.values())
    if total_skills < 5:
        suggestions.append({"type": "critical", "text": "Very few skills detected. Expand your skills section with specific tools and technologies."})
    if not skills.get("Cloud & DevOps"):
        suggestions.append({"type": "tip", "text": "Cloud/DevOps skills (Docker, AWS, CI/CD) are in high demand — consider adding them."})

    if scores["Impact Language"]["score"] < 10:
        suggestions.append({"type": "important", "text": "Use more action verbs like 'led', 'built', 'optimized', 'launched' to show impact."})

    if not suggestions:
        suggestions.append({"type": "tip", "text": "Great resume! Consider tailoring keywords to match specific job descriptions."})

    return suggestions

def rank_against_job(resume_text, job_description):
    if not job_description.strip():
        return None

    resume_tokens = set(tokenize(resume_text))
    job_tokens = set(tokenize(job_description))

    if not job_tokens:
        return None

    intersection = resume_tokens & job_tokens
    match_score = round(len(intersection) / len(job_tokens) * 100, 1)

    missing = list(job_tokens - resume_tokens)[:12]
    matched = list(intersection)[:12]

    return {
        "match_score": min(match_score, 100),
        "matched_keywords": matched,
        "missing_keywords": missing,
        "recommendation": "Strong Match" if match_score >= 60 else
                         "Moderate Match" if match_score >= 35 else "Needs Tailoring"
    }

# ─── Routes ──────────────────────────────────────────────────────────────────

# ─── FIX 4: Flask looks for templates in a 'templates/' subfolder ────────────
# Make sure index.html is at:  templates/index.html  (not next to app.py)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = ""
    job_description = request.form.get('job_description', '')

    if 'resume_file' in request.files and request.files['resume_file'].filename:
        file = request.files['resume_file']
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        ext = filename.lower().rsplit('.', 1)[-1]
        if ext == 'pdf':
            text = extract_text_from_pdf(filepath)
        elif ext == 'docx':
            text = extract_text_from_docx(filepath)
        elif ext == 'txt':
            text = extract_text_from_txt(filepath)
        else:
            os.remove(filepath)
            return jsonify({"error": "Unsupported file type. Upload PDF, DOCX, or TXT."}), 400

        os.remove(filepath)

    elif 'resume_text' in request.form and request.form['resume_text'].strip():
        text = request.form['resume_text']
    else:
        return jsonify({"error": "No resume provided. Upload a file or paste text."}), 400

    if len(text.strip()) < 50:
        return jsonify({"error": "Could not extract enough text from the file. Try pasting text directly."}), 400

    contact = extract_contact_info(text)
    skills = extract_skills(text)
    sections = detect_sections(text)
    keywords = compute_tfidf_keywords(text)
    scores, overall_score = score_resume(text, sections, skills, contact)
    grade, grade_label = get_grade(overall_score)
    word_count = len(text.split())
    suggestions = generate_suggestions(scores, sections, skills, contact, word_count)
    job_match = rank_against_job(text, job_description)

    return jsonify({
        "overall_score": overall_score,
        "grade": grade,
        "grade_label": grade_label,
        "word_count": word_count,
        "contact": contact,
        "skills": skills,
        "sections": sections,
        "scores": scores,
        "keywords": keywords,
        "suggestions": suggestions,
        "job_match": job_match
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
