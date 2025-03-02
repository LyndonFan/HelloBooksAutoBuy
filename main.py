from get_emails import service, search_messages, read_message, cleanup_messages
from get_links import get_all_links
from buy_products import sign_in, buy_product

import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

CWD = Path(__file__).parent.resolve()

def run():
    results = search_messages(service, "from:readers@hellobooks.com")
    print(f"Found {len(results)} results.")
    if len(results) == 0:
        print("No results found.")
        return
    for msg in results:
        read_message(service, msg)

    links = get_all_links()

    if len(links) == 0:
        print("No links found.")
        return

    driver = webdriver.Chrome(service=Service())
    try:
        success = sign_in(driver)
        if success:
            print("Sign in success")
        else:
            print("Unable to sign in")
            driver.quit()
            exit()
    except Exception as e:
        print("Encountered exception:\n%s" % e)
        driver.quit()
        exit()

    print(driver.current_url)
    time.sleep(5)
    if not driver.current_url.split("?")[0] == "https://www.amazon.co.uk/":
        _ = input(
            "Human intervention needed, please resolve and press enter to continue"
        )
        print("Assume it's been resolved, waiting for 5 seconds before continuing")

    for link in links:
        print(link)
        try:
            success = buy_product(driver, link)
            print("Visited page", end=", ")
            if success:
                print("Bought product")
            else:
                print("Did not buy product")
        except Exception as e:
            print("Failed to buy product since an exception occurred")
            print(e)
        finally:
            time.sleep(2)
            print("=" * 50)
    print("Done!")
    driver.quit()
    try:
        cleanup_messages(service, results)
    except Exception as e:
        print("Error encountered while cleaning up")
        print(e)
    finally:
        for folder in CWD.glob("Hello_Books*"):
            for file in folder.iterdir():
                file.unlink()
            folder.rmdir()


if __name__ == "__main__":
    run()
