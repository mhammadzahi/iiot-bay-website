from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from functions.database import new_subscriber, new_message, get_posts_paginated, get_post_by_slug, get_all_posts
from datetime import datetime




app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'iio-bay-icon.png', mimetype='image/png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    print("Home page accessed")
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/blog')
@app.route('/blog/page/<int:page>')
def blog(page=1):
    data = get_posts_paginated(page=page, per_page=9)
    return render_template('blog.html', posts=data['posts'], page=data['page'], total_pages=data['total_pages'], page_range=data['page_range'])


@app.route('/post/<path:post_slug>')
def post(post_slug):
    post = get_post_by_slug(post_slug)
    if not post:
        return render_template('404.html'), 404
        
    return render_template('post.html', post=post)


@app.route('/api/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email_address = request.json.get('email')

    if not new_subscriber(email_address):
        print("Failed to add new subscriber: ", email_address)

    return jsonify({"message": "Subscription successful"}), 200



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        email_address = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not new_message(name, email_address, subject, message):
            print("Failed to save message: ", data)

        return jsonify({"success": True, "message": "Message sent successfully"}), 200

    # GET
    return render_template('contact.html')



@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate a standards-compliant sitemap for Google/Bing"""
    # Get current date for static pages
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Define static pages with lastmod
    pages = [
        {'loc': 'https://www.iiot-bay.com/', 'lastmod': today},
        {'loc': 'https://www.iiot-bay.com/about', 'lastmod': today},
        {'loc': 'https://www.iiot-bay.com/services', 'lastmod': today},
        {'loc': 'https://www.iiot-bay.com/blog', 'lastmod': today},
        {'loc': 'https://www.iiot-bay.com/contact', 'lastmod': today},
        {'loc': 'https://www.iiot-bay.com/terms', 'lastmod': today},
    ]
    
    # Add all blog posts with their creation dates
    posts = get_all_posts()
    for post in posts:
        # Parse and format the date to YYYY-MM-DD
        lastmod = today  # Default to today if parsing fails
        if post.get('created_at'):
            try:
                date_str = post['created_at']
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        lastmod = dt.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        
        pages.append({
            'loc': f"https://www.iiot-bay.com/post/{post['slug']}",
            'lastmod': lastmod
        })
    
    # Generate XML without whitespace issues
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for page in pages:
        xml_lines.append('<url>')
        xml_lines.append(f'<loc>{page["loc"]}</loc>')
        xml_lines.append(f'<lastmod>{page["lastmod"]}</lastmod>')
        xml_lines.append('</url>')
    
    xml_lines.append('</urlset>')
    
    return Response(''.join(xml_lines), mimetype='application/xml')



@app.route('/robots.txt', methods=['GET'])
def robots():
    with open('robots.txt', 'r') as f:
        robots_txt = f.read()
    return Response(robots_txt, mimetype='text/plain')




# if __name__ == '__main__':
#     app.run(debug=True)

