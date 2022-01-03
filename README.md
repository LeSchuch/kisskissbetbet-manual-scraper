# KissKissBetBet scraper

KissKissBetBet scraper is a tool that scraps soccer fixtures odds for the 5
major european leagues on all 17 french bookmakers.

<a href="https://asciinema.org/a/nYyG3oxM9zqKGyKzw66PUYJLv?autoplay=1" target="_blank"><img src="https://asciinema.org/a/nYyG3oxM9zqKGyKzw66PUYJLv.svg" width="80%"></a>

## Installation

Clone the repository:

```bash
git clone https://github.com/SchuchDev/kisskissbetbet-manual-scraper
cd kisskissbetbet-manual-scraper
```

Create a python virtual environment and activate it:

```bash
virtualenv venv
source venv/bin/activate
```

Install required python modules:

```bash
pip install -r requirements.txt
```

Scraping uses selenium, for this you need :

- [Google Chrome](https://www.google.com/chrome/) installed

- [Chromedriver](https://chromedriver.chromium.org/)

Please use a version of chromedriver compatible with your Google Chrome

### Usage

Run script in ```kisskissbetbet-manual-scraper``` directory :

```bash
python3 scraper.py
```

### Data format

```python

{
    "bookmaker": "Betclic",
    "league": "Ligue 1"
    "teams": {
        "home": "Troyes",
        "away": "Lyon"
    },
    "odds": {
        "home": 4.0,
        "draw": 3.9,
        "away": 1.73
    }
}

```

## Informations

### Bookmakers supported

- [Barrière Bet](https://www.barrierebet.fr/)
- [Betclic](https://www.betclic.fr/)
- [Betway](https://www.betway.fr/)
- [Bwin](https://www.betway.fr/)
- [Feeling Bet](https://www.france-pari.fr/)
- [France Pari](https://feelingbet.fr/)
- [Geny Bet](https://www.genybet.fr/)
- [Joa Bet](https://www.joabet.fr/)
- [NetBet](https://www.netbet.fr/)
- [ParionsSport](https://www.enligne.parionssport.fdj.fr/)
- [Partouche Sport](https://www.partouchesport.fr/)
- [ParionsSport](https://www.enligne.parionssport.fdj.fr/)
- [PMU](https://www.pmu.fr/)
- [PokerStars Sport](https://www.pokerstarssports.fr/)
- [Unibet](https://www.unibet.fr/)
- [Vbet](https://www.vbet.fr/)
- [Winamax](https://www.winamax.fr/)
- [Zebet](https://www.zebet.fr/)

### Leagues supported

- Bundesliga A
- La Liga
- Ligue 1
- Premier League
- Serie A
