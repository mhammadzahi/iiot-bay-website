from flask import Flask, render_template, request

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
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'id': 3,
        'title': 'IoT Security Best Practices',
        'date': 'November 20, 2025',
        'author': 'Emily Chen',
        'content': 'As we connect more devices, security becomes paramount. Here are the top 5 tips to secure your IoT ecosystem...',
        'image': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80'
    }
]

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
    
    return render_template('blog.html', 
                         posts=paginated_posts,
                         page=page,
                         total_pages=total_pages,
                         page_range=page_range)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    return render_template('post.html', post=post)

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

if __name__ == '__main__':
    app.run(debug=True)
