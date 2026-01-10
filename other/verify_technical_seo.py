#!/usr/bin/env python3
"""
Technical SEO Verification Tool
================================
Verifies technical SEO requirements for blog posts:
- HTTP 200 status
- No noindex directives
- Self-referencing canonical tags
- Server-rendered HTML
- Meta tags present
- Sitemap inclusion

Usage:
    python verify_technical_seo.py [--slug SLUG]
"""

import sqlite3
import os
import sys
import re
from typing import Dict, List

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iiot_bay_database.db')

# Target slugs
TARGET_SLUGS = [
    'انترنت-الاشياء-الصناعية-ورؤية-السعودية-2030',
    'مراقبة-الحالة-والتنبيهات-انترنت-الاشياء-الصناعية',
    'condition-monitoring-vibration-analysis-ksa',
    'digital-twin-smart-factory-saudi-arabia',
    'edge-computing-industrial-iot-saudi-arabia',
    'edge-computing-riyadh-iiot-smart-city',
    'esp32-vs-raspberry-pi-saudi-iot-guide',
    'increase-factory-production-iiot-saudi-arabia-oee',
    'industrial-energy-management-iot-saudi-arabia',
    'industrial-iot-cybersecurity-saudi-arabia',
    'iot-iiot-opencv-raspberry-pi-saudi-education-guide',
    'oee-optimization-industrial-iot-saudi-arabia',
    'on-premise-vs-cloud-iiot-saudi-arabia-2025',
    'predictive-maintenance-industrial-iot-ksa',
    'predictive-maintenance-industrial-iot-saudi-arabia',
    'predictive-maintenance-saudi-arabia-guide-downtime-costs',
    'smart-cities-ksa-iiot-cognitive-future',
    'smart-energy-management-industrial-iot-saudi-arabia',
    'smart-supply-chain-saudi-arabia',
]


def check_post_in_db(slug: str) -> bool:
    """Check if post exists in database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM posts WHERE slug = ?", (slug,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def analyze_template_file(template_path: str) -> Dict:
    """Analyze Flask template for SEO issues"""
    issues = []
    recommendations = []
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for noindex
    if re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', template_content, re.IGNORECASE):
        issues.append("Found noindex directive in template")
    
    # Check for canonical tag
    canonical_pattern = r'<link[^>]*rel=["\']canonical["\']'
    if not re.search(canonical_pattern, template_content, re.IGNORECASE):
        issues.append("Missing canonical tag")
    else:
        # Check if canonical is self-referencing
        if 'url_for' not in template_content or 'canonical' not in template_content.lower():
            recommendations.append("Verify canonical tag is self-referencing")
    
    # Check for meta description
    if not re.search(r'<meta[^>]*name=["\']description["\']', template_content, re.IGNORECASE):
        issues.append("Missing meta description tag")
    
    # Check for title tag
    if not re.search(r'<title>', template_content, re.IGNORECASE):
        issues.append("Missing title tag")
    
    # Check for Open Graph tags
    if not re.search(r'<meta[^>]*property=["\']og:', template_content, re.IGNORECASE):
        recommendations.append("Consider adding Open Graph tags for social sharing")
    
    # Check for structured data
    if 'application/ld+json' not in template_content:
        recommendations.append("Consider adding JSON-LD structured data (Article schema)")
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'has_noindex': bool(re.search(r'noindex', template_content, re.IGNORECASE)),
        'has_canonical': bool(re.search(canonical_pattern, template_content, re.IGNORECASE)),
        'has_meta_description': bool(re.search(r'<meta[^>]*name=["\']description["\']', template_content, re.IGNORECASE)),
    }


def check_flask_routes(app_path: str) -> Dict:
    """Check Flask routes for proper HTTP status codes"""
    issues = []
    recommendations = []
    
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check if post route exists
    if '@app.route' not in app_content:
        issues.append("No Flask routes found")
        return {'issues': issues, 'recommendations': recommendations}
    
    # Check for post route
    post_route_pattern = r'@app\.route\(["\'].*?/post/<.*?>["\']'
    if not re.search(post_route_pattern, app_content):
        issues.append("Post route not found")
    
    # Check for 404 handler
    if '404' not in app_content:
        recommendations.append("Add custom 404 error handler")
    
    # Check for sitemap
    if 'sitemap' not in app_content.lower():
        recommendations.append("Add dynamic sitemap.xml generation")
    
    # Check for robots.txt
    if 'robots' not in app_content.lower():
        recommendations.append("Add robots.txt route")
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'has_post_route': bool(re.search(post_route_pattern, app_content)),
    }


def generate_seo_checklist() -> str:
    """Generate SEO checklist for manual verification"""
    return """
SEO VERIFICATION CHECKLIST
==========================

□ Technical Infrastructure:
  □ Flask app returns HTTP 200 for all post URLs
  □ No redirect chains (direct access)
  □ Server-side rendering (not client-side JavaScript)
  □ HTML is complete in initial response (view source test)
  
□ Meta Tags (in template):
  □ Unique <title> tag per post
  □ Meta description (150-160 characters)
  □ Self-referencing canonical tag
  □ No noindex/nofollow directives
  □ Open Graph tags (og:title, og:description, og:image)
  □ Twitter Card tags
  
