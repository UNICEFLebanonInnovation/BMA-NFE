from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a new context and start recording video
        context = browser.new_context(
            record_video_dir="/home/jules/verification/video",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Navigate to the login page
        page.goto("http://localhost:8000/accounts/login/")
        page.wait_for_timeout(500)

        # Login
        page.fill("input[name='login']", "admin")
        page.fill("input[name='password']", "admin")
        page.click("button[type='submit']")
        page.wait_for_timeout(2000)

        # Go straight to a child's profile
        child_id = 26
        page.goto(f"http://localhost:8000/mscc/child-profile/{child_id}/?current_tab=services")
        page.wait_for_timeout(3000)

        page.add_style_tag(content="#djDebug { display: none !important; }")

        # Click the education tab
        try:
            page.click("button#edu-tab", timeout=3000)
            page.wait_for_timeout(2000)
        except Exception as e:
            print("Could not click Services tab via button#edu-tab", e)

        # Wait to ensure tab content is visible
        page.wait_for_timeout(1000)

        # Let's take a screenshot
        page.screenshot(path="/home/jules/verification/verification_services.png", full_page=True)

        context.close()
        browser.close()

if __name__ == "__main__":
    verify_feature()
