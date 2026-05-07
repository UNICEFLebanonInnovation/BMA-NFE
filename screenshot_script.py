from playwright.sync_api import sync_playwright

def run_cuj(page):
    # Go to login page
    page.goto("http://localhost:3000/accounts/login/")
    page.wait_for_timeout(1000)

    # Login
    page.fill("input[name='login']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_timeout(2000)

    # Take screenshot of students list
    page.goto("http://localhost:3000/students/")
    page.wait_for_timeout(2000)
    page.screenshot(path="docs/screenshots/06_students.png")

    # Take screenshot of attendances
    page.goto("http://localhost:3000/attendances/")
    page.wait_for_timeout(2000)
    page.screenshot(path="docs/screenshots/07_attendances.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            run_cuj(page)
        finally:
            browser.close()
