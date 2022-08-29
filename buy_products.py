from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import re
import time
import os
import sys
import getpass

CWD = os.path.dirname(os.path.abspath(__file__))


def sign_in(driver):
    driver.get('https://www.amazon.co.uk/ap/signin?openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2Fref%3Dgw_sgn_ib%3F_encoding%3DUTF8%26pf_rd_p%3D644cc3df-edda-483a-b5b9-37ecf58fdf0e%26pd_rd_wg%3Do5prS%26pf_rd_r%3D05RBYQ8ZEMKJ2VNG4A0C%26content-id%3Damzn1.sym.644cc3df-edda-483a-b5b9-37ecf58fdf0e%26pd_rd_w%3DTx3RV%26pd_rd_r%3D5924fccb-3bf1-4684-9649-243f69a430d0&openid.assoc_handle=gbflex&openid.pape.max_auth_age=0&pf_rd_r=NN2BSD96XARTK2R8G5DK&pf_rd_p=644cc3df-edda-483a-b5b9-37ecf58fdf0e&pd_rd_r=8d8f9af0-0c11-4529-a2bf-e8beba1a6779&pd_rd_w=GxRqW&pd_rd_wg=Tpshg&ref_=pd_gw_unk')
    # time.sleep(1)
    # email_field = driver.find_element_by_xpath('//input[@id="ap_email"]')
    # email = input('Enter your email address: ')
    # email_field.send_keys(email)
    # continue_button = driver.find_element_by_xpath('//input[@id="continue"]')
    # continue_button.click()
    # time.sleep(1)
    # password_field = driver.find_element_by_xpath('//input[@id="ap_password"]')
    # password = getpass.getpass('Enter your password: ')
    # password_field.send_keys(password)
    # sign_in_button = driver.find_element_by_xpath(
    #     '//input[@id="signInSubmit"]')
    # sign_in_button.click()
    holder = input("Press enter after it's finished signing in")
    return True


def buy_product(driver, url):
    driver.get(url)
    time.sleep(1)
    title = driver.find_element_by_xpath('//span[@id="productTitle"]').text
    price = driver.find_element_by_xpath('//span[@id="kindle-price"]').text
    print(f'{title}: {price}')
    price = re.sub('[^0-9\.]', '', price)
    try:
        price = float(price)
    except ValueError as e:
        print(e)
        raise e
    if price > 0:
        print('Book is not free')
        return False
    button = driver.find_element_by_xpath('//input[@id="one-click-button"]')
    button.click()
    time.sleep(3)
    return True


if __name__ == '__main__':
    driver = webdriver.Chrome(os.path.join(CWD, 'chromedriver'))
    with open(os.path.join(CWD, 'links.txt'), 'r') as f:
        links = f.read().strip().split('\n')
    try:
        success = sign_in(driver)
        assert success
        print('Sign in success')
    except AssertionError as e:
        print("Unable to sign in")
        print(e)
        driver.quit()
        exit()
    except Exception as e:
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
