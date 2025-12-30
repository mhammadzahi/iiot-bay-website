#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), 'iiot_bay_database.db')


def create_slug(title):
    """Create a URL-friendly slug from the title"""
    slug = title.lower()
    slug = slug.replace(' ', '-')
    # Remove special characters
    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789-'
    slug = ''.join(c for c in slug if c in allowed_chars)
    # Remove duplicate hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    return slug


def insert_post(title, date, author, content, image, slug):
    """Insert a new post into the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("""
            INSERT INTO posts (title, date, author, content, image, slug, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, date, author, content, image, slug, created_at))
        
        conn.commit()
        post_id = cur.lastrowid
        conn.close()
        
        return True, post_id
    except sqlite3.IntegrityError as e:
        return False, f"Error: Slug '{slug}' already exists. Please use a different title."
    except Exception as e:
        return False, f"Error inserting post: {e}"


def main():
    print("=" * 60)
    print("Add New Blog Post")
    print("=" * 60)
    print()
    
    # Get post details from user
    title = input("Post Title: ").strip()
    if not title:
        print("Error: Title is required!")
        return
    
    date = input("Post Date (YYYY-MM-DD) [press Enter for today]: ").strip()
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    author = input("Author Name: ").strip()
    if not author:
        print("Error: Author is required!")
        return
    
    print("\nPost Content (press Enter twice when finished):")
    content_lines = []
    while True:
        line = input()
        if line == "" and len(content_lines) > 0 and content_lines[-1] == "":
            content_lines.pop()  # Remove the last empty line
            break
        content_lines.append(line)
    
    content = "\n".join(content_lines).strip()
    if not content:
        print("Error: Content is required!")
        return
    
    image = input("\nImage filename (e.g., post-image.jpg): ").strip()
    
    # Generate slug
    suggested_slug = create_slug(title)
    slug = input(f"\nSlug [press Enter to use '{suggested_slug}']: ").strip()
    if not slug:
        slug = suggested_slug
    
    # Confirm before inserting
    print("\n" + "=" * 60)
    print("Post Preview:")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Date: {date}")
    print(f"Author: {author}")
    print(f"Content: {content[:100]}..." if len(content) > 100 else f"Content: {content}")
    print(f"Image: {image}")
    print(f"Slug: {slug}")
    print("=" * 60)
    
    confirm = input("\nAdd this post to the database? (y/n): ").strip().lower()
    
    if confirm == 'y':
        success, result = insert_post(title, date, author, content, image, slug)
        if success:
            print(f"\n✓ Post added successfully! (ID: {result})")
            print(f"  URL: /blog/{slug}")
        else:
            print(f"\n✗ {result}")
    else:
        print("\nPost not added.")


if __name__ == "__main__":
    main()
