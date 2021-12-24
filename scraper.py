import json
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fp.fp import FreeProxy
from fake_useragent import UserAgent


DRIVER_PATH = "/opt/chromedriver"
BOOKMAKERS_JSON = os.getcwd() + "/bookmakers.json"

# LEAGUES
BUNDESLIGA = "Bundesliga"
LIGA = "La Liga"
LIGUE_1 = "Ligue 1"
PREMIER_LEAGUE = "Premier League"
SERIE_A = "Serie A"


def init_menu():
    print("###################################################\n")
    print("SCRIPT TO GET FOOTBALL ODDS ON FRENCH BOOKMAKERS")
    print("Made with love by Schuch")
    print("\n###################################################")


def menu_bookmaker(bookmakers):
    print("\n[0] Exit")
    for key, i in zip(bookmakers.keys(), range(1, len(bookmakers) + 1)):
        print([i], key)
    print("\n")


def menu_league():
    print("\n[0] Exit")
    print("[1] Bundesliga")
    print("[2] La Liga")
    print("[3] Ligue 1")
    print("[4] Premier League")
    print("[5] Serie A\n")


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
        return SERIE_A
    elif league_choice == 5:
        return PREMIER_LEAGUE
    elif league_choice == 0 or league_choice > 5:
        print("Please choose a valid league number")
        menu_bookmaker(bookmakers)


def format_bookmaker_name(name):
    return str(name.lower().replace(" ", "_").replace("è", "e"))


def format_league_name(name):
    return str(name.lower().replace(" ", "_"))


def get_webdriver(window_size, user_agent=True, proxy=False):
    options = webdriver.ChromeOptions()
    options.headless = True
    if user_agent:
        ua = UserAgent()
        options.add_argument("--user-agent={0}".format(ua.random))
    if proxy:
        proxy = FreeProxy(country_id=["FR"], timeout=1, rand=True).get()
        options.add_argument("--proxy-server={0}".format(proxy))
    options.add_argument("--window-size={0}".format(window_size))
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(chrome_options=options, executable_path=DRIVER_PATH)


def scrap_bookmaker(bookmaker, league):

    user_agent = True if not "Bwin" in bookmaker["name"] else False
    driver = get_webdriver(bookmaker["window_size"], user_agent)
    url = bookmaker["url"] + bookmaker["url_{}".format(format_league_name(league))]

    print("\n[+] Fetching {0} odds for {1} [+]".format(bookmaker["name"], league))
    print("[+] URL: {} [+]\n".format(url))

    driver.get(url)
    time.sleep(bookmaker["wait"])

    try:

        scrap_teams = driver.find_elements_by_class_name(bookmaker["div_teams"])
        scrap_odds = (
            driver.find_elements_by_class_name(bookmaker["div_odds"])
            if bookmaker["name"] != "Bwin"
            else driver.find_elements_by_xpath(
                "//div[contains(@class, '{}')]".format(bookmaker["div_odds"])
            )
        )
    except:
        raise

    (home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds,) = globals()[
        "scrap_{}".format(format_bookmaker_name(bookmaker["name"]))
    ](scrap_teams, scrap_odds)

    driver.quit()

    data = sort_data(
        home_teams,
        away_teams,
        home_teams_odds,
        away_teams_odds,
        draw_odds,
    )

    return display_json(data)


def json_load(data):
    return json.loads(str(data).replace("'", '"'), strict=False)


def validate_string(string):
    for s in ["'", '"']:
        if string.find(s) != -1:
            string = string.replace(s, " ")
    return string


def display_json(data):
    if data:
        print("[+] Scraping result in JSON format [+]\n")
        try:
            print(
                json.dumps(
                    json_load(data),
                    ensure_ascii=False,
                    indent=4,
                )
            )
        except:
            print(data)
            raise
        print("\n")
    else:
        print(
            "[!] No result in fetching {0} odds for {1} [!]\n".format(
                bookmaker["name"], league
            )
        )
    return None


def is_odds(home_team_odd, draw_odd, away_team_odd):
    try:
        float(home_team_odd)
        float(draw_odd)
        float(away_team_odd)
        return True
    except ValueError:
        return False


def sort_data(home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds):
    datas = []
    for h, a, ho, ao, do in zip(
        home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds
    ):
        if is_odds(ho, do, ao):
            datas.append(
                {
                    "HomeTeam": validate_string(h),
                    "AwayTeam": validate_string(a),
                    "HomeTeamOdd": ho,
                    "DrawOdd": do,
                    "AwayTeamOdd": ao,
                }
            )
    return json_load(datas)


def sort_home_away_teams(teams, web_element=True):
    home_teams = []
    away_teams = []
    if web_element == True:
        for t in range(0, len(teams) - 1, 2):
            home_teams.append(teams[t].text)
            away_teams.append(teams[t + 1].text)
        return home_teams, away_teams
    for t in range(0, len(teams) - 1, 2):
        home_teams.append(teams[t])
        away_teams.append(teams[t + 1])
    return home_teams, away_teams


def sort_odds(odds, step=3, web_element=True):
    home_teams_odds = []
    away_teams_odds = []
    draw_odds = []
    if web_element == True:
        for o in range(0, len(odds), step):
            try:
                home_teams_odds.append(odds[o].text.replace(",", "."))
                draw_odds.append(odds[o + 1].text.replace(",", "."))
                away_teams_odds.append(odds[o + 2].text.replace(",", "."))
            except IndexError:
                continue
        return home_teams_odds, away_teams_odds, draw_odds
    for o in range(0, len(odds), step):
        try:
            home_teams_odds.append(odds[o].replace(",", "."))
            draw_odds.append(odds[o + 1].replace(",", "."))
            away_teams_odds.append(odds[o + 2].replace(",", "."))
        except IndexError:
            continue
    return home_teams_odds, away_teams_odds, draw_odds


