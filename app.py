from flask import Flask, render_template, request, jsonify
import re


def slugify(title: str) -> str:
    """Create a URL-friendly slug from a post title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip('-')
    return slug

app = Flask(__name__)

# Mock Data for Blog
posts = [
    {
        'id': 1,
        'title': 'The Future of Smart Homes',
        'date': 'November 28, 2025',
        'author': 'Sarah Connor',
        'content': 'Smart homes are becoming more intuitive. With the rise of AI and IoT, our living spaces are learning from our habits...',
        'image': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 2,
        'title': 'Industrial IoT Revolution',
        'date': 'November 25, 2025',
        'author': 'John Smith',
        'content': 'Industry 4.0 is here. Factories are becoming smarter, more efficient, and safer thanks to connected sensors...',
        'image': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices bb',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 77,
        'title': 'IoT Security Best Practices aa',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 78,
        'title': 'IoT Security Best Practices p',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 79,
        'title': 'IoT Security Best Practices o',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 80,
        'title': 'IoT Security Best Practices n',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 82,
        'title': 'IoT Security Best Practices m',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 81,
        'title': 'IoT Security Best Practices l',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 85,
        'title': 'IoT Security Best Practices k',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 86,
        'title': 'IoT Security Best Practices j',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 87,
        'title': 'IoT Security Best Practices i',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 88,
        'title': 'IoT Security Best Practices h',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 89,
        'title': 'IoT Security Best Practices g',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 90,
        'title': 'IoT Security Best Practices f',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 91,
        'title': 'IoT Security Best Practices e',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 92,
        'title': 'IoT Security Best Practices d',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 93,
        'title': 'IoT Security Best Practices c',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 94,
        'title': 'IoT Security Best Practices b',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 95,
        'title': 'IoT Security Best Practices a',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    }
]

# Ensure each post has a unique slug generated from its title
seen_slugs = set()
for p in posts:
    base = slugify(p.get('title', ''))
    slug = base
    suffix = 1
    while slug in seen_slugs or not slug:
        suffix += 1
        slug = f"{base}-{suffix}"
    p['slug'] = slug
    seen_slugs.add(slug)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html') # We might just keep this in index for now or create a separate page

@app.route('/blog')
@app.route('/blog/page/<int:page>')
def blog(page=1):
    per_page = 6
    total_posts = len(posts)
    total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division
    
    # Calculate start and end indices
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get posts for current page
    paginated_posts = posts[start:end]
    
    # Calculate page range for pagination display
    page_range = []
    if total_pages <= 7:
        page_range = list(range(1, total_pages + 1))
    else:
        if page <= 4:
            page_range = list(range(1, 6)) + ['...', total_pages]
        elif page >= total_pages - 3:
            page_range = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_range = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
    
    return render_template('blog.html', posts=paginated_posts, page=page, total_pages=total_pages, page_range=page_range)


@app.route('/post/<path:post_slug>')
def post(post_slug):
    # Find post by slug (derived from title)
    post = next((p for p in posts if p.get('slug') == post_slug), None)
    return render_template('post.html', post=post)


@app.route('/api/post/<path:post_slug>/title')
def post_title_api(post_slug):
    """Return the post title as JSON for a given post ID.

    Response examples:
    - 200: {"id": 1, "title": "The Future of Smart Homes"}
    - 404: {"error": "Post not found"}
    """
    post = next((p for p in posts if p.get('slug') == post_slug), None)
    if post:
        return jsonify({"slug": post_slug, "title": post.get('title')}), 200
    return jsonify({"error": "Post not found"}), 404



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Here we would handle the form submission (e.g., send email)
        # For now, we'll just print to console
        print(f"Name: {request.form.get('name')}")
        print(f"Email: {request.form.get('email')}")
        print(f"Message: {request.form.get('message')}")
        return render_template('contact.html', success=True)
    return render_template('contact.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
