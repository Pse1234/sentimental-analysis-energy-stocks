import os
import csv
import random
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from time import sleep
import urllib.parse


class TwitterScrapper:
    """
    LAST MODIFIED:
        2023-01-26
    AUTHORS GITHUB:
        @Pse1234, @sarrabenyahia

    A simple twitter webscrapper based on selenium
    It enables you to get data from what you are interesed of, for example: "TOTALENERGIES"

    Parameters:
    -----------
    research: str, default []
        words that you want to looking for in twitter

    link: str, default "www.twitter.com"
        Webpage link for webscrapping, in our case twitter.
        We let this parameter on in case twitter decide to change it or you want a specific language, for example: "www.twitter.com/"

    output_path: str, default "./../"
        If you have the same architecture than us, you can change it to ./../data/ but creating a specific folder

    start_date: str, default 2017-10-31
        date with format yyyy-mm-dd

    end_date: str, default 2022-09-30
        date with format yyyy-mm-dd

    mail: str, default None
        mail of the user in case you want access into twitter

    username: str, default None
        username of the user in case you want to access into twitter, as we are in private navigation, a suspicious alert may be activated

    password: str, default None
        password of the user in case you want to access into twitter

    verbose: boolean default False
        printing information about each step of the algorithm

    Note:
    -----
    Keep in mind that accessing to an account allows you to get extra data. The algorithm is constructed to avoid all the bot detections systems of twitter. We have test it for a thousand of times.
    If some of the xpath don't match anymore because twitter have changed their webpage,
    you can adapt them: inspect the element of the webpage and copy the xpath.
    Sometimes, you will have an error, you have to re-run the algorithm for great work.
    """

    def __init__(
        self,
        research: str = "Elon musk",
        link: str = "https://twitter.com/",
        output_path: str = "./../data/",
        start_date=None,
        end_date=None,
        mail=None,
        username=None,
        password=None,
        verbose: bool = False,
    ):
        self.research = research
        self.link = link
        self.output_path = output_path
        self.list_seconds = [3, 4, 5, 6, 7, 8, 9, 10]
        self.mail = mail
        self.username = username
        self.password = password
        self.verbose = verbose
        self.start_date = start_date
        self.end_date = end_date

    def _get_tweet_data(self, card):
        """Extract data from tweet card"""
        try:
            handle = card.find_element("xpath", './/span[contains(text(), "@")]').text
        except NoSuchElementException:
            return
        try:
            username = card.find_element("xpath", ".//span").text
        except NoSuchElementException:
            return
        try:
            postdate = card.find_element("xpath", ".//time").get_attribute("datetime")
        except NoSuchElementException:
            return
        try:
            comment = card.find_element("xpath", ".//div[2]/div[2]/div[1]").text
        except NoSuchElementException:
            return
        try:
            responding = card.find_element("xpath", ".//div[2]/div[2]/div[2]").text
        except NoSuchElementException:
            return
        try:
            text = comment + responding
        except NoSuchElementException:
            return
        try:
            reply_cnt = card.find_element("xpath", './/div[@data-testid="reply"]').text
        except NoSuchElementException:
            return
        try:
            retweet_cnt = card.find_element(
                "xpath", './/div[@data-testid="retweet"]'
            ).text
            # retweet_cnt = card.find_element('xpath','.//div[@data-testid="retweet"]').text
        except NoSuchElementException:
            return
        try:
            like_cnt = card.find_element("xpath", './/div[@data-testid="like"]').text
            # like_cnt = card.find_element('xpath','.//div[@data-testid="like"]').text
        except NoSuchElementException:
            return
        tweet = (username, handle, postdate, text, reply_cnt, retweet_cnt, like_cnt)
        return tweet

    def _open_set_up_chrome(self):
        """Opens and sets up chrome in incognito mode (private navigation), maximazing the windows for avoiding changes in xpath which are relative to the size of the windows due to proportionality CSS methods."""
        options = webdriver.ChromeOptions().add_argument("--incognito")
        driver = Chrome(options=options)
        driver.maximize_window()
        sleep(random.choice(self.list_seconds))
        # navigate to login screen
        driver.get(self.link)
        if self.verbose:
            print("Chrome opened")
        return driver

    def _pop_out_notifications(self, driver):
        """Deactivating the popup at the beggining of accessing to twitter (Activate the notifications popup)"""
        popup = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/span/span',
        )
        popup.click()
        if self.verbose:
            print("good for pop out notifications")

    def _connexion(self, driver):
        """Connexion with twitter accound using mail, username and password"""
        connexion = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[1]/a/div/span/span',
        )
        connexion.click()
        sleep(8)
        email_input = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input',
        )
        sleep(random.choice(self.list_seconds))
        email_input.send_keys(self.mail)
        sleep(random.choice(self.list_seconds))
        suivant = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span',
        )
        suivant.click()
        if self.verbose:
            print("good for connexion")
        sleep(7)

    def _suspicious_activity(self, driver):
        """Deactivating the popup for suspicious activity due to incognito mode. For that, entering the username"""
        suspicious = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input',
        )
        sleep(random.choice(self.list_seconds))
        suspicious.send_keys(self.username)
        sleep(random.choice(self.list_seconds))
        suspicious.send_keys(Keys.RETURN)
        if self.verbose:
            print("good for suspicious activity")
        sleep(7)

    def _password(self, driver):
        """Entering the password for finally accessing to our account"""
        password_input = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input',
        )
        sleep(random.choice(self.list_seconds))
        password_input.send_keys(self.password)
        sleep(random.choice(self.list_seconds))
        password_input.send_keys(Keys.RETURN)
        sleep(random.choice(self.list_seconds))
        if self.verbose:
            print("good for password input")

    def _no_reinforcement(self, driver):
        """Sometimes a popup for activating a reinforcement of the account security may appear. Then, it deactivates it."""
        no_reinforcement = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[1]/div/div/svg',
        )
        no_reinforcement.click()
        sleep(random.choice(self.list_seconds))
        if self.verbose:
            print("good for reinforcement")

    def _advanced_link(self, driver):
        """This enables us to search directly by the URL, avoiding many XPATH that could change, it allows you to specify some advanced parameters for the search"""
        company_name = self.research
        encoded_name = urllib.parse.quote(company_name)
        if self.end_date is not None and self.start_date is not None:
            advanced_link = f"https://twitter.com/search?q={encoded_name}%20until%3A{self.end_date}%20since%3A{self.start_date}&src=typed_query&f=live"
        elif self.end_date is None and self.start_date is not None:
            advanced_link = f"https://twitter.com/search?q={encoded_name}%20since%3A{self.start_date}&src=typed_query&f=live"
        elif self.end_date is not None and self.start_date is None:
            advanced_link = f"https://twitter.com/search?q={encoded_name}%20until%3A{self.end_date}&src=typed_query&f=live"
        else:
            advanced_link = (
                f"https://twitter.com/search?q={encoded_name}&src=typed_query&f=live"
            )
        driver.get(advanced_link)
        if self.verbose:
            print("good for advanced link")
        return driver

    def _last_pop_up_notification(self, driver):
        """Sometimes an additionnal pop up could appear then it deactivates it"""
        popup = driver.find_element(
            "xpath",
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]',
        )
        popup.click()
        sleep(random.choice(self.list_seconds))

    def _get_recents(self, driver):
        """get recents tweets from the 'lasts' page for recent activity"""
        recent = driver.find_element(
            "xpath",
            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a/div/div/span',
        )
        recent.click()
        if self.verbose:
            print("good for getting recents tweets")
        sleep(random.choice(self.list_seconds))

    def _collect_all_tweets_from_current_view(self, driver, lookback_limit=25):
        page_cards = driver.find_elements("xpath", '//article[@data-testid="tweet"]')
        if self.verbose:
            print("Good for collecting all tweets")
        if len(page_cards) <= lookback_limit:
            return page_cards
        else:
            return page_cards[-lookback_limit:]

    def _generate_tweet_id(self, tweet):
        if self.verbose:
            print("good for generating tweets id")
        return "".join(tweet)

    def _scroll_down_page(
        self, driver, last_position, scroll_attempt=0, max_attempts=3
    ):
        """The function will try to scroll down the page and will check the current
        and last positions as an indicator. If the current and last positions are the same after `max_attempts`
        the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
        flag will be returned as `True`"""
        end_of_scroll_region = False

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.choice(self.list_seconds))
        curr_position = driver.execute_script("return window.pageYOffset;")
        if curr_position == last_position:
            if scroll_attempt < max_attempts:
                end_of_scroll_region = True
            else:
                _scroll_down_page(last_position, curr_position, scroll_attempt + 1)
        last_position = curr_position
        if self.verbose:
            print("good for scrolling down the page")
        return last_position, end_of_scroll_region

    def _save_tweet_data_to_csv(self, records, output_path, mode="a+"):
        """Saving the data collected into the specified output path with csv format"""
        header = [
            "User",
            "Handle",
            "PostDate",
            "TweetText",
            "ReplyCount",
            "RetweetCount",
            "LikeCount",
        ]
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            open(output_path, "w").close()
            mode = "w"
        with open(output_path, mode=mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if mode == "w":
                writer.writerow(header)
            if records:
                writer.writerow(records)

    def main(self) -> None:

        self._save_tweet_data_to_csv(
            None, self.output_path, "w"
        )  # create file for saving records
        last_position = None
        end_of_scroll_region = False
        unique_tweets = set()

        driver = self._open_set_up_chrome()
        sleep(20)

        # Popup "Activate the notifications"
        try:
            self._pop_out_notifications(driver)
            sleep(random.choice(self.list_seconds))
        except NoSuchElementException:
            print("No popup for activate notifications :)")

        if (
            self.username is not None
            and self.mail is not None
            and self.password is not None
        ):
            # Connexion
            sleep(random.choice(self.list_seconds))
            self._connexion(driver)

            # Ils considèrent qu'on a une activité suspecte :
            try:
                self._suspicious_activity(driver)
            except NoSuchElementException:
                if self.verbose:
                    print("No popup for suspicious activity :)")

            # On rentre le mot de passe
            self._password(driver)

            # On ne veut pas renforcer la sécurité du compte :
            try:
                self._no_reinforcement(driver)
            except NoSuchElementException:
                if self.verbose:
                    print("No popup for reinforcing security :) ")

            # Popup "Activate the notifications"
            try:
                sleep(random.choice(self.list_seconds))
                self._pop_out_notifications(driver)
            except NoSuchElementException:
                sleep(random.choice(self.list_seconds))

        # advanced research from entering the link with dates
        self._advanced_link(driver)
        sleep(random.choice(self.list_seconds))

        # Popup "Activate the notifications"
        try:
            self._pop_out_notifications(driver)
        except NoSuchElementException:
            sleep(random.choice(self.list_seconds))

        # Get the recents
        self._get_recents(driver)

        while not end_of_scroll_region:
            cards = self._collect_all_tweets_from_current_view(driver)
            for card in cards:
                try:
                    tweet = self._get_tweet_data(card)
                except StaleElementReferenceException:
                    continue
                if not tweet:
                    continue
                tweet_id = self._generate_tweet_id(tweet)
                if tweet_id not in unique_tweets:
                    unique_tweets.add(tweet_id)
                    self._save_tweet_data_to_csv(tweet, self.output_path)
            last_position, end_of_scroll_region = self._scroll_down_page(
                driver, last_position
            )
        driver.quit()


def launch():
    # companies that we are interesed on webscrapping
    already_webscrapped = "BP PLC, "
    companies_string = "STORA ENSO OYJ-R SHS, INTERNATIONAL PAPER CO, UPM-KYMMENE OYJ, NEWMONT CORP, EXXON MOBIL CORP, VALERO ENERGY CORP, NUCOR CORP, BARRICK GOLD CORP, FMC CORP, FREEPORT-MCMORAN INC, TOTALENERGIES SE, CONOCOPHILLIPS, ARCHER-DANIELS-MIDLAND CO, POSCO HOLDINGS INC -SPON ADR, BHP GROUP LTD-SPON ADR, TECK RESOURCES LTD-CLS B, RIO TINTO PLC-SPON ADR, WILMAR INTERNATIONAL LTD, MONDI PLC, ANGLO AMERICAN PLC, CENOVUS ENERGY INC, ALTAGAS LTD, WESTLAKE CORP, GLENCORE PLC, MOSAIC CO/THE, MARATHON PETROLEUM CORP,PHILLIPS 66, WEYERHAEUSER CO, ENERGY TRANSFER LP, VIPER ENERGY PARTNERS LP, SUNOCO LP, WESTROCK CO, PEMBINA PIPELINE CORP, ALCOA CORP, ARCELORMITTAL, NUTRIEN LTD, NUTRIEN LTD, DOW INC, CORTEVA INC, OCCIDENTAL PETROLEUM CORP, ONEOK INC, CHEVRON CORP, PIONEER NATURAL RESOURCES CO, TARGA RESOURCES CORP, SCHLUMBERGER LTD, BAKER HUGHES CO, DEVON ENERGY CORP, HESS CORP, MARATHON OIL CORP, WILLIAMS COS INC, COTERRA ENERGY INC, APA CORP, EOG RESOURCES INC, KINDER MORGAN INC, EQT CORP, HALLIBURTON CO, DIAMONDBACK ENERGY INC, S&P 500 ENERGY INDEX"
    companies_list = companies_string.split(",")
    for i in companies_list:
        output_path = f"./../data/webscraped_{'_'.join(i.split())}.csv"
        print(f"Scrapping: {i} in twitter")
        TwitterScrapper(
            research=i,
            output_path=output_path,
            start_date="2017-10-31",
            end_date="2022-09-19",
            mail="mosefdatascience@gmail.com",
            username="mosefdata",
            password="MosefDataScience@",
        ).main()
        print(f"{i} webscrapped")
    print("finished")


if __name__ == "__main__":
    launch()
