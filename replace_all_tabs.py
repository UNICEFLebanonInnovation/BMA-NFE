import re

with open('./student_registration/templates/mscc/child_services_tab.html', 'r') as f:
    content = f.read()

# We need to replace the whole Education section.
# We can find it by looking for <!-- Education --> and then the next service comment.
start_idx = content.find('<!-- Education -->')
end_idx = content.find('<!-- PSS Service -->')

with open('edu_content_new.html', 'r') as f:
    new_edu = f.read()

new_content = content[:start_idx] + new_edu + '\n    ' + content[end_idx:]

with open('./student_registration/templates/mscc/child_services_tab.html', 'w') as f:
    f.write(new_content)
