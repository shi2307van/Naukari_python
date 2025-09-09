from fastapi import FastAPI
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

app = FastAPI()

@app.get("/scrape/")
def scrape_data(keyword: str):
    try:
        # Initialize Naukri jobs list
        naukri_jobs = []

        options = uc.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment for headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

        # Explicitly specify ChromeDriver version 138 to match Chrome browser version
        driver = uc.Chrome(options=options, version_main=138)

        # --- Naukri Scraping ---
        naukri_url = f"https://www.naukri.com/{keyword.replace(' ', '-').lower()}-jobs?k={keyword.replace(' ', '%20')}"
        try:
            print("Navigating to Naukri...")
            driver.get(naukri_url)
            print("Navigated to Naukri.")
        except Exception as e:
            print("Error navigating to Naukri:", e)
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for job in soup.select('.srp-jobtuple-wrapper, .jobTuple.bgWhite.br4.mb-8'):
            title_tag = job.select_one('a.title, a.title.fw500.ellipsis')
            company_tag = job.select_one('a.comp-name, a.compName')
            location_tag = job.select_one('span.locWdth, span.fleft.grey-text.br2.placeHolderLi.location')
            exp_tag = job.select_one('span.expwdth, li.experience')
            apply_link = title_tag['href'] if title_tag and title_tag.has_attr('href') else ''
            naukri_jobs.append({
                'jobTitle': title_tag.text.strip() if title_tag else '',
                'company': company_tag.text.strip() if company_tag else '',
                'location': location_tag.text.strip() if location_tag else '',
                'experience': exp_tag.text.strip() if exp_tag else '',
                'applyLink': apply_link,
                'platform': 'Naukri'
            })

        print(f"Naukri jobs found: {len(naukri_jobs)}")
        driver.quit()
        
        return naukri_jobs
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
