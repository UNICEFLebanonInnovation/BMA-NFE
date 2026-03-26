import re

with open('edu_content_replaced.html', 'r') as f:
    text = f.read()

# Replace the card wrapper and header
old_header = r'''    <div class="col-md-12 col-lg-6 col-xl-4">

                                <div class="mb-3 card">
                                    <!--<div class="card-header-tab card-header">-->
                                        <!--<div class="card-header-title font-size-lg text-capitalize font-weight-normal">-->
                                            <!--<i class="header-icon lnr-cloud-download icon-gradient bg-happy-itmeo"> </i>-->
                                            <!--Details-->
                                        <!--</div>-->
                                    <!--</div>-->
                                    <div class="p-0 card-body">
                                        <div class="dropdown-menu-header mt-0 mb-0">
                                            <div class="dropdown-menu-header-inner bg-heavy-rain">
                                                <div class="menu-header-image opacity-1"></div>
                                                <div class="menu-header-content text-dark">
                                                  {% if result and es_result.education_program  in 'YFS Level 1 - RS Grade 9, YFS Level 2 - RS Grade 9' %}
                                                    <h5 class="menu-header-title">RS Grade 9 - Grading</h5>
                                                  {% else %}
                                                      <h5 class="menu-header-title">{{ result1.education_program }} - Grading</h5>
                                                  {% endif %}
                                                    <!--<h6 class="menu-header-subtitle">-->
                                                        <!--You have-->
                                                        <!--<b class="text-info">21 </b>-->
                                                        <!--unread messages-->
                                                    <!--</h6>-->
                                                </div>
                                            </div>
                                        </div>'''

new_header = r'''    <div class="col-md-12 col-xl-8">
        <div class="card border h-100 shadow-none">
            <div class="card-header bg-light py-3 border-bottom d-flex justify-content-between align-items-center">
                <h6 class="mb-0 fw-bold text-primary">
                    {% if result and es_result.education_program in 'YFS Level 1 - RS Grade 9, YFS Level 2 - RS Grade 9' %}
                        {% trans "RS Grade 9 - Grading" %}
                    {% else %}
                        {{ result1.education_program }} - {% trans "Grading" %}
                    {% endif %}
                </h6>
            </div>
            <div class="card-body p-0">'''

text = text.replace(old_header, new_header)

# Replace tabs
old_tabs = r'''                                        <ul class="tabs-animated-shadow tabs-animated nav nav-justified tabs-shadow-bordered p-3">
                                            <li class="nav-item">
                                                <a role="tab" class="nav-link mb-2 mr-2 active show" id="tab-c-11" data-toggle="tab" href="#tab-animated-11" aria-selected="true">
                                                  <span>Pre Grading</span>
                                                </a>
                                            </li>
                                          {% if result1.education_program in 'RS Grade 1, RS Grade 2, RS Grade 3, RS Grade 4, RS Grade 5, RS Grade 6, RS Grade 7, RS Grade 8, RS Grade 9' and instance.type == 'Walk-in' %}
                                          {% else %}
                                            <li class="nav-item">
                                                <a role="tab" class="nav-link" id="tab-c-12" data-toggle="tab" href="#tab-animated-12">
                                                    <span>Post Grading </span>
                                                </a>
                                            </li>
                                            <li class="nav-item">
                                                <a role="tab" class="nav-link" id="tab-c-15" data-toggle="tab" href="#tab-animated-15">
                                                    <span>Improvement</span>
                                                </a>
                                            </li>

                                            {% endif %}
                                          {% if result1.education_program in 'RS Grade 7, RS Grade 8, RS Grade 9, YFS Level 1 - RS Grade 9, YFS Level 2 - RS Grade 9' %}
                                            <li class="nav-item">
                                                <a role="tab" class="nav-link" id="tab-c-16" data-toggle="tab" href="#tab-animated-16">
                                                    <span>School Grading</span>
                                                </a>
                                            </li>
                                            {% endif %}

                                          {% if result1.education_program in 'RS Grade 1, RS Grade 2, RS Grade 3, RS Grade 4, RS Grade 5, RS Grade 6' %}
                                            <li class="nav-item">
                                                <a role="tab" class="nav-link" id="tab-c-17" data-toggle="tab" href="#tab-animated-17">
                                                    <span>School Grading</span>
                                                </a>
                                            </li>
                                            {% endif %}
                                        </ul>'''

