"""Page object for the Mercury Web Tours application (frameset based)."""
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import config


class WebTours:
    """Drives the frameset: body > (navbar | info)."""

    def __init__(self, driver, base_url=config.BASE_URL, timeout=config.TIMEOUT):
        self.driver = driver
        self.base_url = base_url
        self.timeout = timeout

    # ------------------------------------------------------------------ frames
    def _goto(self, *names):
        self.driver.switch_to.default_content()
        for name in names:
            WebDriverWait(self.driver, self.timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, name))
            )
        return self

    def navbar(self):
        return self._goto("body", "navbar")

    def info(self):
        return self._goto("body", "info")

    def _info_text(self):
        self.info()
        return self.driver.find_element(By.TAG_NAME, "body").text

    # ------------------------------------------------------------------- open
    def open(self):
        self.driver.get(self.base_url)
        self._goto("body")
        return self

    # -------------------------------------------------------------- navigation
    def goto(self, alt):
        self.navbar()
        self.driver.find_element(By.XPATH, f"//img[@alt='{alt}']").click()
        self._goto("body", "info")
        return self

    def goto_search(self):
        return self.goto("Search Flights Button")

    def goto_itinerary(self):
        return self.goto("Itinerary Button")

    def goto_home(self):
        return self.goto("Home Button")

    def sign_off(self):
        self.goto("SignOff Button")
        self.navbar()
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        return self

    # ------------------------------------------------------------------- auth
    def login(self, username, password):
        self.navbar()
        user = self.driver.find_element(By.NAME, "username")
        user.clear()
        user.send_keys(username)
        pwd = self.driver.find_element(By.NAME, "password")
        pwd.clear()
        pwd.send_keys(password)
        self.driver.find_element(By.NAME, "login").click()
        return self

    def wait_for_info(self, text, timeout=None):
        wanted = text.lower()

        def condition(driver):
            try:
                self._goto("body", "info")
                return wanted in driver.find_element(By.TAG_NAME, "body").text.lower()
            except (NoSuchElementException, TimeoutException):
                return False

        WebDriverWait(self.driver, timeout or self.timeout).until(condition)
        return self

    def is_logged_in(self, username=None):
        try:
            text = self._info_text().lower()
        except Exception:
            return False
        if "welcome," not in text:
            return False
        return username is None or username.lower() in text

    def error_message(self):
        try:
            return self._info_text()
        except Exception:
            return ""

    # ------------------------------------------------------------- registration
    def open_registration(self):
        self.driver.get(f"{config.CGI_URL}/login.pl?getInfo=true")
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        return self

    def submit_registration(self, username, password, confirm=None,
                            first_name="Web", last_name="Tours",
                            address1="1 Rue de la Paix", address2="Tunis"):
        self.open_registration()
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "passwordConfirm").send_keys(confirm or password)
        self.driver.find_element(By.NAME, "firstName").send_keys(first_name)
        self.driver.find_element(By.NAME, "lastName").send_keys(last_name)
        self.driver.find_element(By.NAME, "address1").send_keys(address1)
        self.driver.find_element(By.NAME, "address2").send_keys(address2)
        before = set(self.driver.window_handles)
        self.driver.find_element(By.NAME, "register").click()
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: len(d.window_handles) > len(before)
            or (d.find_element(By.TAG_NAME, "body").text or "").strip() != ""
        )
        new_windows = [h for h in self.driver.window_handles if h not in before]
        if new_windows:
            # the form targets the "info" frame: outside a frameset the browser
            # opens the answer in a new window
            self.driver.switch_to.window(new_windows[-1])
        return self

    def registration_text(self):
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return self.driver.find_element(By.TAG_NAME, "body").text

    # ----------------------------------------------------------------- search
    def fill_search(self, depart=None, arrive=None, depart_date=None,
                    return_date=None, passengers=None, seat_pref=None,
                    seat_type=None, roundtrip=None):
        self.goto_search()
        self.info()
        if depart is not None:
            Select(self.driver.find_element(By.NAME, "depart")).select_by_visible_text(depart)
        if arrive is not None:
            Select(self.driver.find_element(By.NAME, "arrive")).select_by_visible_text(arrive)
        if depart_date is not None:
            field = self.driver.find_element(By.NAME, "departDate")
            field.clear()
            field.send_keys(depart_date)
        if return_date is not None:
            field = self.driver.find_element(By.NAME, "returnDate")
            field.clear()
            field.send_keys(return_date)
        if passengers is not None:
            field = self.driver.find_element(By.NAME, "numPassengers")
            field.clear()
            field.send_keys(str(passengers))
        if roundtrip is not None:
            box = self.driver.find_element(By.NAME, "roundtrip")
            if box.is_selected() != roundtrip:
                box.click()
        if seat_pref:
            self.driver.find_element(
                By.CSS_SELECTOR, f"input[name='seatPref'][value='{seat_pref}']").click()
        if seat_type:
            self.driver.find_element(
                By.CSS_SELECTOR, f"input[name='seatType'][value='{seat_type}']").click()
        return self

    def search(self, **kwargs):
        self.fill_search(**kwargs)
        self.info()
        self.driver.find_element(By.NAME, "findFlights").click()
        return self

    def search_results(self):
        """Returns {'outbound': [...], 'return': [...]} of (flight, price, date)."""
        self.info()
        result = {"outbound": [], "return": []}
        for key, field in (("outbound", "outboundFlight"), ("return", "returnFlight")):
            for radio in self.driver.find_elements(By.NAME, field):
                flight, price, date = radio.get_attribute("value").split(";")
                result[key].append((flight, float(price), date))
        return result

    def page_text(self):
        return self._info_text()

    # ----------------------------------------------------------------- booking
    def select_flight(self, outbound=0, inbound=None):
        self.info()
        radios = self.driver.find_elements(By.NAME, "outboundFlight")
        radios[outbound].click()
        chosen = radios[outbound].get_attribute("value").split(";")
        if inbound is not None:
            returns = self.driver.find_elements(By.NAME, "returnFlight")
            returns[inbound].click()
        self.driver.find_element(By.NAME, "reserveFlights").click()
        return chosen

    def payment_form(self):
        self.info()
        return {
            "total_text": self.driver.find_element(By.TAG_NAME, "body").text,
            "passengers": [e.get_attribute("name") for e in
                           self.driver.find_elements(By.XPATH, "//input[starts-with(@name,'pass')]")],
            "first_name": self.driver.find_element(By.NAME, "firstName").get_attribute("value"),
            "last_name": self.driver.find_element(By.NAME, "lastName").get_attribute("value"),
        }

    def pay(self, card=config.VALID_CARD, exp=config.VALID_EXP,
            first_name=None, last_name=None, address1=None, address2=None,
            passenger_names=None, save_card=False, clear_card=False):
        self.info()
        data = {
            "firstName": first_name, "lastName": last_name,
            "address1": address1, "address2": address2,
        }
        for name, value in data.items():
            if value is not None:
                field = self.driver.find_element(By.NAME, name)
                field.clear()
                field.send_keys(value)
        if passenger_names:
            for index, value in enumerate(passenger_names, start=1):
                field = self.driver.find_element(By.NAME, f"pass{index}")
                field.clear()
                field.send_keys(value)
        card_field = self.driver.find_element(By.NAME, "creditCard")
        card_field.clear()
        if card:
            card_field.send_keys(card)
        exp_field = self.driver.find_element(By.NAME, "expDate")
        exp_field.clear()
        if exp:
            exp_field.send_keys(exp)
        box = self.driver.find_element(By.NAME, "saveCC")
        if box.is_selected() != save_card:
            box.click()
        self.driver.find_element(By.NAME, "buyFlights").click()
        return self

    def book(self, outbound=0, inbound=None, card=config.VALID_CARD,
             exp=config.VALID_EXP, passengers=None, **search_kwargs):
        self.search(**search_kwargs)
        chosen = self.select_flight(outbound=outbound, inbound=inbound)
        self.pay(card=card, exp=exp, passenger_names=passengers)
        return chosen

    # --------------------------------------------------------------- itinerary
    def itinerary_text(self):
        self.goto_itinerary()
        return self._info_text()

    def itinerary_rows(self):
        self.info()
        return self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")

    def cancel_first_reservation(self):
        self.info()
        self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")[0].click()
        self.driver.find_element(By.NAME, "removeFlights").click()
        return self

    def cancel_all_reservations(self):
        self.info()
        self.driver.find_element(By.NAME, "removeAllFlights").click()
        return self
