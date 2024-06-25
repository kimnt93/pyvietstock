import json
import logging
import os
import time
from playwright.sync_api import sync_playwright

from pyvietstock.config import HOME_PAGE_URL


def login(username=None, password=None):
    login_headers = None
    login_token = None

    def handle_request(request):
        nonlocal login_headers, login_token
        if "data/GetTemplateByName" in request.url:
            logging.info("Finding token...")
            login_headers = request.headers
            login_token = request.post_data.split("__RequestVerificationToken=")[1]
            # Save headers and token to .cache/login.json
            logging.info("Saving login headers and token to .cache/login.json")
            with open('.cache/login.json', 'w') as f:
                f.write(json.dumps({
                    'headers': login_headers,
                    'token': login_token
                }))

    if os.path.exists('.cache/login.json'):
        logging.info("Loading login headers and token from .cache/login.json")
        with open('.cache/login.json', 'r') as f:
            data = json.load(f)
            login_headers = data['headers']
            login_token = data['token']
    else:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()

            try:
                # Adjust navigation timeout and start navigation
                logging.info(f"Logging in: {HOME_PAGE_URL}")
                page.goto(HOME_PAGE_URL)

                # Click the "Đăng nhập" button to show the login form
                page.click('button#btn-request-call-login')
                time.sleep(1)
                # Fill in the email and password fields
                page.fill('input#txtEmailLogin', username)
                page.fill('input#txtPassword', password)

                # Click the login button
                page.click('button#btnLoginAccount')

                # Wait for the token to be captured
                time.sleep(2)
                # Enable request interception to capture network traffic
                page.on("request", lambda request: handle_request(request))
                page.goto(HOME_PAGE_URL)
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error during navigation: {e}")
            finally:
                # Ensure context and browser are closed even if an error occurs
                browser.close()

    # Return captured headers and token
    return login_headers, login_token

# Example usage:
# login_headers, login_token = login("your-email@example.com", "your-password")
# print(login_headers, login_token)
