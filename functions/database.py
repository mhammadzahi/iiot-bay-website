import sqlite3, os
# from typing import List, Dict


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iiot_bay_database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def new_subscriber(email: str) -> bool:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO newsletter_subscribers (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error adding subscriber:", e)
        return False

def new_message(name: str, email: str, subject: str, message: str) -> bool:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO contact_messages (full_name, email_address, subject, message) VALUES (?, ?, ?, ?)",
                    (name, email, subject, message))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error saving contact message:", e)
        return False

def get_posts_paginated(page: int = 1, per_page: int = 9):
    """Get paginated blog posts with pagination metadata"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get total posts count
    cur.execute("SELECT COUNT(1) FROM posts")
    total_posts = cur.fetchone()[0]
    total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division
    
    # Calculate offset
    start = (page - 1) * per_page
    
    # Get posts for current page (newest first)
    cur.execute("SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, start))
    rows = cur.fetchall()
    paginated_posts = [dict(r) for r in rows]
    conn.close()
    
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
    
    return {
        'posts': paginated_posts,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range
    }

def get_post_by_slug(post_slug: str):
    """Get a single post by its slug"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE slug=?", (post_slug,))
    row = cur.fetchone()
    post = dict(row) if row else None
    conn.close()
    return post

def get_all_posts():
    """Get all posts for sitemap generation"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT slug, created_at FROM posts ORDER BY id DESC")
    rows = cur.fetchall()
    posts = [dict(r) for r in rows]
    conn.close()
    return posts
