from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, make_response, url_for as flask_url_for, g
from flask_babel import Babel, get_locale
from functions.database import new_subscriber, new_message, get_posts_paginated, get_post_by_slug, get_all_posts, get_random_posts
from datetime import datetime, timezone
import re
from markupsafe import escape
from functools import wraps
from urllib.parse import quote


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'ar']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['SITEMAP_BASE_URL'] = 'https://www.iiot-bay.com'
app.config['SITEMAP_CACHE_TIMEOUT'] = 86400  # 24 hours

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


# ============================================================================
# SITEMAP GENERATOR - SEO-OPTIMIZED & PRODUCTION-READY
# ============================================================================
# This implementation follows Google's sitemap best practices:
# 1. Includes only canonical, indexable URLs (no redirects, no root)
# 2. Implements proper hreflang alternates for multilingual content
# 3. Uses dynamic route discovery to avoid hardcoded routes
# 4. Caches output for performance (24h)
# 5. Generates valid XML with proper formatting
# ============================================================================

# Global cache for sitemap (simple in-memory cache)
_sitemap_cache = {'xml': None, 'timestamp': None}


def _should_include_route(endpoint, rule):
    """
    Filter routes that should NOT be included in sitemap.
    
    SEO reasoning:
    - Exclude API endpoints (not indexable HTML)
    - Exclude admin/auth/internal endpoints (not public)
    - Exclude static files (handled separately)
    - Exclude POST-only routes (not accessible to crawlers)
    - Exclude routes with dynamic parameters that aren't whitelisted
    """
    # Exclude these endpoint patterns
    exclude_patterns = [
        'static', 'api', 'admin', 'auth', 'debug', 'health', 
        'newsletter', 'favicon', 'robots', 'sitemap'
    ]
    
    # Check if endpoint matches exclusion patterns
    for pattern in exclude_patterns:
        if pattern in endpoint.lower():
            return False
    
    # Exclude POST-only routes (forms, APIs)
    if 'GET' not in rule.methods:
        return False
    
    # Exclude root redirect (not canonical)
    if rule.rule == '/':
        return False
    
    # Exclude routes with parameters unless whitelisted
    # Exception: blog pagination is whitelisted
    if '<' in rule.rule and 'page' not in rule.rule:
        return False
    
    return True


def _build_multilang_url(route_name, lang, base_url):
    """
    Build absolute URL for a multilingual route.
    
    SEO reasoning:
    - Always use absolute URLs (required by sitemap spec)
    - Ensure consistent URL structure across languages
    - Handle special cases (index route requires trailing slash)
    """
    if route_name == 'index':
        return f"{base_url}/{lang}/"
    else:
        # Remove 'lang_' prefix if present in endpoint name
        path = route_name.replace('lang_', '')
        return f"{base_url}/{lang}/{path}"


