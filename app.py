from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, make_response, url_for as flask_url_for, g
from flask_babel import Babel, get_locale
from functions.database import new_subscriber, new_message, get_posts_paginated, get_post_by_slug, get_all_posts, get_random_posts, add_new_post, create_slug
from datetime import datetime, timezone
import re, os
from markupsafe import escape
from functools import wraps
from urllib.parse import quote
from dotenv import load_dotenv
from PIL import Image
from werkzeug.utils import secure_filename

load_dotenv()


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


# ============================================================================
# CANONICAL URL ENFORCEMENT - SEO CRITICAL
# ============================================================================
# Enforce: HTTPS + www + language prefix with 301 redirects
# This prevents Google from indexing non-canonical URLs
# ============================================================================

@app.before_request
def enforce_canonical_url():
    """
    Enforce canonical URL structure with 301 permanent redirects:
    - Force HTTPS (if not already)
    - Force www subdomain
    - Ensure language prefix exists (handled separately in routes)
    
    This should run BEFORE Cloudflare, but Cloudflare rules will handle
    the heavy lifting for protocol and domain. This is backup/verification.
    """
    # Skip enforcement for:
    # 1. Static files (performance)
    # 2. API endpoints (may be called from various sources)
    # 3. Admin endpoints (may need flexibility)
    # 4. Sitemap/robots (should work on any domain)
    if (request.path.startswith('/static/') or 
        request.path.startswith('/api/') or 
        request.path.startswith('/admin/') or
        request.path in ['/sitemap.xml', '/robots.txt', '/favicon.ico']):
        return None
    
    # Get the current URL components
    scheme = request.scheme
    host = request.host.lower()
    path = request.path
    query_string = request.query_string.decode('utf-8')
    
    # Check if redirect is needed
    needs_redirect = False
    canonical_scheme = 'https'
    canonical_host = 'www.iiot-bay.com'
    
    # Force HTTPS (Cloudflare should handle this, but backup check)
    if scheme != canonical_scheme:
        needs_redirect = True
        scheme = canonical_scheme
    
    # Force www subdomain
    # Handle both iiot-bay.com and any other variants
    if host != canonical_host:
        # Only redirect if it's our domain (not localhost for development)
        if 'iiot-bay.com' in host or (host not in ['localhost', '127.0.0.1'] and not host.startswith('localhost:')):
            needs_redirect = True
            host = canonical_host
    
    if needs_redirect:
        # Build canonical URL
        canonical_url = f"{scheme}://{host}{path}"
        if query_string:
            canonical_url += f"?{query_string}"
        
        # 301 permanent redirect to canonical URL
        return redirect(canonical_url, code=301)
    
    return None


# Decorator to validate language prefix
def with_lang(f):
    """Decorator to handle language prefix in URLs"""
    @wraps(f)
    def decorated_function(lang, *args, **kwargs):
        # Validate language
        if lang not in app.config['BABEL_SUPPORTED_LOCALES']:
            # Redirect to default language with 301 (permanent)
            return redirect(f"/{app.config['BABEL_DEFAULT_LOCALE']}{request.path}", code=301)
        
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
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.googletagmanager.com https://www.google-analytics.com https://ssl.google-analytics.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https: https://www.googletagmanager.com https://www.google-analytics.com https://ssl.google-analytics.com https://stats.g.doubleclick.net; "
        "connect-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google-analytics.com https://ssl.google-analytics.com https://stats.g.doubleclick.net https://www.googletagmanager.com https://region1.google-analytics.com https://region1.analytics.google.com; "
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
    """Redirect root to default language with 301 (permanent)"""
    return redirect(f"/{app.config['BABEL_DEFAULT_LOCALE']}/", code=301)


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
        turnstile_response = data.get('cf-turnstile-response', '').strip()
        
        # Validate Cloudflare Turnstile
        if not turnstile_response:
            return jsonify({"success": False, "message": "Please complete the security verification"}), 400
        
        # Verify Turnstile token with Cloudflare
        import requests
        verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        verify_data = {
            'secret': os.getenv('TURNSTILE_SECRET_KEY'),
            'response': turnstile_response,
            'remoteip': request.remote_addr
        }
        
        try:
            turnstile_result = requests.post(verify_url, data=verify_data, timeout=5).json()
            if not turnstile_result.get('success'):
                return jsonify({"success": False, "message": "Security verification failed. Please try again."}), 400
        except Exception as e:
            print(f"Turnstile verification error: {e}")
            return jsonify({"success": False, "message": "Security verification error. Please try again."}), 500
        
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
# Google-compliant sitemap with:
# - Valid XML with proper namespaces
# - Only canonical URLs with language prefixes (/ar/, /en/)
# - No root (/), no redirects, no query strings
# - Proper hreflang alternates (ar, en, x-default)
# - ISO 8601 lastmod dates
# ============================================================================

