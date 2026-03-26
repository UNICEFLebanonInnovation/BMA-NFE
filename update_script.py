import re

with open('./student_registration/templates/mscc/child_services_tab.html', 'r') as f:
    content = f.read()

# We need to replace the whole Education section.
# We can find it by looking for <!-- Education --> and then the next service comment.
start_idx = content.find('<!-- Education -->')
end_idx = content.find('<!-- PSS Service -->')

education_content = content[start_idx:end_idx]

# Let's inspect the education content
with open('edu_content.html', 'w') as f:
    f.write(education_content)
