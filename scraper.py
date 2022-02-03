import datetime
import json
import time
import sys
import os
import unicodedata
from bs4 import BeautifulSoup
from fp.fp import FreeProxy
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


DRIVER_PATH = "/opt/chromedriver"
BOOKMAKERS_JSON = os.getcwd() + "/bookmakers.json"
MATCHS = "matchs"

# Bookmakers
BARRIERE_BET = "Barrière Bet"
BETCLIC = "Betclic"
BETWAY = "Betway"
BWIN = "Bwin"
FEELING_BET = "Feeling Bet"
FRANCE_PARI = "France Pari"
GENY_BET = "Geny Bet"
JOA_BET = "Joa Bet"
NETBET = "Netbet"
PARIONS_SPORT = "Parions Sport"
PARTOUCHE_SPORT = "Partouche Sport"
PMU = "PMU"
POKERSTARS_SPORT = "PokerStars Sport"
UNIBET = "Unibet"
VBET = "Vbet"
WINAMAX = "Winamax"
ZEBET = "Zebet"

SCRAP_BETWAY_LIVE = "uk-flex-middle"
SCRAP_GENY_BET_LIVE = "//li[@data-tab-id='snc-tab-match']"
SCRAP_GENY_BET_POP_UP = "didomi-notice-disagree-button"

# Leagues
BUNDESLIGA = "Bundesliga"
LIGA = "La Liga"
LIGUE_1 = "Ligue 1"
PREMIER_LEAGUE = "Premier League"
SERIE_A = "Serie A"


def init_menu():
    print(
        r"""                   
                                                ___
                                            _.-'___'-._
          _                _              .'--.`   `.--'.
 ___  ___| |__  _   _  ___| |__          /.'   \   /   `.\
/ __|/ __| '_ \| | | |/ __| '_ \        | /'-._/```\_.-'\ |
\__ \ (__| | | | |_| | (__| | | |       |/    |     |    \|
|___/\___|_| |_|\__,_|\___|_| |_|       | \ .''-._.-''. / |
                                         \ |     |     | /
                                          '.'._.-'-._.'.'
                                            '-:_____;-'

--------------------------------------------------------------
                Python script to retrieve the odds
        for the 5 major European soccer championships 
                on all 17 French bookmakers
--------------------------------------------------------------
        """
    )


def menu_bookmaker(bookmakers):
    print("\n[0] Exit")
    for key, i in zip(bookmakers.keys(), range(1, len(bookmakers) + 1)):
        print([i], key)


def menu_league():
    print("\n[0] Exit")
    print("[1] Bundesliga")
    print("[2] La Liga")
    print("[3] Ligue 1")
    print("[4] Premier League")
    print("[5] Serie A")


def get_dict_bookmakers():
    with open(BOOKMAKERS_JSON, "r") as file:
        return json.load(file)


def handle_bookmaker_choice(bookmaker_choice, bookmakers):
    if bookmaker_choice not in range(1, len(bookmakers) + 1):
        if bookmaker_choice == 0:
            print("Exit")
            sys.exit()
        print("Bookmaker choice not conformed")
        sys.exit()
    return bookmakers[list(bookmakers.keys())[bookmaker_choice - 1]]


def handle_league_choice(league_choice, bookmakers):
    if league_choice == 1:
        return BUNDESLIGA
    elif league_choice == 2:
        return LIGA
    elif league_choice == 3:
        return LIGUE_1
    elif league_choice == 4:
        return PREMIER_LEAGUE
    elif league_choice == 5:
        return SERIE_A
    elif league_choice == 0 or league_choice > 5:
        print("Please choose a valid league number")
        menu_bookmaker(bookmakers)


def format_bookmaker_name(name):
    return str(name).lower().replace(" ", "_").replace("è", "e")


def format_league_name(name):
    return str(name).lower().replace(" ", "_")


def format_team_name(team):
    return unicodedata.normalize("NFKD", validate_string(team))


def format_odd(odd):
    return round(float(str(odd).replace(",", ".")), 2)


