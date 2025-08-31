from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import sys
import os

def setup_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def click_view_replies(driver):
    try:
        buttons = driver.find_elements(By.XPATH, '//yt-formatted-string[@id="more-replies"]')
        for b in buttons:
            try:
                driver.execute_script("arguments[0].click();", b)
                time.sleep(1)
            except:
                pass
    except:
        pass

def scroll_until_end(driver, delay=2, max_wait=5):
    last_count = 0
    same_count_times = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(delay)

        comments = driver.find_elements(By.CSS_SELECTOR, "#content #content-text")
        current_count = len(comments)

        sys.stdout.write(f"\r⏳ Komentar terload: {current_count}")
        sys.stdout.flush()

        click_view_replies(driver)

        if current_count == last_count:
            same_count_times += 1
        else:
            same_count_times = 0

        if same_count_times >= max_wait:
            print("\n✅ Semua komentar sudah ke-load.")
            break

        last_count = current_count

    return comments

def scrape_youtube_comments(url):
    driver = setup_driver()
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content #content-text"))
        )
    except:
        print("❌ Komentar tidak muncul, mungkin videonya disable komentar.")
        driver.quit()
        return []

    scroll_until_end(driver, delay=2)

    author_elements = driver.find_elements(By.CSS_SELECTOR, "#author-text span")
    comment_elements = driver.find_elements(By.CSS_SELECTOR, "#content #content-text")

    comments = []
    for idx, (a, c) in enumerate(zip(author_elements, comment_elements), start=1):
        username = a.text.strip()
        text = c.text.strip()
        if text:
            comments.append((username, text))
            sys.stdout.write(f"\r💾 Mengambil komentar {idx}/{len(comment_elements)}")
            sys.stdout.flush()

    print("\n✅ Semua komentar berhasil diambil.")
    driver.quit()
    return comments

def main():
    url = "https://www.youtube.com/watch?v=VL3Fv73y7Xw" #link youtube(bukan shorts)
    comments = scrape_youtube_comments(url)

    file_name = "youtube_comments.csv" #nama file csv
    file_exists = os.path.exists(file_name)

    with open(file_name, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["username", "comment"])  

        for username, text in comments:
            writer.writerow([username, text])

    print(f"[DONE] Berhasil tambah {len(comments)} komentar ke {file_name}")

if __name__ == "__main__":
    main()