## SCRAPPING SCRIPTS BY BOOKMAKERS


def scrap_barriere_bet(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# BETCLIC
def scrap_betclic(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds, 6)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# BETWAY
def scrap_betway(scrap_teams, scrap_odds):

    home_teams = []
    away_teams = []
    for team in scrap_teams:
        home_teams.append(team.text.split("\n")[0])
        away_teams.append(team.text.split("\n")[1])

    sorted_odds = []
    for o in scrap_odds:
        if o.text:
            sorted_odds.append(o.text)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(sorted_odds, 3, False)

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# BWIN
def scrap_bwin(scrap_teams, scrap_odds):

    teams = []
    for t in scrap_teams:
        if t.text not in ["", "-"]:
            teams.append(t.text)
    home_teams = []
    away_teams = []
    for t in range(0, len(teams), 2):
        try:
            home_teams.append(teams[t])
            away_teams.append(teams[t + 1])
        except IndexError:
            continue

    odds = []
    for o in scrap_odds:
        if o.text not in ["", "-"]:
            odds.append(o.text)

    home_teams_odds = []
    away_teams_odds = []
    draw_odds = []
    for o in range(0, len(scrap_odds), 5):
        try:
            home_teams_odds.append(scrap_odds[o].text)
            draw_odds.append(scrap_odds[o + 1].text)
            away_teams_odds.append(scrap_odds[o + 2].text)
        except IndexError:
            continue

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# FRANCE PARI
def scrap_france_pari(scrap_teams, scrap_odds):

    sorted_teams = []
    for team in scrap_teams:
        sorted_teams += team.text.split(" / ")
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)

    sorted_odds = []
    for odd in scrap_odds:
        if odd.text:
            sorted_odds.append(odd)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(sorted_odds)

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# FEELING BET
def scrap_feeling_bet(scrap_teams, scrap_odds):

    sorted_teams = []
    for team in scrap_teams:
        sorted_teams += team.text.split(" / ")
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)

    sorted_odds = []
    for odd in scrap_odds:
        if odd.text:
            sorted_odds.append(odd)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(sorted_odds)

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# GENY BET
def scrap_geny_bet(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# JOA BET
def scrap_joa_bet(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds, 10)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# NETBET
def scrap_netbet(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# PARIONS SPORT EN LIGNE
def scrap_parions_sport(scrap_teams, scrap_odds):
    sorted_teams = []
    for team in scrap_teams:
        sorted_teams += team.text.split(" - ")
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# PARTOUCHE SPORT
def scrap_partouche_sport(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# PMU
def scrap_pmu(scrap_teams, scrap_odds):

    sorted_teams = []
    for team in scrap_teams:
        if "//" in team.text:
            sorted_teams += team.text.split(" // ")
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)

    sorted_odds = []
    for odd in scrap_odds:
        if odd.text != "":
            sorted_odds.append(odd)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(sorted_odds)

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# POKERSTARS SPORT
def scrap_pokerstars_sport(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# UNIBET
def scrap_unibet(scrap_teams, scrap_odds):

    sorted_teams = []
    for team in scrap_teams:
        sorted_teams += team.text.split(" - ")
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)

    home_teams_odds = []
    away_teams_odds = []
    draw_odds = []
    for o in range(0, len(scrap_odds) - 1, 6):
        home_teams_odds.append(scrap_odds[o + 1].text)
        draw_odds.append(scrap_odds[o + 3].text)
        away_teams_odds.append(scrap_odds[o + 5].text)

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# Vbet
def scrap_vbet(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# WINAMAX
def scrap_winamax(scrap_teams, scrap_odds):
    home_teams, away_teams = sort_home_away_teams(scrap_teams)
    home_teams_odds, away_teams_odds, draw_odds = sort_odds(scrap_odds)
    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# ZEBET
def scrap_zebet(scrap_teams, scrap_odds):

    sorted_teams = []
    for team in scrap_teams:
        if team.text != "" and team.text != "N":
            sorted_teams.append(team.text)
    home_teams, away_teams = sort_home_away_teams(sorted_teams, False)

    odds = []
    for odd in scrap_odds:
        if odd.text:
            odds.append(odd.text.replace(",", "."))

    home_teams_odds = []
    away_teams_odds = []
    draw_odds = []
    for o in range(0, len(odds) - 1, 3):
        try:
            if (
                float(odds[o]) > 3 and float(odds[o + 1]) > 3 and float(odds[o + 2]) > 3
            ) == False:
                home_teams_odds.append(odds[o])
                draw_odds.append(odds[o + 1])
                away_teams_odds.append(odds[o + 2])
        except:
            pass

    return home_teams, away_teams, home_teams_odds, away_teams_odds, draw_odds


# DEBUG
def debug(elements):
    debug = []
    for e in elements:
        debug.append(e.text)
    print(debug)


if __name__ == "__main__":
    dict_bookmakers = get_dict_bookmakers()

    # Infinite loop
    while 1:

        # Display init menu
        init_menu()

        # Display bookmakers choices
        menu_bookmaker(dict_bookmakers)
        bookmaker_choice = int(input("Choose a bookmaker: "))

        # Handle user choice for his bookmaker selection
        bookmaker = handle_bookmaker_choice(bookmaker_choice, dict_bookmakers)

        # Display leagues choices
        menu_league()
        league_choice = int(input("Choose a soccer league: "))

        # Handle user choice for his league selection
        league = handle_league_choice(league_choice, dict_bookmakers)

        data = scrap_bookmaker(bookmaker, league)
