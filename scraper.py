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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


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
        duration += "{0}h".format(hours)
    if minutes:
        duration += " {0}m".format(minutes)
    if seconds:
        duration += " {0}s".format(seconds)
    return duration.strip()


def get_webdriver(bookmaker):

    options = webdriver.ChromeOptions()
    options.headless = True

    if bookmaker not in [BWIN]:
        print("\n[+] Getting a user-agent [+]")
        time.sleep(1)
        ua = UserAgent().random
        options.add_argument("--user-agent={0}".format(ua))
        print("[+] User-Agent: {} [+]".format(ua))

    print("\n[+] Getting a proxy [+]")
    proxy = FreeProxy(country_id=["FR"], timeout=1, rand=True).get()
    webdriver.DesiredCapabilities.CHROME["proxy"] = {
        "httpProxy": proxy,
        "ftpProxy": proxy,
        "sslProxy": proxy,
        "proxyType": "MANUAL",
    }
    print("[+] Proxy: {} [+]".format(proxy))

    options.add_argument("--window-size={}".format("1920,2000"))
    options.add_argument("--no-sandbox")
    webdriver.DesiredCapabilities.CHROME["acceptSslCerts"] = True

    return webdriver.Chrome(options=options, service=Service(DRIVER_PATH))


def scrap_bookmaker(bookmaker, league, retry=False):

    begin_date = get_current_date()

    driver = get_webdriver(bookmaker["name"])
    url = bookmaker["url"] + bookmaker["url_{}".format(format_league_name(league))]

    print("\n[+] Fetching {0} odds for {1} [+]".format(bookmaker["name"], league))
    print("[+] URL: {} [+]\n".format(url))

    try:
        driver.get(url)
    except Exception as e:
        print("[!] Selenium exception, {} [!]\n".format(e))
        return scrap_bookmaker(config, bookmaker, league)

    # time.sleep(5)

    if bookmaker["name"] == "Betway":
        event = driver.find_element(
            By.XPATH, "//*[@id='snc-central-column']/div[2]/div[3]/ul/li[1]"
        )
        if event and event.text.strip().lower() != MATCHS:
            button = driver.find_element(
                By.XPATH, "//*[@id='snc-central-column']/div[2]/div[3]/ul/li[2]/a/span"
            )
            if button:
                button.click()

    if bookmaker["name"] == "Geny Bet":
        event = driver.find_element(
            By.XPATH, "//*[@id='snc-component-tabs-centred']/ul/li[1]"
        )
        if event and event.text.strip().lower() != MATCHS:
            pop_up = driver.find_element(
                By.XPATH, "//*[@id='didomi-popup']/div/div/div/span"
            )
            if pop_up:
                pop_up.click()
                time.sleep(2)
            button = driver.find_element(By.XPATH, "//*[@id='snc-tab-match']")
            if button:
                button.click()
                time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    fixtures = parse_data(soup, bookmaker)

    if not fixtures:
        if not retry:
            print(
                "[!] Retry once fetching {0} odds for {1} [!]".format(
                    bookmaker["name"], league
                )
            )
            return scrap_bookmaker(bookmaker, league, True)
        print(
            "[!] No result in fetching {0} odds for {1} [!]\n".format(
                bookmaker["name"], league
            )
        )
        return None

    print("[+] Displaying scraping result [+]\n")

    for f in fixtures:
        print(
            json.dumps(
                json_load(f),
                ensure_ascii=False,
                indent=4,
            )
        )
        time.sleep(1)

    print(
        "\n[+] {} fixtures found on {} for {} [+]".format(
            len(fixtures), bookmaker["name"], league
        )
    )

    print(
        "\n[+] Time elapsed : {} [+]\n".format(
            get_duration(begin_date, get_current_date())
        )
    )

    return fixtures


def parse_data(soup, bookmaker):

    fixtures = []
    for card in soup.find_all(
        bookmaker["html_cards_attribute"], class_=bookmaker["html_cards_class"]
    ):

        teams = []
        odds = []
        parsed = False

        try:

            # Parse teams
            scrap_teams = card.find_all(
                bookmaker["html_teams_attribute"],
                class_=bookmaker["html_teams_class"],
            )

            # PMU
            if len(list(scrap_teams)) == 1:
                scrap_teams = scrap_teams[0].text.replace("\n", "").split("//")

                #
                if len(list(scrap_teams)) == 1:
                    scrap_teams = scrap_teams[0].split("/")

                    # Betway
                    if len(list(scrap_teams)) == 1:
                        scrap_teams = scrap_teams[0].split("              ")

                        #
                        if len(list(scrap_teams)) == 1:
                            scrap_teams = scrap_teams[0].split("-")

                parsed = True

            for t in scrap_teams:
                team = t.strip() if parsed else t.text.strip()
                if team and not team.isdigit() and team != "N":
                    teams.append(team)

            # Parse odds
            scrap_odds = card.find_all(
                bookmaker["html_odds_attribute"], class_=bookmaker["html_odds_class"]
            )

            for o in scrap_odds:
                odd = o.text.strip()
                if odd and odd != "...":
                    odds.append(odd)
            if bookmaker["name"] == ZEBET:
                for o in range(0, len(odds), 2):
                    try:
                        odds.remove(odds[o])
                    except IndexError:
                        continue

            # Construct fixture data
            try:
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
    if 1:

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
