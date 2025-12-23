from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from functions.database import new_subscriber, new_message, get_posts_paginated, get_post_by_slug, get_all_posts, get_random_posts
from datetime import datetime
import re
from markupsafe import escape




app = Flask(__name__)


@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # Content Security Policy - Prevent XSS
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    # HTTP Strict Transport Security - Force HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Cross-Origin Opener Policy
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS Protection (legacy browsers)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'iio-bay-icon.png', mimetype='image/png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    random_posts = get_random_posts(limit=9)
    return render_template('index.html', random_posts=random_posts)


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
    email_address = request.json.get('email', '').strip()
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email_address or not re.match(email_pattern, email_address):
        return jsonify({"message": "Invalid email address"}), 400

    if not new_subscriber(email_address):
        print("Failed to add new subscriber: ", email_address)
        return jsonify({"message": "Subscription failed"}), 500

    return jsonify({"message": "Subscription successful"}), 200



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.json
        name = escape(data.get('name', '').strip())
        email_address = data.get('email', '').strip()
        subject = escape(data.get('subject', '').strip())
        message = escape(data.get('message', '').strip())
        
        # Validate required fields
        if not name or not email_address or not message:
            return jsonify({"success": False, "message": "All required fields must be filled"}), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email_address):
            return jsonify({"success": False, "message": "Invalid email address"}), 400

        if not new_message(name, email_address, subject, message):
            print("Failed to save message: ", data)
            return jsonify({"success": False, "message": "Failed to send message"}), 500

        return jsonify({"success": True, "message": "Message sent successfully"}), 200

    # GET
    return render_template('contact.html')



@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    # Get current date for static pages
    today = datetime.now().strftime('%Y-%m-%d')
    dates_ = ['2025-12-23', '2025-12-15', '2025-12-17', '2025-12-09', '2025-12-15', '2025-12-18', '2025-12-13']

    
    # Define static pages with lastmod
    pages = [
        {'loc': 'https://www.iiot-bay.com/', 'lastmod': dates_[0]},
        {'loc': 'https://www.iiot-bay.com/about', 'lastmod': dates_[1]},
        {'loc': 'https://www.iiot-bay.com/services', 'lastmod': dates_[2]},
        {'loc': 'https://www.iiot-bay.com/blog', 'lastmod': dates_[3]},
        {'loc': 'https://www.iiot-bay.com/contact', 'lastmod': dates_[4]},
        {'loc': 'https://www.iiot-bay.com/terms', 'lastmod': dates_[5]},
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

