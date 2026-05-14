# 4. Automate your browser to scrape this jobs page: https://people.bamboohr.com/careers
""" 
    Make a program that:
        1. Opens the browser
        2. Navigates to the jobs page URL
        3. Scrapes the jobs page
"""

from playwright.sync_api import sync_playwright

def scrape_jobs():
    print("Starting browser to scrape jobs...")
    
    with sync_playwright() as p:
        # 1. Opens the browser (using headless mode for scraping since we don't need to see it)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 2. Navigates to the jobs page URL
            print("Navigating to https://people.bamboohr.com/careers...")
            page.goto("https://people.bamboohr.com/careers")
            
            # Wait for the jobs container to load. BambooHR uses javascript to load them.
            # We look for links containing "/careers/" which is how the jobs are formatted.
            print("Waiting for jobs to load...")
            page.wait_for_selector('a[href*="/careers/"]')
            
            # 3. Scrapes the jobs page
            print("\n--- Current Openings ---\n")
            
            # Grab all the job link elements
            job_elements = page.locator('a[href*="/careers/"]').all()
            
            if not job_elements:
                print("No jobs found on the page.")
            else:
                for element in job_elements:
                    title = element.inner_text().strip()
                    
                    # Ignore empty links or hidden elements
                    if title:
                        href = element.get_attribute("href")
                        # The links are usually relative, so we construct the full URL
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