def get_current_date():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def is_valid_fixture(odds, teams):
    try:
        float(str(odds[0]).replace(",", "."))
        float(str(odds[1]).replace(",", "."))
        float(str(odds[2]).replace(",", "."))
    except ValueError:
        return False
    if min([format_odd(odds[0]), format_odd(odds[1]), format_odd(odds[2])]) >= 3:
        return False
    if any(["," in teams[0], "," in teams[1]]):
        return False
    return True


def get_duration(begin_date, end_date):
    duration = ""
    diff = datetime.datetime.strptime(
        end_date, "%Y/%m/%d %H:%M:%S"
    ) - datetime.datetime.strptime(begin_date, "%Y/%m/%d %H:%M:%S")
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours:
        duration += "{}h".format(hours)
    if minutes:
        duration += " {}m".format(minutes)
    if seconds:
        duration += " {}s".format(seconds)
    return duration.strip()


def get_webdriver(bookmaker):

    options = webdriver.ChromeOptions()
    options.headless = True

    if bookmaker not in [BWIN]:
        print("\n[+] Getting an user-agent [+]")
        try:
            ua = UserAgent().random
        except IndexError:
            ua = UserAgent().random
        options.add_argument("--user-agent={}".format(ua))
        print("[+] User-Agent: {} [+]".format(ua))

    # print("\n[+] Getting a proxy [+]")
    # proxy = FreeProxy(country_id=["FR"], timeout=1, rand=True).get()
    # webdriver.DesiredCapabilities.CHROME["proxy"] = {
    #     "httpProxy": proxy,
    #     "ftpProxy": proxy,
    #     "sslProxy": proxy,
    #     "proxyType": "MANUAL",
    # }
    # print("[+] Proxy: {} [+]".format(proxy))

    options.add_argument("--window-size={}".format("1920,2000"))
    options.add_argument("--no-sandbox")
    webdriver.DesiredCapabilities.CHROME["acceptSslCerts"] = True

    return webdriver.Chrome(options=options, service=Service(DRIVER_PATH))


def scrap_bookmaker(bookmaker, league, retry=False):

    begin_date = get_current_date()

    driver = get_webdriver(bookmaker["name"])
    url = bookmaker["url"] + bookmaker["url_{}".format(format_league_name(league))]

    print("\n[+] Fetching {} fixtures for {} [+]".format(bookmaker["name"], league))
    print("[+] URL: {} [+]\n".format(url))

    try:
        driver.get(url)
        time.sleep(5 if not retry else 10)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//{}[contains(@class, '{}')]".format(
                        bookmaker["html_cards_attribute"], bookmaker["html_cards_class"]
                    ),
                )
            )
        )
        if bookmaker["name"] == BETWAY:
            buttons = driver.find_elements(By.CLASS_NAME, SCRAP_BETWAY_LIVE)
            for button in buttons:
                if button.text == MATCHS:
                    button.click()
                    break
        elif bookmaker["name"] == GENY_BET:
            driver.find_element(By.ID, SCRAP_GENY_BET_POP_UP).click()
            driver.find_element(By.XPATH, SCRAP_GENY_BET_LIVE).click()
    except TimeoutException as e:
        print("[!] Selenium exception raised [!]\n {}".format(e))
        if not retry:
            return scrap_bookmaker(bookmaker, league, retry=True)
        print("[!] Scraping error, fixture card was not found [!]\n")
        return None
    except Exception as e:
        raise
        print("[!] Selenium exception raised [!]\n {}".format(e))
        if not retry:
            return scrap_bookmaker(bookmaker, league, retry=True)
        return None
    finally:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

    fixtures = parse_data(soup, bookmaker)

    if not fixtures:
        if not retry:
            print(
                "[!] Retry once fetching {} fixtures for {} [!]".format(
                    bookmaker["name"], league
                )
            )
            return scrap_bookmaker(bookmaker, league, retry=True)
        print(
            "[!] No result in fetching {} fixtures for {} [!]\n".format(
                bookmaker["name"], league
            )
        )
        return None

    print(
        "\n[+] {} fixtures found on {} for {} [+]\n".format(
            len(fixtures), bookmaker["name"], league
        )
    )

    for f in fixtures:
        print(
            json.dumps(
                json_load(f),
                ensure_ascii=False,
                indent=4,
            ),
            "\n",
        )
        time.sleep(1)

    print(
        "\n[+] Time elapsed : {} [+]\n".format(
            get_duration(begin_date, get_current_date())
        )
    )

    return fixtures


