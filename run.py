from get_emails import service, search_messages, read_message, cleanup_message
from get_links import get_all_links
from buy_products import sign_in, buy_product

import os
from selenium import webdriver
import time

CWD = os.path.dirname(os.path.abspath(__file__))


def run():
    results = search_messages(service, "from:readers@hellobooks.com")
    print(f"Found {len(results)} results.")
    for msg in results:
        read_message(service, msg)

    links = get_all_links()

    driver = webdriver.Chrome(os.path.join(CWD, 'chromedriver'))
    try:
        success = sign_in(driver)
        assert success
        print('Sign in success')
    except Exception as e:
        if isinstance(e, AssertionError):
            print("Unable to sign in")
        else:
            print("Encountered exception:\n%s" % e)
        driver.quit()
        exit()

    for l in links:
        print(l)
        try:
            success = buy_product(driver, l)
            print('Visited page', end=', ')
            if success:
                print('Bought product')
            else:
                print('Did not buy product')
        except Exception as e:
            print('Failed to buy product since an exception occurred')
            print(e)
        finally:
            time.sleep(2)
            print('='*50)
    print("Done!")
    driver.quit()

    for msg in results:
        cleanup_message(service, msg)

    os.system('rm -rf Hello_Books*')


if __name__ == '__main__':
    run()
