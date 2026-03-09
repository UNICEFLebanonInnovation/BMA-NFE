from playwright.sync_api import sync_playwright
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        css_path = 'student_registration/static/css/redesign.css'
        if not os.path.exists(css_path):
            print(f"CSS file not found: {css_path}")
            return

        with open(css_path, 'r') as f:
            css_content = f.read()

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <style>{css_content}</style>
        </head>
        <body>
            <div class="app-wrapper">
                <nav class="sidebar">
                    <div class="p-4 text-center">
                        <div style="height: 40px; background: #eee; display: flex; align-items: center; justify-content: center;">LOGO</div>
                    </div>
                    <div class="nav flex-column">
                        <a href="#" class="nav-link active"><i class="bi bi-house"></i> <span>Dashboard</span></a>
                        <a href="#" class="nav-link"><i class="bi bi-person-plus"></i> <span>Registration</span></a>
                    </div>
                </nav>
                <main class="main-content">
                    <header class="topbar">
                        <button class="btn me-3"><i class="bi bi-list fs-4"></i></button>
                        <h5 class="mb-0 me-auto">Dashboard Redesign</h5>
                        <div class="d-flex align-items-center">
                            <div class="me-3"><i class="bi bi-bell"></i></div>
                            <div>John Doe</div>
                        </div>
                    </header>
                    <div class="p-4">
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="card metric-card">
                                    <div class="metric-label">Beneficiaries</div>
                                    <div class="metric-value">1,234</div>
                                </div>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <span>Recent Enrollments</span>
                                <button class="btn btn-primary btn-sm">Add New</button>
                            </div>
                            <div class="table-responsive" style="max-height: 400px;">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Name</th>
                                            <th>Program</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {"".join([f"<tr><td>#00{i}</td><td>Student Name {i}</td><td>NFE Core</td><td><span class='badge bg-success'>Active</span></td></tr>" for i in range(1, 15)])}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </body>
        </html>
        """

        page = browser.new_page()
        page.set_content(html_content)
        page.set_viewport_size({"width": 1280, "height": 800})
        page.screenshot(path="./verification/redesign_dashboard.png")
        print("Dashboard screenshot saved.")

        browser.close()

if __name__ == "__main__":
    run_verification()