def _parse_post_date(date_str):
    """
    Parse various date formats and return ISO 8601 format (YYYY-MM-DD).
    
    SEO reasoning:
    - lastmod must be in W3C Datetime format (ISO 8601)
    - Accurate dates help search engines prioritize fresh content
    """
    if not date_str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Try common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(str(date_str), fmt)
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue
    
    # Fallback to current date
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def _generate_sitemap_xml(base_url, languages, default_lang):
    """
    Generate complete sitemap XML with proper hreflang alternates.
    
    SEO reasoning:
    - Each URL appears ONCE with alternates (not duplicated per language)
    - hreflang alternates help Google serve correct language version
    - x-default points to default language (Arabic in this case)
    - Proper XML formatting ensures parser compatibility
    """
    urls = []
    processed_routes = set()
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # ========================================================================
    # STEP 1: Discover and process static routes from Flask app
    # ========================================================================
    # This automatically finds all public-facing routes without hardcoding
    for rule in app.url_map.iter_rules():
        endpoint = rule.endpoint
        
        # Skip routes that shouldn't be in sitemap
        if not _should_include_route(endpoint, rule):
            continue
        
        # Extract route name (remove language parameter)
        route_pattern = rule.rule.replace('/<lang>/', '').replace('/<lang>', '').strip('/')
        if not route_pattern:
            route_pattern = 'index'
        
        # Avoid processing same route multiple times
        if route_pattern in processed_routes:
            continue
        processed_routes.add(route_pattern)
        
        # Skip blog pagination (we'll only include /ar/blog and /en/blog)
        if 'page' in route_pattern:
            continue
        
        # Build URL entry with alternates for all languages
        alternates = {}
        for lang in languages:
            if route_pattern == 'index':
                url = f"{base_url}/{lang}/"
            else:
                url = f"{base_url}/{lang}/{route_pattern}"
            alternates[lang] = url
        
        # Use first language's URL as canonical
        canonical_url = alternates[languages[0]]
        
        urls.append({
            'loc': canonical_url,
            'lastmod': current_time,
            'alternates': alternates,
            'default_lang': default_lang
        })
    
    # ========================================================================
    # STEP 2: Add blog posts (language-neutral URLs)
    # ========================================================================
    # Posts use /post/{slug} without language prefix for backwards compatibility
    # They inherit language from cookie/browser, not URL
    try:
        posts = get_all_posts()
        for post in posts:
            if not post.get('slug'):
                continue
            
            post_url = f"{base_url}/post/{quote(post['slug'])}"
            post_date = _parse_post_date(post.get('created_at'))
            
            # Posts don't have language alternates (single URL for all languages)
            urls.append({
                'loc': post_url,
                'lastmod': post_date,
                'alternates': None,
                'default_lang': None
            })
    except Exception as e:
        # Log error but don't break sitemap generation
        print(f"Error fetching posts for sitemap: {e}")
    
    # ========================================================================
    # STEP 3: Generate XML output with proper formatting
    # ========================================================================
    # Using list join with newlines for proper XML formatting
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    
    for url_entry in urls:
        xml_parts.append('  <url>')
        xml_parts.append(f'    <loc>{url_entry["loc"]}</loc>')
        xml_parts.append(f'    <lastmod>{url_entry["lastmod"]}</lastmod>')
        
        # Add hreflang alternates for multilingual pages
        if url_entry['alternates']:
            # Self-referencing alternate
            for lang, alt_url in url_entry['alternates'].items():
                xml_parts.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{alt_url}"/>')
            
            # x-default points to default language (SEO best practice)
            default_url = url_entry['alternates'][url_entry['default_lang']]
            xml_parts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{default_url}"/>')
        
        xml_parts.append('  </url>')
    
    xml_parts.append('</urlset>')
    
    # Join with newlines for proper XML formatting (not one long line)
    return '\n'.join(xml_parts)


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    Dynamic sitemap generator endpoint.
    
    SEO Benefits:
    - Helps search engines discover all pages efficiently
    - Provides language alternates for international SEO
    - Updates automatically when routes or posts change
    - Cached for performance (doesn't slow down crawlers)
    
    Caching strategy:
    - Cache for 24 hours to avoid regenerating on every request
    - Crawlers typically fetch sitemap once per crawl session
    - Balance between freshness and server load
    """
    global _sitemap_cache
    
    # Check if cache is valid
    cache_timeout = app.config.get('SITEMAP_CACHE_TIMEOUT', 86400)
    now = datetime.now(timezone.utc).timestamp()
    
    if (_sitemap_cache['xml'] and 
        _sitemap_cache['timestamp'] and 
        (now - _sitemap_cache['timestamp']) < cache_timeout):
        # Serve from cache
        return Response(_sitemap_cache['xml'], mimetype='application/xml; charset=utf-8')
    
    # Generate fresh sitemap
    base_url = app.config.get('SITEMAP_BASE_URL', 'https://www.iiot-bay.com')
    languages = app.config['BABEL_SUPPORTED_LOCALES']
    default_lang = app.config['BABEL_DEFAULT_LOCALE']
    
    sitemap_xml = _generate_sitemap_xml(base_url, languages, default_lang)
    
    # Update cache
    _sitemap_cache['xml'] = sitemap_xml
    _sitemap_cache['timestamp'] = now
    
    return Response(sitemap_xml, mimetype='application/xml; charset=utf-8')



@app.route('/robots.txt', methods=['GET'])
def robots():
    with open('robots.txt', 'r') as f:
        robots_txt = f.read()
    return Response(robots_txt, mimetype='text/plain')




# if __name__ == '__main__':
#     app.run(debug=True)

