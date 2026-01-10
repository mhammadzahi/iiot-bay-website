#!/usr/bin/env python3
"""
SEO Indexing Fixer for IIoT-Bay Blog Posts
==========================================
Fixes "Discovered – currently not indexed" issues by improving:
- Content quality and depth
- Heading structure (H1/H2/H3 hierarchy)
- Internal linking
- FAQ sections
- Technical SEO signals

Usage:
    python fix_seo_indexing.py [--dry-run] [--slug SLUG]
"""

import sqlite3
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iiot_bay_database.db')

# Target slugs to fix
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

# Internal linking map (topic -> related slugs)
INTERNAL_LINKS = {
    'predictive-maintenance': [
        'predictive-maintenance-industrial-iot-ksa',
        'predictive-maintenance-industrial-iot-saudi-arabia',
        'predictive-maintenance-saudi-arabia-guide-downtime-costs',
        'condition-monitoring-vibration-analysis-ksa',
    ],
    'iot-hardware': [
        'esp32-vs-raspberry-pi-saudi-iot-guide',
        'iot-iiot-opencv-raspberry-pi-saudi-education-guide',
        'edge-computing-industrial-iot-saudi-arabia',
        'edge-computing-riyadh-iiot-smart-city',
    ],
    'oee-optimization': [
        'oee-optimization-industrial-iot-saudi-arabia',
        'increase-factory-production-iiot-saudi-arabia-oee',
    ],
    'energy-management': [
        'industrial-energy-management-iot-saudi-arabia',
        'smart-energy-management-industrial-iot-saudi-arabia',
    ],
    'smart-cities': [
        'smart-cities-ksa-iiot-cognitive-future',
        'edge-computing-riyadh-iiot-smart-city',
    ],
    'digital-twin': [
        'digital-twin-smart-factory-saudi-arabia',
    ],
    'cybersecurity': [
        'industrial-iot-cybersecurity-saudi-arabia',
    ],
    'supply-chain': [
        'smart-supply-chain-saudi-arabia',
    ],
    'cloud-vs-onpremise': [
        'on-premise-vs-cloud-iiot-saudi-arabia-2025',
    ],
}

