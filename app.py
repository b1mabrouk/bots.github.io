from flask import Flask, render_template, request, send_file, jsonify
import os
import pysrt
import google.generativeai as genai
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBqsEjNqaZVmEsIVQmg-L11jSmR0ao3xB4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro',
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.3,
                                top_p=0.8,
                                top_k=40
                            ))

# Available languages
LANGUAGES = {
    'Arabic': 'ar',
    'English': 'en',
    'Turkish': 'tr',
    'French': 'fr',
    'Spanish': 'es',
    'German': 'de',
    'Russian': 'ru',
    'Chinese': 'zh',
    'Japanese': 'ja',
    'Korean': 'ko'
}

def translate_text(text, target_lang):
    try:
        # Preserve any HTML-like formatting tags
        formatting_tags = []
        import re
        
        # Find and temporarily remove formatting tags
        def replace_tags(match):
            formatting_tags.append(match.group(0))
            return f"[TAG{len(formatting_tags)-1}]"
            
        text_without_tags = re.sub(r'<[^>]+>', replace_tags, text)
        
        prompt = f"""Translate the following subtitle text to {target_lang}. This is for a video/movie subtitle, so the translation must be:

1. HIGHLY ACCURATE and maintain the exact meaning
2. NATURAL and sound like native speech in the target language
3. CONCISE to fit subtitle timing
4. CULTURALLY APPROPRIATE for the target language

Special requirements:
- Preserve all numbers and special characters
- Keep names and proper nouns unchanged
- Maintain the same tone (formal/informal) as the original
- If there are multiple lines, preserve the line breaks
- For idioms and expressions, use equivalent ones in the target language

Original text:
{text_without_tags}

Translation (keep it concise and natural):"""
        
        response = model.generate_content(prompt)
        translated_text = ''
        
        if hasattr(response, 'candidates') and response.candidates:
            translated_text = response.candidates[0].content.parts[0].text.strip()
        elif hasattr(response, 'parts') and response.parts:
            translated_text = response.parts[0].text.strip()
        else:
            translated_text = response.text.strip()
            
        # Restore formatting tags
        for i, tag in enumerate(formatting_tags):
            translated_text = translated_text.replace(f"[TAG{i}]", tag)
            
        # Clean up any artifacts
        translated_text = translated_text.replace('Translation:', '').strip()
        translated_text = re.sub(r'^["\']|["\']$', '', translated_text)  # Remove quotes if present
        
        return translated_text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate_srt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.srt'):
        return jsonify({'error': 'Only .srt files are allowed'}), 400
    
    source_lang = request.form.get('source_lang')
    target_lang = request.form.get('target_lang')
    
    if source_lang == target_lang:
        return jsonify({'error': 'Source and target languages must be different'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load and translate
        subs = pysrt.open(filepath)
        for sub in subs:
            sub.text = translate_text(sub.text, target_lang)
        
        # Save translated file
        output_filename = f"{os.path.splitext(filename)[0]}_{LANGUAGES[target_lang]}.srt"
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        subs.save(output_filepath, encoding='utf-8')
        
        # Return file
        return send_file(
            output_filepath,
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
