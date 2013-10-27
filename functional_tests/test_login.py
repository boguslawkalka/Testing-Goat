import time
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.auth import get_user_model
User = get_user_model()

from .base import FunctionalTest

TEST_EMAIL = 'testinggoat@yahoo.com'
TEST_PASSWORD = 'soFNjTMqMLEtj8W4'

class LoginTest(FunctionalTest):

    def switch_to_new_window(self, text_in_title):
        retries = 50
        while retries > 0:
            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
                if text_in_title in self.browser.title:
                    return
            retries -= 1
            time.sleep(0.2)
        self.fail('could not find window')


    def wait_for_element_with_id(self, element_id):
        WebDriverWait(self.browser, timeout=20).until(
            lambda b: b.find_element_by_id(element_id)
        )


    def test_login_with_persona(self):
        # Edith goes to the awesome superlists site
        # and notices a "Sign in" link for the first time.
        self.browser.get(self.server_url)
        self.browser.find_element_by_id('id_login').click()

        # A Persona login box appears
        self.switch_to_new_window('Mozilla Persona')
        self.browser.find_element_by_id(
            'authentication_email'
        ).send_keys(TEST_EMAIL)
        self.browser.find_element_by_tag_name('button').click()

        # We get redirected to the Yahoo page
        self.wait_for_element_with_id('username')
        self.browser.find_element_by_id(
            'username'
        ).send_keys(TEST_EMAIL)
        self.browser.find_element_by_id(
            'passwd'
        ).send_keys(TEST_PASSWORD)
        self.browser.find_element_by_id('.save').click()

        # The Persona window closes
        self.switch_to_new_window('To-Do')

        # She can see that she is logged in
        self.wait_for_element_with_id('id_logout')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)
        self.fail(self.browser.get_cookies())


from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.conf import settings


class PreLoginTest(FunctionalTest):

    def setUp(self):
        super().setUp()
        user = User.objects.create(email='edith@email.com')
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        self.browser.get(self.server_url) # needed to be able to set cookie for domain
        #print(self.browser.get_cookies())
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))
        print(self.browser.get_cookies())


    def test_should_be_logged_in(self):
        self.browser.get(self.server_url)
        self.browser.find_element_by_id('id_logout')

