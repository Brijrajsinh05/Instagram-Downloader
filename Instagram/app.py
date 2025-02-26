from flask import Flask, render_template, request, jsonify, send_file
import instaloader
import os
import json
import tempfile
from urllib.parse import urlparse
import random

app = Flask(__name__)
L = instaloader.Instaloader()

# Knowledge base for the chatbot
KNOWLEDGE_BASE = {
    'greetings': [
        "Hello! I'm your AI assistant created by Brijrajsinh Jadav. How can I help you today?",
        "Hi there! I'm Brijrajsinh Jadav's AI assistant. What can I do for you?",
        "Welcome! I'm an AI created by Brijrajsinh Jadav. How may I assist you?"
    ],
    'download_help': [
        "To download Instagram content, simply paste the Instagram URL in the box above and click on any of the download services like SnapInsta, FastDL, or SaveIG.",
        "Just copy the Instagram post URL you want to download, then click on one of our download service buttons. It's that simple!",
        "I can help you download Instagram content! Just use any of our download services above - they're all free and reliable."
    ],
    'features': [
        "Our Instagram downloader supports videos, photos, reels, IGTV, and carousel posts. All downloads are in HD quality!",
        "You can download any public Instagram content including videos, photos, reels, and stories. We ensure high-quality downloads.",
        "We support downloading all types of Instagram content in the best quality possible."
    ],
    'about': [
        "This tool was created by Brijrajsinh Jadav to help users download Instagram content easily and safely.",
        "I'm an AI assistant created by Brijrajsinh Jadav, designed to help you with Instagram downloads and any other questions.",
        "This is a free Instagram download service created by Brijrajsinh Jadav, featuring multiple download options and HD quality."
    ]
}

def get_smart_response(message):
    message = message.lower()
    
    # Check for common questions and keywords
    if any(word in message for word in ['hi', 'hello', 'hey']):
        return random.choice(KNOWLEDGE_BASE['greetings'])
    
    elif any(word in message for word in ['download', 'save', 'get']):
        return random.choice(KNOWLEDGE_BASE['download_help'])
    
    elif any(word in message for word in ['feature', 'support', 'can', 'possible']):
        return random.choice(KNOWLEDGE_BASE['features'])
    
    elif any(word in message for word in ['who', 'about', 'creator', 'made']):
        return random.choice(KNOWLEDGE_BASE['about'])
    
    # General response for other queries
    return ("I'm an AI assistant created by Brijrajsinh Jadav. I can help you with downloading Instagram content "
           "and answer questions about our service. What would you like to know?")

def get_media_info(url):
    try:
        # Extract shortcode from URL
        pattern = r'instagram.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)'
        match = re.search(pattern, url)
        if not match:
            return {'error': 'Invalid Instagram URL'}
        
        shortcode = match.group(1)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        result = {
            'type': 'video' if post.is_video else 'image',
            'url': post.video_url if post.is_video else post.url,
            'caption': post.caption if post.caption else '',
            'likes': post.likes,
            'comments': post.comments,
            'date': post.date.isoformat()
        }
        
        # Handle carousel/album
        if post.typename == 'GraphSidecar':
            result['type'] = 'carousel'
            result['items'] = []
            for node in post.get_sidecar_nodes():
                item = {
                    'type': 'video' if node.is_video else 'image',
                    'url': node.video_url if node.is_video else node.display_url
                }
                result['items'].append(item)
        
        return result
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'Please provide an Instagram URL'})
        
        result = get_media_info(url)
        if 'error' in result:
            return jsonify(result)
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/local-chat', methods=['POST'])
def local_chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Get appropriate response
    response = get_smart_response(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
