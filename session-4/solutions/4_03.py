# 3. Survey Automation
# 👉 Survey URL: https://forms.gle/uXPeoEpXkdFEfRw49

# 🔎  Automate your browser to:
#     1. Open the browser
#     2. Navigate to the survey URL
#     3. Answer and submit the survey

import re
import time
from playwright.sync_api import sync_playwright

def automate_survey():
    survey_name = "Carolina Santos"
    survey_email = "carolina@email.com"
    survey_address = "123 Automation St, Tech City"
    survey_phone = "555-0123"
    survey_comments = "This survey was filled out by an automated script using Playwright!"

    print("Starting browser automation...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Navigating to survey URL...")
            page.goto("https://forms.gle/uXPeoEpXkdFEfRw49")
            page.wait_for_selector('div[role="button"]')
            print("Survey loaded. Filling out answers...")

            page.get_by_role("textbox", name="Name").fill(survey_name)
            page.get_by_role("textbox", name="Email").fill(survey_email)
            page.get_by_role("textbox", name="Address").fill(survey_address)
            page.get_by_role("textbox", name="Phone number").fill(survey_phone)
            page.get_by_role("textbox", name="Comments").fill(survey_comments)

            time.sleep(1.5)

            print("Submitting the survey...")
            page.locator('div[role="button"]').filter(has_text=re.compile("Enviar|Submit", re.IGNORECASE)).first.click()
            page.wait_for_url("**/formResponse*")
            print("Survey submitted successfully!")

            time.sleep(2)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    automate_survey()
