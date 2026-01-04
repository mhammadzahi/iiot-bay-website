from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, make_response, url_for as flask_url_for, g
from flask_babel import Babel, get_locale
from functions.database import new_subscriber, new_message, get_posts_paginated, get_post_by_slug, get_all_posts, get_random_posts
from datetime import datetime
import re
from markupsafe import escape
from functools import wraps


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'ar']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)


def get_locale():
    # 1. Check URL for language (from view_args set by @with_lang decorator)
    if hasattr(g, 'lang') and g.lang in app.config['BABEL_SUPPORTED_LOCALES']:
        return g.lang
    
    # 2. Check cookie (for post pages without language prefix)
    lang_cookie = request.cookies.get('user_lang')
    if lang_cookie in app.config['BABEL_SUPPORTED_LOCALES']:
        return lang_cookie
    
    # 3. Check Accept-Language header as fallback
    best_match = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
    if best_match:
        return best_match
    
    # 4. Default to Arabic
    return app.config['BABEL_DEFAULT_LOCALE']


babel.init_app(app, locale_selector=get_locale)


# Decorator to validate language prefix
def with_lang(f):
    """Decorator to handle language prefix in URLs"""
    @wraps(f)
    def decorated_function(lang, *args, **kwargs):
        # Validate language
        if lang not in app.config['BABEL_SUPPORTED_LOCALES']:
            # Redirect to default language
            return redirect(f"/{app.config['BABEL_DEFAULT_LOCALE']}{request.path}")
        
        # Store language in g for use in get_locale()
        g.lang = lang
        
        # Call the wrapped function
        response = make_response(f(*args, **kwargs))
        
        # Set cookie to persist language choice (for post pages)
        response.set_cookie('user_lang', lang, max_age=60*60*24*365)
        
        return response
    return decorated_function


# Custom url_for that automatically includes lang parameter
def url_for(endpoint, **values):
    """Custom url_for that automatically includes the current language"""
    # Don't add lang for static files, external URLs, or post endpoints
    if endpoint == 'static' or endpoint.startswith('_') or endpoint == 'post':
        return flask_url_for(endpoint, **values)
    
    # Use current language from g, or default
    if 'lang' not in values:
        values['lang'] = getattr(g, 'lang', app.config['BABEL_DEFAULT_LOCALE'])
    
    return flask_url_for(endpoint, **values)


@app.context_processor
def inject_locale():
    """Make get_locale and custom url_for available in all templates"""
    return {
        'get_locale': get_locale,
        'url_for': url_for,
        'current_lang': getattr(g, 'lang', app.config['BABEL_DEFAULT_LOCALE']),
        'supported_locales': app.config['BABEL_SUPPORTED_LOCALES']
    }


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
    
    # Content-Language header
    response.headers['Content-Language'] = str(get_locale())
    
    return response


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'iio-bay-icon.png', mimetype='image/png')


# Root redirect to default language
@app.route('/')
def root():
    """Redirect root to default language"""
    return redirect(f"/{app.config['BABEL_DEFAULT_LOCALE']}/")


@app.route('/<lang>/')
@with_lang
def index():
    random_posts = get_random_posts(limit=9)
    return render_template('index.html', random_posts=random_posts)


@app.route('/<lang>/about')
@with_lang
def about():
    return render_template('about.html')


@app.route('/<lang>/services')
@with_lang
def services():
    return render_template('services.html')


@app.route('/<lang>/terms')
@with_lang
def terms():
    return render_template('terms.html')


@app.route('/<lang>/blog')
@app.route('/<lang>/blog/page/<int:page>')
@with_lang
def blog(page=1):
    data = get_posts_paginated(page=page, per_page=9)
    return render_template('blog.html', posts=data['posts'], page=data['page'], total_pages=data['total_pages'], page_range=data['page_range'])


@app.route('/post/<path:post_slug>')
def post(post_slug):
    """Post route without language prefix for backward compatibility"""
    post = get_post_by_slug(post_slug)
    if not post:
        return render_template('404.html'), 404
        
    return render_template('post.html', post=post)


@app.route('/<lang>/contact', methods=['GET', 'POST'])
@with_lang
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
    random_posts = get_random_posts(limit=6)
    return render_template('contact.html', random_posts=random_posts)


@app.route('/api/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Newsletter subscription endpoint (no language prefix for API)"""
    email_address = request.json.get('email', '').strip()
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email_address or not re.match(email_pattern, email_address):
        return jsonify({"message": "Invalid email address"}), 400

    if not new_subscriber(email_address):
        print("Failed to add new subscriber: ", email_address)
        return jsonify({"message": "Subscription failed"}), 500

    return jsonify({"message": "Subscription successful"}), 200


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler - redirect to default language 404"""
    lang = getattr(g, 'lang', app.config['BABEL_DEFAULT_LOCALE'])
    return render_template('404.html'), 404


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    # Get current date for static pages
    today = datetime.now().strftime('%Y-%m-%d')
    dates_ = ['2025-12-23', '2025-12-15', '2025-12-17', '2025-12-09', '2025-01-03', '2025-12-18', '2025-12-13']

    pages = []
    
    # Define static pages (without language-specific routes)
    static_routes = [
        ('index', dates_[4]),
        ('about', dates_[4]),
        ('services', dates_[4]),
        ('blog', dates_[4]),
        ('contact', dates_[4]),
        ('terms', dates_[4]),
    ]
    
    # Add both language versions of each static page
    for route_name, lastmod in static_routes:
        for lang in app.config['BABEL_SUPPORTED_LOCALES']:
            if route_name == 'index':
                loc = f"https://www.iiot-bay.com/{lang}/"
            else:
                loc = f"https://www.iiot-bay.com/{lang}/{route_name}"
            
            pages.append({
                'loc': loc,
                'lastmod': lastmod,
                'alternates': {
                    'ar': f"https://www.iiot-bay.com/ar/{route_name if route_name != 'index' else ''}".rstrip('/') + ('/' if route_name == 'index' else ''),
                    'en': f"https://www.iiot-bay.com/en/{route_name if route_name != 'index' else ''}".rstrip('/') + ('/' if route_name == 'index' else ''),
                }
            })
    
    # Add all blog posts (without language prefix as per requirement)
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
            'lastmod': lastmod,
            'alternates': None  # Posts don't have language alternates
        })
    
    # Generate XML with hreflang alternates
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    
    for page in pages:
        xml_lines.append('<url>')
        xml_lines.append(f'<loc>{page["loc"]}</loc>')
        xml_lines.append(f'<lastmod>{page["lastmod"]}</lastmod>')
        
        # Add hreflang alternates for pages with translations
        if page.get('alternates'):
            for lang, url in page['alternates'].items():
                xml_lines.append(f'<xhtml:link rel="alternate" hreflang="{lang}" href="{url}"/>')
        
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