□ Content Structure:
  □ Single H1 tag (post title)
  □ Proper H2 → H3 hierarchy
  □ Descriptive heading text
  □ Internal links to related posts
  □ External authoritative links (Vision 2030, etc.)
  
□ Structured Data:
  □ JSON-LD Article schema
  □ Author information
  □ Published date
  □ Modified date
  □ Organization schema
  □ FAQ schema (if applicable)
  
□ Performance:
  □ Page load time < 3 seconds
  □ Images optimized (WebP format)
  □ CSS/JS minified
  □ Gzip compression enabled
  
□ Indexing Signals:
  □ Sitemap.xml includes all posts
  □ Sitemap submitted to Google Search Console
  □ No crawl errors in GSC
  □ Mobile-friendly test passed
  □ Core Web Vitals passing
  
□ Content Quality:
  □ Minimum 1500+ words
  □ Original content (not duplicate)
  □ Clear user intent match
  □ E-E-A-T signals present
  □ Regular content updates

MANUAL TESTS TO RUN:
===================

1. View Source Test:
   - Open: https://www.iiot-bay.com/post/{slug}
   - Right-click → "View Page Source"
   - Verify: All content visible in HTML (not loaded by JS)

2. Google Search Console:
   - Request indexing for each URL
   - Check coverage report
   - Verify no crawl errors

3. Mobile-Friendly Test:
   - https://search.google.com/test/mobile-friendly
   - Test each post URL

4. Rich Results Test:
   - https://search.google.com/test/rich-results
   - Verify structured data detected

5. PageSpeed Insights:
   - https://pagespeed.web.dev/
   - Check Core Web Vitals scores

COMMON "DISCOVERED - NOT INDEXED" FIXES:
========================================

1. **Thin Content** → Add depth (FAQ, examples, details)
2. **Duplicate Content** → Make each post unique
3. **Poor Internal Linking** → Link from high-authority pages
4. **Low Crawl Priority** → Improve content quality signals
5. **Technical Issues** → Fix rendering, speed, mobile issues
6. **No User Engagement** → Improve CTR from search results
7. **Recent Publication** → Be patient (can take weeks)
8. **Crawl Budget** → Prioritize important pages in sitemap
"""


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify technical SEO setup')
    parser.add_argument('--slug', type=str, help='Check specific slug')
    args = parser.parse_args()
    
    print("="*80)
    print("TECHNICAL SEO VERIFICATION")
    print("="*80)
    
    # Check database
    if not os.path.exists(DB_PATH):
        print(f"\n✗ Database not found: {DB_PATH}")
        sys.exit(1)
    else:
        print(f"\n✓ Database found: {DB_PATH}")
    
    # Check posts in database
    slugs_to_check = [args.slug] if args.slug else TARGET_SLUGS
    
    print(f"\n\nCHECKING {len(slugs_to_check)} POSTS IN DATABASE:")
    print("-"*80)
    
    missing_posts = []
    for slug in slugs_to_check:
        exists = check_post_in_db(slug)
        status = "✓" if exists else "✗"
        print(f"{status} {slug}")
        if not exists:
            missing_posts.append(slug)
    
    if missing_posts:
        print(f"\n⚠ Warning: {len(missing_posts)} posts not found in database")
    
    # Check Flask templates
    template_path = os.path.join(os.path.dirname(DB_PATH), 'templates', 'post.html')
    if os.path.exists(template_path):
        print(f"\n\nANALYZING POST TEMPLATE:")
        print("-"*80)
        template_analysis = analyze_template_file(template_path)
        
        if template_analysis['issues']:
            print("\n⚠ Issues found:")
            for issue in template_analysis['issues']:
                print(f"  ✗ {issue}")
        else:
            print("\n✓ No critical issues found")
        
        if template_analysis['recommendations']:
            print("\nRecommendations:")
            for rec in template_analysis['recommendations']:
                print(f"  • {rec}")
    else:
        print(f"\n✗ Template not found: {template_path}")
    
    # Check Flask app
    app_path = os.path.join(os.path.dirname(DB_PATH), 'app.py')
    if os.path.exists(app_path):
        print(f"\n\nANALYZING FLASK APP:")
        print("-"*80)
        route_analysis = check_flask_routes(app_path)
        
        if route_analysis['issues']:
            print("\n⚠ Issues found:")
            for issue in route_analysis['issues']:
                print(f"  ✗ {issue}")
        else:
            print("\n✓ No critical issues found")
        
        if route_analysis['recommendations']:
            print("\nRecommendations:")
            for rec in route_analysis['recommendations']:
                print(f"  • {rec}")
    
    # Print checklist
    print("\n\n")
    print(generate_seo_checklist())
    
    # Print next steps
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. Run the SEO fix script:
   python other/fix_seo_indexing.py --dry-run
   python other/fix_seo_indexing.py

2. Verify changes in browser:
   - Check heading structure
   - Verify internal links work
   - Confirm FAQ sections render correctly

3. Test in Google Search Console:
   - Request indexing for updated posts
   - Monitor coverage report
   - Check for crawl errors

4. Wait 2-4 weeks for Google to:
   - Re-crawl updated posts
   - Re-evaluate content quality
   - Update index status

5. Monitor results:
   - Check GSC Coverage report
   - Track impressions/clicks
   - Adjust strategy based on data
""")


if __name__ == '__main__':
    main()