# Global cache for sitemap (24-hour in-memory cache)
_sitemap_cache = {'xml': None, 'timestamp': None}


def _generate_sitemap_xml(base_url, languages, default_lang):
    """
    Generate Google-compliant sitemap XML.
    
    Each page emits ONE <url> block with:
    - <loc> pointing to Arabic (canonical) URL
    - hreflang alternates for ar, en, and x-default
    - <lastmod> in YYYY-MM-DD format
    """
    current_time = '2026-01-19'
    
    # Public pages that exist in both languages
    # Only include pages with language prefixes
    static_pages = [
        '',         # index - /ar/ and /en/
        'about',    # /ar/about and /en/about
        'services', # /ar/services and /en/services
        'blog',     # /ar/blog and /en/blog
        'contact',  # /ar/contact and /en/contact
        'terms',    # /ar/terms and /en/terms
    ]
    
    # Build XML with proper formatting
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    ]
    
    # Generate URL entries for each static page
    for page in static_pages:
        # Build URLs for both languages
        if page == '':
            url_ar = f"{base_url}/ar/"
            url_en = f"{base_url}/en/"
        else:
            url_ar = f"{base_url}/ar/{page}"
            url_en = f"{base_url}/en/{page}"
        
        # Emit one <url> block with Arabic as canonical
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{url_ar}</loc>')
        xml_lines.append(f'    <lastmod>{current_time}</lastmod>')
        
        # hreflang alternates
        xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="ar" href="{url_ar}"/>')
        xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{url_en}"/>')
        xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url_ar}"/>')
        
        xml_lines.append('  </url>')
    
    # Add blog posts (language-neutral URLs without prefixes)
    # Posts don't have hreflang since they're accessed via /post/{slug}
    try:
        posts = get_all_posts()
        for post in posts:
            if not post.get('slug'):
                continue
            
            post_url = f"{base_url}/post/{quote(post['slug'])}"
            
            # Use current_time for all posts
            post_date = current_time
            
            # Posts don't have hreflang (no language alternates)
            xml_lines.append('  <url>')
            xml_lines.append(f'    <loc>{post_url}</loc>')
            xml_lines.append(f'    <lastmod>{post_date}</lastmod>')
            xml_lines.append('  </url>')
    except Exception as e:
        # Don't break sitemap generation if posts fail
        print(f"Warning: Could not fetch posts for sitemap: {e}")
    
    xml_lines.append('</urlset>')
    
    return '\n'.join(xml_lines)


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    Production-ready sitemap endpoint with explicit XML response headers.
    """
    global _sitemap_cache
    
    # Force cache refresh if requested (for testing/deployment)
    force_refresh = request.args.get('refresh') == '1'
    
    # Check cache validity
    cache_timeout = app.config.get('SITEMAP_CACHE_TIMEOUT', 86400)
    now = datetime.now(timezone.utc).timestamp()
    
    if (not force_refresh and
        _sitemap_cache['xml'] and 
        _sitemap_cache['timestamp'] and 
        (now - _sitemap_cache['timestamp']) < cache_timeout):
        # Serve from cache with explicit headers
        response = Response(_sitemap_cache['xml'])
        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        return response
    
    # Generate fresh sitemap
    base_url = app.config.get('SITEMAP_BASE_URL', 'https://www.iiot-bay.com')
    languages = app.config['BABEL_SUPPORTED_LOCALES']
    default_lang = app.config['BABEL_DEFAULT_LOCALE']
    
    sitemap_xml = _generate_sitemap_xml(base_url, languages, default_lang)
    
    # Update cache
    _sitemap_cache['xml'] = sitemap_xml
    _sitemap_cache['timestamp'] = now
    
    # Return with explicit Content-Type header
    response = Response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response



@app.route('/robots.txt', methods=['GET'])
def robots():
    with open('robots.txt', 'r') as f:
        robots_txt = f.read()
    return Response(robots_txt, mimetype='text/plain')


@app.route('/admin/add-new-post', methods=['GET', 'POST'])
def admin_add_new_post():
    """Admin endpoint to add a new blog post - protected by access key"""
    # Get the admin key from environment
    admin_key = os.getenv('admin_add_new_post_key')
    
    if request.method == 'POST':
        # Verify access key first
        provided_key = request.form.get('access_key', '').strip()
        
        if not provided_key:
            return render_template('add_post.html', 
                                 error="Access key is required!",
                                 form_data=request.form)
        
        if provided_key != admin_key:
            return render_template('add_post.html', 
                                 error="Invalid access key! Access denied.",
                                 form_data=request.form)
        
        # Get form data
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        content = request.form.get('content', '').strip()
        slug = request.form.get('slug', '').strip()
        
        # Handle image upload
        image_filename = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Validate it's an image
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                
                if file_ext not in allowed_extensions:
                    return render_template('add_post.html', 
                                         error="Invalid file type. Only image files are allowed!",
                                         form_data=request.form)
                
                try:
                    # Generate filename from slug or title
                    base_name = slug if slug else create_slug(title)
                    image_filename = f"{base_name}.webp"
                    
                    # Open and convert image to WebP
                    img = Image.open(file.stream)
                    
                    # Convert RGBA to RGB if necessary (WebP handles both, but let's be safe)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as WebP
                    img_path = os.path.join('static', 'img', image_filename)
                    img.save(img_path, 'WEBP', quality=85, optimize=True)
                    
                except Exception as e:
                    return render_template('add_post.html', 
                                         error=f"Error processing image: {str(e)}",
                                         form_data=request.form)
        
        # Validate required fields
        if not title or not author or not content:
            return render_template('add_post.html', 
                                 error="Title, Author, and Content are required fields!",
                                 form_data=request.form)
        
        # Use today's date in the same format as other posts (e.g., "January 09, 2026")
        date = datetime.now().strftime('%B %d, %Y')
        
        # Generate slug from title if not provided
        if not slug:
            slug = create_slug(title)
        else:
            # Keep user-provided slug as-is, just clean up spaces and hyphens
            slug = slug.strip()
            slug = slug.replace(' ', '-')
            # Remove duplicate hyphens
            while '--' in slug:
                slug = slug.replace('--', '-')
            slug = slug.strip('-')
        
        # Prefix image filename with full path to match other posts
        if image_filename:
            image_filename = f"/static/img/{image_filename}"
        
        # Insert post into database
        success, result = add_new_post(title, date, author, content, image_filename, slug)
        
        if success:
            return render_template('add_post.html', 
                                 success=f"Post added successfully! Post ID: {result}",
                                 post_url=f"/post/{slug}")
        else:
            return render_template('add_post.html', 
                                 error=result,
                                 form_data=request.form)
    
    # GET request - show the form
    return render_template('add_post.html')


# if __name__ == '__main__':
#     app.run(debug=True)

