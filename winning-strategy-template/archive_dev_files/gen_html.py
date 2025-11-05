import markdown

with open('TRADING_LOGIC.md', 'r', encoding='utf-8') as f:
    md = f.read()

html = markdown.markdown(md, extensions=['extra', 'tables', 'fenced_code', 'toc'])

styled = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Trading Logic</title>
<style>
body {{font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 20px;}}
h1 {{color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;}}
h2 {{color: #34495e; margin-top: 30px; border-bottom: 1px solid #bdc3c7;}}
h3 {{color: #7f8c8d; margin-top: 20px;}}
code {{background-color: #f4f4f4; padding: 3px 8px; border-radius: 4px; font-family: Consolas, monospace;}}
pre {{background-color: #f8f8f8; padding: 20px; border-radius: 6px; border-left: 5px solid #3498db; overflow-x: auto;}}
pre code {{background-color: transparent; padding: 0;}}
ul, ol {{margin: 15px 0; padding-left: 30px;}}
li {{margin: 10px 0;}}
</style></head><body>{html}</body></html>"""

with open('TRADING_LOGIC.html', 'w', encoding='utf-8') as f:
    f.write(styled)

print("HTML generated successfully")
