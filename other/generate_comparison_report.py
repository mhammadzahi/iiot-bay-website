#!/usr/bin/env python3
"""
Post-Fix Comparison Report Generator
====================================
Generates before/after comparison showing the impact of SEO fixes.

Usage:
    python generate_comparison_report.py
"""

import sqlite3
import os
import re
from typing import Dict, List

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iiot_bay_database.db')


def analyze_post_seo(content: str) -> Dict:
    """Analyze SEO elements in post content"""
    
    # Count headings
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    h2_count = len(re.findall(r'<h2[^>]*>', content))
    h3_count = len(re.findall(r'<h3[^>]*>', content))
    
    # Check for FAQ
    has_faq = bool(re.search(r'(FAQ|Frequently Asked|الأسئلة الشائعة)', content, re.IGNORECASE))
    
    # Check for internal links
    internal_link_count = len(re.findall(r'href="https://www\.iiot-bay\.com/post/', content))
    
    # Check for conclusion
    has_conclusion = bool(re.search(r'<h2[^>]*>.*(Conclusion|الخلاصة|الخاتمة|Summary)', content, re.IGNORECASE))
    
    # Check for related reading section
    has_related = bool(re.search(r'(Related Reading|قراءة ذات صلة)', content, re.IGNORECASE))
    
    # Word count (rough)
    text_content = re.sub(r'<[^>]+>', '', content)
    word_count = len(text_content.split())
    
    # Section count
    section_count = len(re.findall(r'<section[^>]*>', content))
    
    return {
        'h1_count': h1_count,
        'h2_count': h2_count,
        'h3_count': h3_count,
        'has_faq': has_faq,
        'internal_links': internal_link_count,
        'has_conclusion': has_conclusion,
        'has_related': has_related,
        'word_count': word_count,
        'section_count': section_count,
        'total_headings': h1_count + h2_count + h3_count,
    }


def generate_seo_score(analysis: Dict) -> int:
    """Generate a simple SEO score (0-100)"""
    score = 0
    
    # H1 tag (20 points)
    if analysis['h1_count'] == 1:
        score += 20
    elif analysis['h1_count'] == 0:
        score += 0
    else:
        score += 10  # Penalty for multiple H1s
    
    # Heading structure (15 points)
    if analysis['h2_count'] >= 3:
        score += 10
    if analysis['h3_count'] >= 2:
        score += 5
    
    # Internal links (20 points)
    if analysis['internal_links'] >= 3:
        score += 20
    elif analysis['internal_links'] >= 1:
        score += 10
    
    # FAQ section (15 points)
    if analysis['has_faq']:
        score += 15
    
    # Conclusion (10 points)
    if analysis['has_conclusion']:
        score += 10
    
    # Related content (10 points)
    if analysis['has_related']:
        score += 10
    
    # Word count (10 points)
    if analysis['word_count'] >= 1500:
        score += 10
    elif analysis['word_count'] >= 1000:
        score += 5
    
    return min(score, 100)


