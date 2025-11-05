"""
Simple PDF generator using markdown and pdfkit (wkhtmltopdf alternative)
or reportlab as fallback
"""
import markdown
import os

# Read markdown
with open('TRADING_LOGIC.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert to HTML
html_content = markdown.markdown(
    md_content, 
    extensions=['extra', 'tables', 'fenced_code', 'toc']
)

# Create styled HTML
styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Trading Strategy Logic - 45.97% Return</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 32px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            font-size: 24px;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 20px;
        }}
        h4 {{
            color: #95a5a6;
            font-size: 16px;
        }}
        p {{
            margin: 12px 0;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            color: #e74c3c;
            font-size: 90%;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 20px;
            border-radius: 6px;
            border-left: 5px solid #3498db;
            overflow-x: auto;
            margin: 20px 0;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 10px 0;
        }}
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 40px 0;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
{html_content}
<hr>
<p style="text-align: center; color: #7f8c8d; font-size: 14px;">
Generated on November 3, 2025 | 
<a href="https://github.com/qingleiw/trading-strategy-contest">GitHub Repository</a>
</p>
</body>
</html>"""

# Save HTML version
with open('TRADING_LOGIC.html', 'w', encoding='utf-8') as f:
    f.write(styled_html)
print("✓ Generated TRADING_LOGIC.html")

# Try to generate PDF using available tools
pdf_generated = False

# Method 1: Try pdfkit (wkhtmltopdf)
try:
    import pdfkit
    pdfkit.from_string(styled_html, 'TRADING_LOGIC.pdf')
    print("✓ Generated TRADING_LOGIC.pdf using pdfkit")
    pdf_generated = True
except Exception as e:
    print(f"  pdfkit not available: {e}")

# Method 2: Try using Chrome headless via playwright
if not pdf_generated:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(styled_html)
            page.pdf(path='TRADING_LOGIC.pdf', format='A4')
            browser.close()
        print("✓ Generated TRADING_LOGIC.pdf using Playwright")
        pdf_generated = True
    except Exception as e:
        print(f"  Playwright not available: {e}")

# Method 3: Use Windows Print to PDF or browser
if not pdf_generated:
    print("\n📝 HTML file generated successfully!")
    print("\n💡 To generate PDF, you can:")
    print("   1. Open TRADING_LOGIC.html in your browser")
    print("   2. Press Ctrl+P (Print)")
    print("   3. Select 'Save as PDF' or 'Microsoft Print to PDF'")
    print("   4. Save as TRADING_LOGIC.pdf")
    print("\n   Or run: start TRADING_LOGIC.html")

print(f"\n📄 Files generated:")
print(f"   - TRADING_LOGIC.html ({len(styled_html)} bytes)")
if pdf_generated:
    import os
    if os.path.exists('TRADING_LOGIC.pdf'):
        size = os.path.getsize('TRADING_LOGIC.pdf')
        print(f"   - TRADING_LOGIC.pdf ({size} bytes)")
