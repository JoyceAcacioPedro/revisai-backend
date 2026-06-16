from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import date, timedelta

load_dotenv()

def get_client():
    api_key = os.environ.get('GROQ_API_KEY')
    return Groq(api_key=api_key)

def generate_revision_plan(topic_title, topic_content, files_text=""):
    client = get_client()
    
    combined_content = f"""
    Topic: {topic_title}
    Notes: {topic_content}
    Additional material: {files_text if files_text else 'None'}
    """

    prompt = f"""
    You are an expert study planner. Based on the following study material, 
    create a spaced repetition revision plan.
    
    {combined_content}
    
    Generate exactly 5 revision activities using spaced repetition intervals:
    - Day 1: summary (review the material)
    - Day 3: flashcards (key concepts)
    - Day 7: quiz (test knowledge)
    - Day 14: quiz (reinforce memory)
    - Day 30: quiz (long-term retention)
    
    Return ONLY a JSON array, no explanation, no markdown, exactly like this:
    [
        {{"type": "summary", "days_from_now": 1}},
        {{"type": "flashcards", "days_from_now": 3}},
        {{"type": "quiz", "days_from_now": 7}},
        {{"type": "quiz", "days_from_now": 14}},
        {{"type": "quiz", "days_from_now": 30}}
    ]
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
    )

    raw = response.choices[0].message.content.strip()

    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    plan = json.loads(raw)
    
    today = date.today()
    activities = []
    for item in plan:
        activities.append({
            "type": item["type"],
            "date": today + timedelta(days=item["days_from_now"])
        })
    
    return activities


def generate_summary(topic_title, topic_content):
    client = get_client()

    prompt = f"""
    You are a study assistant. Based on the following study material, 
    generate a clear and concise summary for revision.
    
    Topic: {topic_title}
    Notes: {topic_content}
    
    Return ONLY a JSON object, no explanation, no markdown:
    {{
        "key_points": ["point 1", "point 2", "point 3"],
        "summary": "A clear paragraph summarizing the main concepts.",
        "important_terms": [
            {{"term": "term1", "definition": "definition1"}},
            {{"term": "term2", "definition": "definition2"}}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    return json.loads(raw)

def generate_flashcards(topic_title, topic_content):
    client = get_client()

    prompt = f"""
    You are a study assistant. Based on the following study material,
    generate flashcards for active recall practice.
    
    Topic: {topic_title}
    Notes: {topic_content}
    
    Return ONLY a JSON object, no explanation, no markdown:
    {{
        "flashcards": [
            {{"front": "question or concept", "back": "answer or explanation"}},
            {{"front": "question or concept", "back": "answer or explanation"}}
        ]
    }}
    
    Generate between 5 and 10 flashcards covering the most important concepts.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    return json.loads(raw)


def generate_quiz(topic_title, topic_content):
    client = get_client()

    prompt = f"""
    You are a study assistant. Based on the following study material,
    generate a multiple choice quiz.
    
    Topic: {topic_title}
    Notes: {topic_content}
    
    Return ONLY a JSON object, no explanation, no markdown:
    {{
        "questions": [
            {{
                "question": "the question text",
                "options": ["option A", "option B", "option C", "option D"],
                "correct": 0
            }}
        ]
    }}
    
    The "correct" field is the index (0-3) of the correct option.
    Generate between 5 and 8 questions.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    return json.loads(raw)


def extract_text_from_files(topic_files):
    extracted = []
    
    for topic_file in topic_files:
        file_path = topic_file.file.path
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ' '.join(
                        page.extract_text() or '' 
                        for page in reader.pages
                    )
                extracted.append(text)
                
            elif ext in ['.docx', '.doc']:
                from docx import Document
                doc = Document(file_path)
                text = ' '.join(p.text for p in doc.paragraphs)
                extracted.append(text)
                
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted.append(f.read())
                    
        except Exception as e:
            print(f"Erro ao ler ficheiro {file_path}: {e}")
    
    return ' '.join(extracted)



