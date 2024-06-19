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
            # Close the context once the token is found
            context.close()

    if os.path.exists('.cache/login.json'):
        logging.info("Loading login headers and token from .cache/login.json")
        with open('.cache/login.json', 'r') as f:
            data = json.load(f)
            login_headers = data['headers']
            login_token = data['token']
    else:
        logging.info(f"Logging in: {HOME_PAGE_URL}")
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            context = browser.new_context()

            # Enable request interception to capture network traffic
            context.on("request", lambda request: handle_request(request))

            page = context.new_page()

            try:
                # Adjust navigation timeout and start navigation
                page.goto(HOME_PAGE_URL, wait_until='domcontentloaded', timeout=10000)
                # Wait for the token to be captured
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error during navigation: {e}")
            finally:
                # Ensure browser is closed even if an error occurs
                context.close()
                browser.close()

        # Save headers and token to .cache/login.json
        logging.info("Saving login headers and token to .cache/login.json")
        with open('.cache/login.json', 'w') as f:
            f.write(json.dumps({
                'headers': login_headers,
                'token': login_token
            }))

    # Return captured headers and token
    return login_headers, login_token
