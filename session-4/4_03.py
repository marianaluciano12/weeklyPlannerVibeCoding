# 3. Automate your browser to answer this survey: https://forms.gle/uXPeoEpXkdFEfRw49
""" 
    Make a program that:
        1. Opens the browser
        2. Navigates to the survey URL
        3. Answers the survey
"""

import time
from playwright.sync_api import sync_playwright

def automate_survey():
    # Survey data to fill in
    survey_name = "Carolina Santos"
    survey_email = "carolina@email.com"
    survey_address = "123 Automation St, Tech City"
    survey_phone = "555-0123"
    survey_comments = "This survey was filled out by an automated script using Playwright!"

    print("Starting browser automation...")
    
    with sync_playwright() as p:
        # 1. Opens the browser (headless=False so you can see it in action)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 2. Navigates to the survey URL
            print("Navigating to survey URL...")
            page.goto("https://forms.gle/uXPeoEpXkdFEfRw49")
            
            # Wait for the form to fully load by waiting for any button (like the Enviar button)
            page.wait_for_selector('div[role="button"]')
            print("Survey loaded successfully. Filling out answers...")
            
            # 3. Answers the survey
            
            # Google forms typically use aria-labelledby for their inputs, so we can target them by name
            page.get_by_role("textbox", name="Name").fill(survey_name)
            page.get_by_role("textbox", name="Email").fill(survey_email)
            
            # Address and Comments are also text boxes (textareas)
            page.get_by_role("textbox", name="Address").fill(survey_address)
            page.get_by_role("textbox", name="Phone number").fill(survey_phone)
            page.get_by_role("textbox", name="Comments").fill(survey_comments)
            
            # Small delay just so you can see the filled form before submission
            time.sleep(1.5)
            
            # Click the Submit button
            print("Submitting the survey...")
            
            # Use a robust locator that looks for a button containing "Enviar" or "Submit"
            import re
            page.locator('div[role="button"]').filter(has_text=re.compile("Enviar|Submit", re.IGNORECASE)).first.click()
            
            # Wait for the confirmation page to load (Google Forms redirects to /formResponse)
            page.wait_for_url("**/formResponse*")
            print("Survey submitted successfully!")
            
            # Give you a moment to see the success screen
            time.sleep(2)
            
        except Exception as e:
            print(f"An error occurred while filling the survey: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    automate_survey()
