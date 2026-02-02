from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import anthropic
import openai
from google import generativeai as genai
import sqlite3
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
CORS(app)  # Allow requests from your Creao app

# Your API keys (we'll use environment variables for security)
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize clients
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
openai.api_key = OPENAI_KEY
genai.configure(api_key=GOOGLE_KEY)

# Rate limiting settings
DAILY_LIMIT = 10

# Initialize database
def init_db():
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usage
                 (user_id TEXT, date TEXT, count INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def get_user_id(request):
    """Generate anonymous user ID from IP"""
    ip = request.remote_addr
    return hashlib.md5(ip.encode()).hexdigest()

def check_rate_limit(user_id):
    """Check if user has exceeded daily limit"""
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    c.execute('SELECT count FROM usage WHERE user_id=? AND date=?', (user_id, today))
    result = c.fetchone()
    conn.close()
    
    if result is None:
        return True  # First query today
    return result[0] < DAILY_LIMIT

def increment_usage(user_id):
    """Increment user's query count"""
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    c.execute('SELECT count FROM usage WHERE user_id=? AND date=?', (user_id, today))
    result = c.fetchone()
    
    if result is None:
        c.execute('INSERT INTO usage VALUES (?, ?, 1)', (user_id, today))
    else:
        c.execute('UPDATE usage SET count=? WHERE user_id=? AND date=?', 
                 (result[0] + 1, user_id, today))
    conn.commit()
    conn.close()

@app.route('/query', methods=['POST'])
def query_ais():
    """Main endpoint to query multiple AIs"""
    user_id = get_user_id(request)
    
    # Check rate limit
    if not check_rate_limit(user_id):
        return jsonify({
            'error': 'Daily limit reached',
            'message': 'You have reached your daily limit of 10 queries. Try again tomorrow!'
        }), 429
    
    data = request.json
    prompt = data.get('prompt', '')
    ais = data.get('ais', ['claude', 'chatgpt', 'gemini'])  # Which AIs to query
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    results = {}
    
    # Query Claude
    if 'claude' in ais and ANTHROPIC_KEY:
        try:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            results['claude'] = response.content[0].text
        except Exception as e:
            results['claude'] = f"Error: {str(e)}"
    
    # Query ChatGPT
    if 'chatgpt' in ais and OPENAI_KEY:
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            results['chatgpt'] = response.choices[0].message.content
        except Exception as e:
            results['chatgpt'] = f"Error: {str(e)}"
    
    # Query Gemini
    if 'gemini' in ais and GOOGLE_KEY:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            results['gemini'] = response.text
        except Exception as e:
            results['gemini'] = f"Error: {str(e)}"
    
    # Increment usage
    increment_usage(user_id)
    
    # Get remaining queries
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute('SELECT count FROM usage WHERE user_id=? AND date=?', (user_id, today))
    used = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'results': results,
        'usage': {
            'used': used,
            'limit': DAILY_LIMIT,
            'remaining': DAILY_LIMIT - used
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)