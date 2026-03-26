import re

with open('edu_content.html', 'r') as f:
    text = f.read()

# Replace the outer timeline container
text = re.sub(
    r'<div class="vertical-time-icons vertical-timeline vertical-timeline--animate vertical-timeline--one-column">',
    r'<ul class="list-group list-group-flush mb-0">',
    text
)
# And the closing div
# This might be tricky, let's just replace the items first.

item_pattern = r'<div class="vertical-timeline-item vertical-timeline-element">\s*<div><span class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-info"><i class="pe-7s-info text-info"></i></div></span>\s*<div class="vertical-timeline-element-content bounce-in"><h4 class="timeline-title">(.*?)</h4>\s*<p>(.*?)</p>\s*</div>\s*</div>\s*</div>'

def replace_item(match):
    title = match.group(1).strip()
    value = match.group(2).strip()
    return f'''<li class="list-group-item d-flex justify-content-between align-items-center px-3 py-2 border-0 border-bottom">
    <span class="text-muted fw-bold small">{title}</span>
    <span class="badge bg-info-subtle text-info fw-bold">{value}</span>
</li>'''

text = re.sub(item_pattern, replace_item, text, flags=re.DOTALL)

with open('edu_content_replaced.html', 'w') as f:
    f.write(text)