def parse_data(soup, bookmaker):

    fixtures = []
    cards = soup.find_all(
        bookmaker["html_cards_attribute"], class_=bookmaker["html_cards_class"]
    )
    for card in cards:
        teams = []
        odds = []
        parsed = False

        try:
            # Parse teams
            scrap_teams = card.find_all(
                bookmaker["html_teams_attribute"],
                class_=bookmaker["html_teams_class"],
            )

            if all([len(list(scrap_teams)) == 1, bookmaker["name"] == JOA_BET]):
                break
            if len(list(scrap_teams)) == 1:
                if bookmaker["name"] == BETWAY:
                    scrap_teams = scrap_teams[0].text.replace("\n", "").split("       ")
                if any(b == bookmaker["name"] for b in (FEELING_BET, FRANCE_PARI)):
                    scrap_teams = scrap_teams[0].text.split("/")
                if bookmaker["name"] == PMU:
                    scrap_teams = scrap_teams[0].text.replace("\n", "").split("//")
                if any(b == bookmaker["name"] for b in (PARIONS_SPORT, UNIBET)):
                    scrap_teams = scrap_teams[0].text.split(" - ")
                parsed = True

            for t in scrap_teams:
                team = t.strip() if parsed else t.text.strip()
                if all([team, not team.isdigit(), team != "N"]):
                    teams.append(team)

            # Parse odds
            scrap_odds = card.find_all(
                bookmaker["html_odds_attribute"], class_=bookmaker["html_odds_class"]
            )

            for o in scrap_odds:
                odd = o.text.strip()
                if all([odd, odd != "..."]):
                    odds.append(odd)
            if bookmaker["name"] == ZEBET:
                for o in range(0, len(odds), 2):
                    try:
                        odds.remove(odds[o])
                    except IndexError:
                        continue

            # Construct fixture data
            try:
                if is_valid_fixture(odds, teams):
                    fixtures.append(
                        {
                            "teams": {
                                "home": format_team_name(teams[0]),
                                "away": format_team_name(teams[1]),
                            },
                            "odds": {
                                "home": format_odd(odds[0]),
                                "draw": format_odd(odds[1]),
                                "away": format_odd(odds[2]),
                            },
                        }
                    )
            except IndexError:
                continue

        except:
            raise

    return fixtures


def json_load(data):
    return json.loads(str(data).replace("'", '"'), strict=False)


def validate_string(string):
    for s in ["'", '"']:
        if string.find(s) != -1:
            string = string.replace(s, " ")
    return str(string)


def debug(elements):
    debug = []
    for e in elements:
        debug.append(e.text)
    print(debug)


if __name__ == "__main__":

    # Display init menu
    init_menu()

    # Get bookmakers data
    dict_bookmakers = get_dict_bookmakers()

    # Infinite loop
    while 1:

        # Display bookmakers choices
        menu_bookmaker(dict_bookmakers)
        bookmaker_choice = int(input("Choose a bookmaker: "))

        # Handle user choice for his bookmaker selection
        bookmaker = handle_bookmaker_choice(bookmaker_choice, dict_bookmakers)
        print("\n[+] You chose {} [+]".format(bookmaker["name"]))

        # Display leagues choices
        menu_league()
        league_choice = int(input("Choose a league: "))

        # Handle user choice for his league selection
        league = handle_league_choice(league_choice, dict_bookmakers)
        print("\n[+] You chose {} [+]".format(league))

        # Scrap data
        data = scrap_bookmaker(bookmaker, league)