# FAQ templates by topic
FAQ_TEMPLATES = {
    'predictive-maintenance': {
        'en': [
            {
                'q': 'What is the difference between predictive and preventive maintenance?',
                'a': 'Preventive maintenance follows fixed schedules regardless of equipment condition, while predictive maintenance uses real-time sensor data and analytics to predict failures before they occur. This reduces unnecessary maintenance and prevents unexpected downtime.'
            },
            {
                'q': 'How much can predictive maintenance reduce downtime in Saudi factories?',
                'a': 'Studies show that predictive maintenance can reduce unplanned downtime by 30-50% in industrial facilities. For Saudi Arabian factories operating in harsh conditions, these improvements can significantly impact OEE and production capacity.'
            },
            {
                'q': 'What sensors are needed for predictive maintenance in Saudi Arabia?',
                'a': 'Common sensors include vibration sensors for rotating equipment, temperature sensors for bearings and motors, current sensors for electrical monitoring, and pressure sensors for hydraulic systems. All equipment must be rated for high temperatures and dust ingress common in the Kingdom.'
            },
        ],
        'ar': [
            {
                'q': 'ما الفرق بين الصيانة التنبؤية والصيانة الوقائية؟',
                'a': 'الصيانة الوقائية تتبع جداول زمنية ثابتة بغض النظر عن حالة المعدات، بينما تستخدم الصيانة التنبؤية بيانات المستشعرات في الوقت الفعلي والتحليلات للتنبؤ بالأعطال قبل حدوثها. هذا يقلل من الصيانة غير الضرورية ويمنع التوقف غير المتوقع.'
            },
            {
                'q': 'كم يمكن للصيانة التنبؤية أن تقلل من وقت التوقف في المصانع السعودية؟',
                'a': 'تظهر الدراسات أن الصيانة التنبؤية يمكن أن تقلل من وقت التوقف غير المخطط له بنسبة 30-50٪ في المنشآت الصناعية. بالنسبة للمصانع السعودية التي تعمل في ظروف قاسية، يمكن لهذه التحسينات أن تؤثر بشكل كبير على الكفاءة الإنتاجية.'
            },
        ]
    },
    'oee': {
        'en': [
            {
                'q': 'What is OEE and why does it matter?',
                'a': 'OEE (Overall Equipment Effectiveness) measures manufacturing productivity by combining availability, performance, and quality metrics. It helps Saudi factories identify bottlenecks and improve competitiveness in alignment with Vision 2030 goals.'
            },
            {
                'q': 'What is a good OEE score for Saudi manufacturing?',
                'a': 'World-class OEE is 85% or higher. Many Saudi factories operate between 50-70% OEE. Even a 5% improvement can significantly increase production capacity without capital investment in new equipment.'
            },
        ]
    },
    'iot-hardware': {
        'en': [
            {
                'q': 'ESP32 vs Raspberry Pi: Which is better for industrial IoT in Saudi Arabia?',
                'a': 'ESP32 is ideal for distributed sensors and battery-powered applications due to low power consumption. Raspberry Pi suits edge computing, data aggregation, and applications requiring more processing power. Many Saudi projects use both in complementary roles.'
            },
            {
                'q': 'Can IoT devices withstand Saudi Arabia\'s harsh industrial environment?',
                'a': 'Yes, with proper enclosures rated for high temperatures (50°C+), dust ingress (IP65 or higher), and industrial-grade components. Commercial IoT devices often fail without these protections.'
            },
        ]
    },
    'smart-cities': {
        'en': [
            {
                'q': 'How does IIoT support Saudi Arabia\'s smart city initiatives?',
                'a': 'Industrial IoT provides the sensor infrastructure, edge computing, and data analytics needed for smart cities. Projects like NEOM and Riyadh Smart City rely on IIoT for energy management, traffic optimization, and environmental monitoring.'
            },
        ]
    },
    'cybersecurity': {
        'en': [
            {
                'q': 'What are the main cybersecurity risks for Industrial IoT in Saudi Arabia?',
                'a': 'Key risks include unauthorized access to OT networks, malware targeting industrial controllers, data breaches, and supply chain vulnerabilities. Saudi Arabia\'s National Cybersecurity Authority (NCA) provides specific guidelines for industrial sectors.'
            },
            {
                'q': 'How can Saudi factories secure their IIoT deployments?',
                'a': 'Implement network segmentation, use industrial firewalls, deploy intrusion detection systems, maintain regular security updates, and follow NCA guidelines. On-premise solutions often provide better control for sensitive operations.'
            },
        ]
    },
}