new_tabs = r'''                <ul class="nav nav-tabs nav-fill border-bottom-0 bg-light" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active rounded-0 border-top-0 border-start-0 border-end-0 fw-bold" id="tab-c-11" data-bs-toggle="tab" data-bs-target="#tab-animated-11" type="button" role="tab" aria-selected="true">
                            {% trans "Pre Grading" %}
                        </button>
                    </li>
                    {% if not (result1.education_program in 'RS Grade 1, RS Grade 2, RS Grade 3, RS Grade 4, RS Grade 5, RS Grade 6, RS Grade 7, RS Grade 8, RS Grade 9' and instance.type == 'Walk-in') %}
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-0 border-top-0 border-start-0 border-end-0 fw-bold text-muted" id="tab-c-12" data-bs-toggle="tab" data-bs-target="#tab-animated-12" type="button" role="tab" aria-selected="false">
                            {% trans "Post Grading" %}
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-0 border-top-0 border-start-0 border-end-0 fw-bold text-muted" id="tab-c-15" data-bs-toggle="tab" data-bs-target="#tab-animated-15" type="button" role="tab" aria-selected="false">
                            {% trans "Improvement" %}
                        </button>
                    </li>
                    {% endif %}
                    {% if result1.education_program in 'RS Grade 7, RS Grade 8, RS Grade 9, YFS Level 1 - RS Grade 9, YFS Level 2 - RS Grade 9' %}
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-0 border-top-0 border-start-0 border-end-0 fw-bold text-muted" id="tab-c-16" data-bs-toggle="tab" data-bs-target="#tab-animated-16" type="button" role="tab" aria-selected="false">
                            {% trans "School Grading" %}
                        </button>
                    </li>
                    {% endif %}
                    {% if result1.education_program in 'RS Grade 1, RS Grade 2, RS Grade 3, RS Grade 4, RS Grade 5, RS Grade 6' %}
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-0 border-top-0 border-start-0 border-end-0 fw-bold text-muted" id="tab-c-17" data-bs-toggle="tab" data-bs-target="#tab-animated-17" type="button" role="tab" aria-selected="false">
                            {% trans "School Grading" %}
                        </button>
                    </li>
                    {% endif %}
                </ul>'''

text = text.replace(old_tabs, new_tabs)


# Replace edit buttons inside tabs
def replace_edit_buttons(text):
    text = re.sub(
        r'<div style="float:right;margin-top: 5px;margin-right: 12px;font-size: 25px;">(.*?)</div>',
        r'<div class="d-flex justify-content-end p-2 border-bottom bg-light">\1</div>',
        text,
        flags=re.DOTALL
    )
    # Style the links inside
    text = re.sub(
        r'<a href="(.*?)" data-toggle="tooltip"(.*?)>Edit</a>',
        r'<a href="\1" class="btn btn-sm btn-outline-primary" data-bs-toggle="tooltip"\2><i class="bi bi-pencil me-1"></i> {% trans "Edit" %}</a>',
        text
    )
    text = re.sub(
        r'<a href="(.*?)" data-toggle="tooltip"(.*?)>Add</a>',
        r'<a href="\1" class="btn btn-sm btn-primary" data-bs-toggle="tooltip"\2><i class="bi bi-plus me-1"></i> {% trans "Add" %}</a>',
        text
    )
    return text

text = replace_edit_buttons(text)

# Remove the custom scroll containers (scroll-area-sm, ps__*, scrollbar-container)
text = re.sub(r'<div class="scroll-area-sm"[^>]*>', '<div class="overflow-auto" style="max-height: 250px;">', text)
text = re.sub(r'<div class="scrollbar-container ps ps--active-y">', '', text)
text = re.sub(r'<div class="ps__rail-x".*?</div></div>', '', text)

# Convert <div class="p-3"> to <div class="p-0"> for list group alignment
text = text.replace('<div class="p-3">', '<div class="p-0">')
text = text.replace('<div class="tab-pane active show"', '<div class="tab-pane fade show active"')
text = text.replace('<div class="tab-pane"', '<div class="tab-pane fade"')

# And close ul instead of closing div where necessary (since we substituted vertical-time-icons div to ul)
# This will be simpler to handle by regex
text = re.sub(r'</p>\s*</div>\s*</div>\s*</div>', r'</p></div></div></div>', text) # Remove whitespace issues before

# Actually I have already replaced the list items! So the closing </div> of vertical-time-icons needs to be </ul>
text = re.sub(r'<ul class="list-group list-group-flush mb-0">\s*<li(.*?)</li>\s*</div>', r'<ul class="list-group list-group-flush mb-0">\n<li\1</li>\n</ul>', text, flags=re.DOTALL)

# But wait, we replaced `<div class="vertical-time-icons...` with `<ul class="list-group...`
# That means there is a trailing `</div>` that belongs to `vertical-time-icons`. Let's just fix the whole html.
text = text.replace('</ul>\n                                                        </div>', '</ul>')
text = text.replace('</div>\n                                                        </div>\n                                                    <div class="ps__rail-x"', '</ul>\n                                                    </div>\n                                                    <div class="ps__rail-x"')
text = text.replace('</div>\n                                                        </div>\n                                                        </div>', '</ul>\n                                                        </div>')

text = re.sub(r'<ul class="nav flex-column">.*?</ul>', '', text, flags=re.DOTALL)

with open('edu_content_new.html', 'w') as f:
    f.write(text)
