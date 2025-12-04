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
    pages = [
        {'loc': '/', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/about', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': '/services', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': '/blog', 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': '/contact', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': '/terms', 'priority': '0.5', 'changefreq': 'yearly'},
    ]
    
    # Add all blog posts
    posts = get_all_posts()
    for post in posts:
        pages.append({
            'loc': f"/post/{post['slug']}",
            'priority': '0.6',
            'changefreq': 'monthly',
            'lastmod': post.get('created_at', '')
        })
    
    # Generate XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>https://www.iiot-bay.com{page["loc"]}</loc>\n'
        if page.get('lastmod'):
            xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'
    
    xml += '</urlset>'
    
    return Response(xml, mimetype='application/xml')



@app.route('/robots.txt', methods=['GET'])
def robots():
    with open('robots.txt', 'r') as f:
        robots_txt = f.read()
    return Response(robots_txt, mimetype='text/plain')


# if __name__ == '__main__':
    # import uvicorn
    # from asgiref.wsgi import WsgiToAsgi
    # asgi_app = WsgiToAsgi(app)  # Convert Flask WSGI to ASGI
    # uvicorn.run(asgi_app, host="0.0.0.0", port=5000)
    
    # app.run(debug=True, port=5000, host="0.0.0.0")  #development
    # app.run()