class SEOFixer:
    """Fix SEO indexing issues for blog posts"""
    
    def __init__(self, db_path: str, dry_run: bool = False):
        self.db_path = db_path
        self.dry_run = dry_run
        self.changes_log = []
        
    def connect_db(self) -> sqlite3.Connection:
        """Connect to SQLite database"""
        return sqlite3.connect(self.db_path)
    
    def get_post(self, slug: str) -> Dict:
        """Retrieve post by slug"""
        conn = self.connect_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def detect_language(self, content: str) -> str:
        """Detect if content is Arabic or English"""
        arabic_chars = re.findall(r'[\u0600-\u06FF]', content)
        return 'ar' if len(arabic_chars) > 100 else 'en'
    
    def fix_heading_structure(self, content: str, title: str) -> Tuple[str, List[str]]:
        """
        Fix heading hierarchy (H1 -> H2 -> H3)
        Ensure H1 exists and is used only once
        """
        changes = []
        
        # Check if H1 exists
        h1_match = re.search(r'<h1[^>]*>.*?</h1>', content, re.DOTALL)
        
        if not h1_match:
            # Add H1 at the beginning of article if missing
            article_start = re.search(r'(<article[^>]*>)', content)
            if article_start:
                # Check if there's already a header section
                header_match = re.search(r'<header>.*?</header>', content, re.DOTALL)
                if header_match:
                    # Add H1 after header
                    insert_pos = header_match.end()
                else:
                    # Add H1 right after article tag
                    insert_pos = article_start.end()
                
                h1_tag = f'\n    <h1>{title}</h1>\n'
                content = content[:insert_pos] + h1_tag + content[insert_pos:]
                changes.append("Added H1 heading with post title")
        
        # Check for multiple H1 tags (should only be one)
        h1_count = len(re.findall(r'<h1[^>]*>', content))
        if h1_count > 1:
            # Convert additional H1 tags to H2
            first_h1_found = False
            def replace_extra_h1(match):
                nonlocal first_h1_found
                if not first_h1_found:
                    first_h1_found = True
                    return match.group(0)
                else:
                    return match.group(0).replace('<h1', '<h2').replace('</h1>', '</h2>')
            
            content = re.sub(r'<h1[^>]*>.*?</h1>', replace_extra_h1, content, flags=re.DOTALL)
            changes.append(f"Converted {h1_count - 1} additional H1 tags to H2")
        
        # Ensure proper H2 -> H3 hierarchy (no H3 before H2)
        has_h2 = bool(re.search(r'<h2[^>]*>', content))
        h3_before_h2 = re.search(r'<h3[^>]*>.*?<h2[^>]*>', content, re.DOTALL)
        
        if not has_h2 and re.search(r'<h3[^>]*>', content):
            # If there are H3 but no H2, convert first level H3 to H2
            content = re.sub(r'<h3([^>]*)>', r'<h2\1>', content, count=1)
            content = re.sub(r'</h3>', '</h2>', content, count=1)
            changes.append("Converted orphan H3 to H2 for proper hierarchy")
        
        return content, changes
    
    def add_internal_links(self, content: str, current_slug: str, lang: str) -> Tuple[str, List[str]]:
        """
        Add contextual internal links to related posts
        Only add if not already linked
        """
        changes = []
        added_links = 0
        
        # Find related posts based on topic
        related_slugs = []
        for topic, slugs in INTERNAL_LINKS.items():
            if current_slug in slugs:
                # Get other posts in same topic
                related_slugs.extend([s for s in slugs if s != current_slug])
        
        if not related_slugs:
            return content, changes
        
        # Limit to 2-3 internal links to avoid over-optimization
        related_slugs = related_slugs[:3]
        
        # Create link patterns to check if already linked
        for related_slug in related_slugs:
            link_pattern = f'/post/{related_slug}'
            if link_pattern in content:
                continue  # Already linked
            
            # Find appropriate anchor text based on slug keywords
            anchor_texts = self._generate_anchor_texts(related_slug, lang)
            
            # Try to find and replace first occurrence of anchor text
            for anchor_text in anchor_texts:
                # Look for the text in a paragraph (not in headings or existing links)
                pattern = f'<p>([^<]*?)({re.escape(anchor_text)})([^<]*?)</p>'
                match = re.search(pattern, content, re.IGNORECASE)
                
                if match:
                    linked_text = f'<a href="https://www.iiot-bay.com/post/{related_slug}">{anchor_text}</a>'
                    replacement = f'<p>{match.group(1)}{linked_text}{match.group(3)}</p>'
                    content = content[:match.start()] + replacement + content[match.end():]
                    added_links += 1
                    changes.append(f"Added internal link to {related_slug}")
                    break
        
        if added_links == 0:
            # If no natural anchor text found, add a "Related Reading" section
            related_section = self._create_related_reading_section(related_slugs, lang)
            # Add before closing article tag
            content = re.sub(r'</article>', f'{related_section}\n</article>', content)
            changes.append(f"Added 'Related Reading' section with {len(related_slugs)} links")
        
        return content, changes
    
    def _generate_anchor_texts(self, slug: str, lang: str) -> List[str]:
        """Generate natural anchor text options based on slug"""
        slug_words = slug.replace('-', ' ')
        
        if lang == 'ar':
            anchor_map = {
                'انترنت-الاشياء': ['إنترنت الأشياء الصناعية', 'انترنت الاشياء الصناعية'],
                'مراقبة-الحالة': ['مراقبة الحالة', 'أنظمة مراقبة الحالة'],
                'الصيانة-التنبؤية': ['الصيانة التنبؤية', 'نظام الصيانة التنبؤية'],
            }
        else:
            anchor_map = {
                'predictive-maintenance': ['predictive maintenance', 'Predictive Maintenance', 'predictive maintenance solutions'],
                'condition-monitoring': ['condition monitoring', 'Condition Monitoring', 'vibration analysis'],
                'digital-twin': ['Digital Twin', 'digital twin technology', 'digital twins'],
                'edge-computing': ['Edge Computing', 'edge computing', 'edge AI'],
                'esp32': ['ESP32', 'ESP32 microcontrollers'],
                'raspberry-pi': ['Raspberry Pi', 'Raspberry Pi platforms'],
                'oee': ['OEE', 'Overall Equipment Effectiveness', 'OEE optimization'],
                'energy-management': ['energy management', 'industrial energy management'],
                'cybersecurity': ['Industrial IoT cybersecurity', 'IIoT security'],
                'smart-cities': ['Smart Cities', 'smart city initiatives'],
                'supply-chain': ['smart supply chain', 'supply chain optimization'],
            }
        
        # Find matching anchors
        for key, anchors in anchor_map.items():
            if key in slug:
                return anchors
        
        # Fallback: use slug as anchor text
        return [slug_words.title()]
    
    def _create_related_reading_section(self, slugs: List[str], lang: str) -> str:
        """Create a 'Related Reading' section with links"""
        if lang == 'ar':
            title = 'قراءة ذات صلة'
            intro = 'للمزيد من المعلومات، راجع هذه المقالات:'
        else:
            title = 'Related Reading'
            intro = 'For more information, see these related articles:'
        
        links_html = '\n'.join([
            f'            <li><a href="https://www.iiot-bay.com/post/{slug}">{self._slug_to_title(slug)}</a></li>'
            for slug in slugs
        ])
        
        return f'''
    <section class="related-reading">
        <h2>{title}</h2>
        <p>{intro}</p>
        <ul>
{links_html}
        </ul>
    </section>'''
    
    def _slug_to_title(self, slug: str) -> str:
        """Convert slug to readable title"""
        return slug.replace('-', ' ').title()
    
    def add_faq_section(self, content: str, slug: str, lang: str) -> Tuple[str, List[str]]:
        """
        Add FAQ section if not present
        Helps with featured snippets and provides user value
        """
        changes = []
        
        # Check if FAQ already exists
        if 'FAQ' in content or 'Frequently Asked' in content or 'الأسئلة الشائعة' in content:
            return content, changes
        
        # Determine topic for FAQ
        faq_topic = self._determine_faq_topic(slug)
        if not faq_topic or faq_topic not in FAQ_TEMPLATES:
            return content, changes
        
        # Get FAQ template
        faq_data = FAQ_TEMPLATES[faq_topic].get(lang, FAQ_TEMPLATES[faq_topic].get('en', []))
        if not faq_data:
            return content, changes
        
        # Generate FAQ section
        faq_html = self._generate_faq_html(faq_data, lang)
        
        # Insert before closing article tag
        content = re.sub(r'</article>', f'{faq_html}\n</article>', content)
        changes.append(f"Added FAQ section with {len(faq_data)} questions")
        
        return content, changes
    
    def _determine_faq_topic(self, slug: str) -> str:
        """Determine FAQ topic based on slug"""
        if any(term in slug for term in ['predictive-maintenance', 'الصيانة-التنبؤية', 'condition-monitoring']):
            return 'predictive-maintenance'
        elif any(term in slug for term in ['oee', 'production']):
            return 'oee'
        elif any(term in slug for term in ['esp32', 'raspberry', 'opencv', 'hardware']):
            return 'iot-hardware'
        elif any(term in slug for term in ['smart-cities', 'المدن-الذكية']):
            return 'smart-cities'
        elif 'cybersecurity' in slug or 'أمن' in slug:
            return 'cybersecurity'
        return None
    
    def _generate_faq_html(self, faq_data: List[Dict], lang: str) -> str:
        """Generate FAQ HTML with schema.org markup"""
        if lang == 'ar':
            title = 'الأسئلة الشائعة'
        else:
            title = 'Frequently Asked Questions'
        
        faq_items = '\n'.join([
            f'''        <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
            <h3 itemprop="name">{item['q']}</h3>
            <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">{item['a']}</p>
            </div>
        </div>'''
            for item in faq_data
        ])
        
        return f'''
    <section class="faq-section" itemscope itemtype="https://schema.org/FAQPage">
        <h2>{title}</h2>
{faq_items}
    </section>'''
    
    def enhance_content_depth(self, content: str, slug: str, lang: str) -> Tuple[str, List[str]]:
        """
        Enhance thin content sections
        Add more context and examples where needed
        """
        changes = []
        
        # Count words in content (rough estimate)
        text_content = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_content.split())
        
        if word_count < 1500:
            changes.append(f"Content is relatively short ({word_count} words) - consider manual expansion")
        
        # Check for very short sections (less than 50 words)
        sections = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)
        for i, section in enumerate(sections):
            section_text = re.sub(r'<[^>]+>', '', section)
            section_words = len(section_text.split())
            if section_words < 50 and section_words > 0:
                changes.append(f"Section {i+1} is thin ({section_words} words) - consider adding more detail")
        
        # Add conclusion section if missing
        if not re.search(r'<h2[^>]*>.*?(Conclusion|الخلاصة|الخاتمة|Summary).*?</h2>', content, re.IGNORECASE):
            conclusion = self._generate_conclusion(slug, lang)
            content = re.sub(r'</article>', f'{conclusion}\n</article>', content)
            changes.append("Added conclusion section")
        
        return content, changes
    
    def _generate_conclusion(self, slug: str, lang: str) -> str:
        """Generate a conclusion section"""
        if lang == 'ar':
            title = 'الخلاصة'
            text = '''        <p>
            يمثل إنترنت الأشياء الصناعية فرصة استراتيجية للمصانع السعودية لتحسين الكفاءة التشغيلية وتقليل التكاليف ودعم أهداف رؤية 2030. 
            من خلال اعتماد التقنيات الحديثة والممارسات الأفضل، يمكن للشركات الصناعية تحقيق ميزة تنافسية مستدامة.
        </p>
        <p>
            للحصول على استشارة مخصصة حول تنفيذ حلول إنترنت الأشياء الصناعية في منشأتك، تواصل مع فريق IIoT-Bay.
        </p>'''
        else:
            title = 'Conclusion'
            text = '''        <p>
            Industrial IoT represents a strategic opportunity for Saudi factories to improve operational efficiency, reduce costs, and support Vision 2030 goals. 
            By adopting modern technologies and best practices, industrial companies can achieve sustainable competitive advantage.
        </p>
        <p>
            For personalized consultation on implementing Industrial IoT solutions in your facility, contact the IIoT-Bay team.
        </p>'''
        
        return f'''
    <section class="conclusion">
        <h2>{title}</h2>
{text}
    </section>'''
    
    def update_post(self, slug: str, new_content: str, new_title: str = None) -> bool:
        """Update post in database"""
        if self.dry_run:
            print(f"[DRY RUN] Would update post: {slug}")
            return True
        
        try:
            conn = self.connect_db()
            cur = conn.cursor()
            
            if new_title:
                cur.execute(
                    "UPDATE posts SET content = ?, title = ? WHERE slug = ?",
                    (new_content, new_title, slug)
                )
            else:
                cur.execute(
                    "UPDATE posts SET content = ? WHERE slug = ?",
                    (new_content, slug)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating post {slug}: {e}")
            return False
    
    def process_post(self, slug: str) -> Dict:
        """Process a single post with all improvements"""
        print(f"\n{'='*80}")
        print(f"Processing: {slug}")
        print(f"{'='*80}")
        
        # Get post
        post = self.get_post(slug)
        if not post:
            return {
                'slug': slug,
                'status': 'error',
                'message': 'Post not found in database'
            }
        
        content = post['content']
        title = post['title']
        lang = self.detect_language(content)
        
        print(f"Language: {lang}")
        print(f"Current title: {title}")
        print(f"Content length: {len(content)} characters")
        
        all_changes = []
        
        # 1. Fix heading structure
        content, changes = self.fix_heading_structure(content, title)
        all_changes.extend(changes)
        
        # 2. Add internal links
        content, changes = self.add_internal_links(content, slug, lang)
        all_changes.extend(changes)
        
        # 3. Add FAQ section
        content, changes = self.add_faq_section(content, slug, lang)
        all_changes.extend(changes)
        
        # 4. Enhance content depth
        content, changes = self.enhance_content_depth(content, slug, lang)
        all_changes.extend(changes)
        
        # Print changes
        if all_changes:
            print("\nChanges made:")
            for i, change in enumerate(all_changes, 1):
                print(f"  {i}. {change}")
        else:
            print("\nNo changes needed - content is already well-optimized")
        
        # Update database
        if all_changes and not self.dry_run:
            success = self.update_post(slug, content)
            if success:
                print(f"\n✓ Post updated successfully")
            else:
                print(f"\n✗ Failed to update post")
                return {
                    'slug': slug,
                    'status': 'error',
                    'message': 'Failed to update database',
                    'changes': all_changes
                }
        
        return {
            'slug': slug,
            'status': 'success',
            'changes': all_changes,
            'language': lang,
            'dry_run': self.dry_run
        }
    
    def process_all_posts(self, slugs: List[str] = None) -> List[Dict]:
        """Process all target posts"""
        if slugs is None:
            slugs = TARGET_SLUGS
        
        results = []
        for slug in slugs:
            result = self.process_post(slug)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate summary report"""
        report = [
            "\n" + "="*80,
            "SEO INDEXING FIX - SUMMARY REPORT",
            "="*80,
            f"\nTotal posts processed: {len(results)}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        ]
        
        successful = [r for r in results if r['status'] == 'success' and r.get('changes')]
        no_changes = [r for r in results if r['status'] == 'success' and not r.get('changes')]
        errors = [r for r in results if r['status'] == 'error']
        
        report.append(f"✓ Successfully updated: {len(successful)}")
        report.append(f"- No changes needed: {len(no_changes)}")
        report.append(f"✗ Errors: {len(errors)}")
        
        if successful:
            report.append("\n" + "-"*80)
            report.append("UPDATED POSTS:")
            report.append("-"*80)
            for r in successful:
                report.append(f"\n{r['slug']}")
                report.append(f"  Language: {r.get('language', 'N/A')}")
                report.append(f"  Changes: {len(r['changes'])}")
                for change in r['changes']:
                    report.append(f"    • {change}")
        
        if errors:
            report.append("\n" + "-"*80)
            report.append("ERRORS:")
            report.append("-"*80)
            for r in errors:
                report.append(f"\n{r['slug']}: {r.get('message', 'Unknown error')}")
        
        report.append("\n" + "="*80)
        report.append("WHY THESE CHANGES HELP WITH INDEXING:")
        report.append("="*80)
        report.append("""
1. **Proper Heading Structure (H1 → H2 → H3)**
   - Helps Google understand content hierarchy
   - Improves crawl efficiency and content parsing
   - Signals clear information architecture

2. **Internal Linking**
   - Distributes page authority across related content
   - Helps Google discover and crawl related pages
   - Increases time on site and reduces bounce rate
   - Shows topical relevance and site depth

3. **FAQ Sections**
   - Targets featured snippets and People Also Ask
   - Adds structured data (schema.org/FAQPage)
   - Answers user intent directly
   - Increases content depth and dwell time

4. **Content Depth Enhancement**
   - Reduces thin content signals
   - Provides more comprehensive coverage
   - Increases page value and crawl priority
   - Improves E-E-A-T signals (Experience, Expertise, Authority, Trust)

5. **Technical SEO Foundation**
   - Server-rendered HTML (Flask)
   - Self-referencing canonical tags
   - No noindex directives
   - Clean URL structure

These improvements signal to Google that the content is:
- Well-structured and easy to parse
- Comprehensive and valuable to users
- Part of a cohesive topical cluster
- Worth prioritizing for indexing and ranking
""")
        
        return '\n'.join(report)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix SEO indexing issues for IIoT-Bay blog posts')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without updating database')
    parser.add_argument('--slug', type=str, help='Process only a specific slug')
    args = parser.parse_args()
    
    # Check database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
    
    # Initialize fixer
    fixer = SEOFixer(DB_PATH, dry_run=args.dry_run)
    
    # Process posts
    if args.slug:
        results = [fixer.process_post(args.slug)]
    else:
        results = fixer.process_all_posts()
    
    # Generate and print report
    report = fixer.generate_report(results)
    print(report)
    
    # Save report to file
    report_path = os.path.join(os.path.dirname(__file__), f'seo_fix_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    main()
