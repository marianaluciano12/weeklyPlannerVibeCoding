# 4. Web Scraping
# 👉 Jobs page: https://people.bamboohr.com/careers

# 🔎  Automate your browser to:
#     1. Open the browser
#     2. Navigate to the jobs page URL
#     3. Scrape and print the job listings

from playwright.sync_api import sync_playwright

def scrape_jobs():
    print("Starting browser to scrape jobs...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("Navigating to https://people.bamboohr.com/careers...")
            page.goto("https://people.bamboohr.com/careers")
            page.wait_for_selector('a[href*="/careers/"]')

            print("\n--- Current Openings ---\n")
            job_elements = page.locator('a[href*="/careers/"]').all()

            if not job_elements:
                print("No jobs found on the page.")
            else:
                for element in job_elements:
                    title = element.inner_text().strip()
                    if title:
                        href = element.get_attribute("href")
                        full_url = f"https://people.bamboohr.com{href}"
                        print(f"- {title}")
                        print(f"  Link: {full_url}\n")

            print("Scraping completed successfully!")

        except Exception as e:
            print(f"An error occurred while scraping: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_jobs()