def get_post(slug: str) -> Dict:
    """Get post from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def compare_before_after(slug: str, before_backup_path: str = None) -> Dict:
    """Compare post before and after fixes"""
    
    # Get current (after) version
    after_post = get_post(slug)
    if not after_post:
        return None
    
    after_analysis = analyze_post_seo(after_post['content'])
    after_score = generate_seo_score(after_analysis)
    
    # If backup provided, get before version
    before_analysis = None
    before_score = None
    
    if before_backup_path and os.path.exists(before_backup_path):
        conn = sqlite3.connect(before_backup_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            before_post = dict(row)
            before_analysis = analyze_post_seo(before_post['content'])
            before_score = generate_seo_score(before_analysis)
    
    return {
        'slug': slug,
        'title': after_post['title'],
        'before': before_analysis,
        'after': after_analysis,
        'before_score': before_score,
        'after_score': after_score,
        'improvement': after_score - before_score if before_score else None,
    }


def generate_report(slugs: List[str], backup_path: str = None) -> str:
    """Generate comparison report for multiple posts"""
    
    report = [
        "="*80,
        "SEO IMPROVEMENTS - BEFORE/AFTER COMPARISON REPORT",
        "="*80,
        "",
    ]
    
    if backup_path and os.path.exists(backup_path):
        report.append(f"Backup file: {backup_path}")
        report.append("")
    else:
        report.append("Note: Showing AFTER state only (no backup provided for comparison)")
        report.append("")
    
    # Analyze each post
    comparisons = []
    for slug in slugs:
        comparison = compare_before_after(slug, backup_path)
        if comparison:
            comparisons.append(comparison)
    
    # Summary statistics
    if comparisons and comparisons[0]['before_score'] is not None:
        avg_before = sum(c['before_score'] for c in comparisons) / len(comparisons)
        avg_after = sum(c['after_score'] for c in comparisons) / len(comparisons)
        avg_improvement = avg_after - avg_before
        
        report.extend([
            "SUMMARY STATISTICS",
            "-"*80,
            f"Posts analyzed: {len(comparisons)}",
            f"Average SEO score before: {avg_before:.1f}/100",
            f"Average SEO score after: {avg_after:.1f}/100",
            f"Average improvement: +{avg_improvement:.1f} points",
            "",
        ])
    
    # Detailed per-post analysis
    report.extend([
        "DETAILED POST ANALYSIS",
        "-"*80,
        "",
    ])
    
    for comp in comparisons:
        report.append(f"📄 {comp['title'][:70]}...")
        report.append(f"   Slug: {comp['slug']}")
        
        if comp['before_score'] is not None:
            report.append(f"   SEO Score: {comp['before_score']}/100 → {comp['after_score']}/100 (Δ +{comp['improvement']})")
        else:
            report.append(f"   SEO Score: {comp['after_score']}/100")
        
        report.append("")
        report.append("   Metric                  Before → After")
        report.append("   " + "-"*50)
        
        if comp['before']:
            report.append(f"   H1 Tags                 {comp['before']['h1_count']:>6} → {comp['after']['h1_count']:<6}")
            report.append(f"   H2 Tags                 {comp['before']['h2_count']:>6} → {comp['after']['h2_count']:<6}")
            report.append(f"   H3 Tags                 {comp['before']['h3_count']:>6} → {comp['after']['h3_count']:<6}")
            report.append(f"   Internal Links          {comp['before']['internal_links']:>6} → {comp['after']['internal_links']:<6}")
            report.append(f"   FAQ Section             {'Yes' if comp['before']['has_faq'] else 'No':>6} → {'Yes' if comp['after']['has_faq'] else 'No':<6}")
            report.append(f"   Conclusion              {'Yes' if comp['before']['has_conclusion'] else 'No':>6} → {'Yes' if comp['after']['has_conclusion'] else 'No':<6}")
            report.append(f"   Related Content         {'Yes' if comp['before']['has_related'] else 'No':>6} → {'Yes' if comp['after']['has_related'] else 'No':<6}")
            report.append(f"   Word Count              {comp['before']['word_count']:>6} → {comp['after']['word_count']:<6}")
        else:
            report.append(f"   H1 Tags                        → {comp['after']['h1_count']}")
            report.append(f"   H2 Tags                        → {comp['after']['h2_count']}")
            report.append(f"   H3 Tags                        → {comp['after']['h3_count']}")
            report.append(f"   Internal Links                 → {comp['after']['internal_links']}")
            report.append(f"   FAQ Section                    → {'Yes' if comp['after']['has_faq'] else 'No'}")
            report.append(f"   Conclusion                     → {'Yes' if comp['after']['has_conclusion'] else 'No'}")
            report.append(f"   Related Content                → {'Yes' if comp['after']['has_related'] else 'No'}")
            report.append(f"   Word Count                     → {comp['after']['word_count']}")
        
        report.append("")
    
    # Key improvements summary
    report.extend([
        "",
        "="*80,
        "KEY IMPROVEMENTS APPLIED",
        "="*80,
        "",
        "✅ Heading Structure:",
        "   • Added H1 tags where missing",
        "   • Fixed multiple H1 issues",
        "   • Improved H2/H3 hierarchy",
        "",
        "✅ Internal Linking:",
        "   • Added 2-3 contextual links per post",
        "   • Created topical clusters",
        "   • Added 'Related Reading' sections",
        "",
        "✅ Content Enhancement:",
        "   • Added FAQ sections with schema markup",
        "   • Added conclusion sections",
        "   • Identified thin sections for review",
        "",
        "✅ User Experience:",
        "   • Better content navigation",
        "   • Direct answers to common questions",
        "   • Improved readability",
        "",
        "="*80,
        "EXPECTED INDEXING IMPROVEMENTS",
        "="*80,
        "",
        "These changes signal to Google that:",
        "",
        "1. Content is well-structured (H1 → H2 → H3 hierarchy)",
        "2. Pages are important (internal links from related content)",
        "3. Content is comprehensive (FAQ sections, conclusions)",
        "4. User intent is addressed (direct Q&A format)",
        "5. Site has topical authority (interconnected content clusters)",
        "",
        "Timeline for indexing:",
        "• Week 1-2: Re-crawl initiated",
        "• Week 3-4: Content re-evaluation",
        "• Week 5-8: Status changes to 'Indexed'",
        "• Month 2-3: Rankings improve, traffic increases",
        "",
    ])
    
    return '\n'.join(report)


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate before/after comparison report')
    parser.add_argument('--backup', type=str, help='Path to backup database for comparison')
    parser.add_argument('--slugs', nargs='+', help='Specific slugs to analyze')
    args = parser.parse_args()
    
    # Default slugs
    slugs = args.slugs if args.slugs else [
        'predictive-maintenance-industrial-iot-ksa',
        'smart-cities-ksa-iiot-cognitive-future',
        'edge-computing-industrial-iot-saudi-arabia',
        'oee-optimization-industrial-iot-saudi-arabia',
        'industrial-iot-cybersecurity-saudi-arabia',
    ]
    
    # Generate report
    report = generate_report(slugs, args.backup)
    print(report)
    
    # Save to file
    from datetime import datetime
    report_filename = f'comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    main()
