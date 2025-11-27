
import xml.etree.ElementTree as ET
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def get_match_status(title):
    """Determines match status from the title."""
    title_lower = title.lower()
    if 'live' in title_lower or 'innings' in title_lower:
        return 'LIVE'
    if 'won' in title_lower or 'drew' in title_lower or 'finished' in title_lower:
        return 'FINISHED'
    return 'UPCOMING'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scores')
def api_scores():
    try:
        search_query = request.args.get('q', '').lower()
        response = requests.get('https://static.cricinfo.com/rss/livescores.xml')
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        scores = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            description = item.find('description').text
            
            if search_query and search_query not in title.lower():
                continue

            scores.append({
                'title': title,
                'link': link,
                'description': description,
                'status': get_match_status(title)
            })
            
        return jsonify(scores)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching RSS feed: {e}"}), 500
    except ET.ParseError as e:
        return jsonify({"error": f"Error parsing XML: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
