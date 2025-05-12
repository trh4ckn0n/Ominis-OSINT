#!/usr/bin/env python3
import asyncio
import logging
import os
import random
import urllib.parse
import subprocess
import httpx
from colorama import Fore, Style, init
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from src.proxy_handler import scrape_proxies, validate_proxies
from src.tools_handler import fetch_google_results

# Suppress InsecureRequestWarning
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init(autoreset=True)  # Initialize colorama for colored output

DEFAULT_NUM_RESULTS = 500
MAX_RETRY_COUNT = 5

counter_emojis = ['🍻', '📑', '📌', '🌐', '🔰', '💀', '🔍', '📮', 'ℹ️', '📂', '📜', '📋', '📨', '🌟', '💫', '✨', '🔥', '🆔', '🎲']
emoji = random.choice(counter_emojis)  # Select a random emoji for the counter

query = None

async def run_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    # Wait for the subprocess to complete.
    stdout, stderr = await process.communicate()

    # Handle output or errors if needed.
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def main():
    clear_screen()
    print("\n" + f"{Fore.RED}_" * 80 + "\n")

# Tu peux modifier les couleurs comme tu veux
C1 = Fore.LIGHTCYAN_EX      # Contour général
C2 = Fore.YELLOW    # Yeux, langue
C3 = Fore.MAGENTA   # Ombres ou détails
C4 = Fore.GREEN     # Autres touches décoratives



COLORS = [Fore.GREEN, Fore.MAGENTA, Fore.WHITE, Fore.LIGHTYELLOW_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTCYAN_EX]

ascii_base = [
    "⠀⢰⠀⠀⠀               ⠀⠀⠀⠀⣦⠀",  # 0 (cornes)
    "⢀⣿⡄⠀⠀⠀             ⠀⠀⠀⠀⢀⣿⡄",  # 1 (cornes)
    "⣜⢸⣧⠀⠀ ⠀🏴trhacknon🏴⠀⠀⠀⣸⡏⢣",
    "⡿⡀⢿⣆⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⣰⣿⠀⣿",
    "⣇⠁⠘⡌⢷⣀⣠⣴⣾⣟⠉⠉⠉⠉⠉⠉⣻⣷⣦⣄⣀⡴⢫⠃⠈⣸",
    "⢻⡆⠀⠀⠀⠙⠻⣶⢝⢻⣧⡀⠀⠀⢀⣴⡿⡫⣶⠞⠛⠁⠀⠀⣰⡿",
    "⠀⠳⡀⠢⡀⠀⠀⠸⡇⢢⠹⡌⠀⠀⢉⠏⡰⢱⡏⠀⠀⢀⡰⢀⡞⠁",
    "⠀⢀⠟⢦⣈⠲⢌⣲⣿⠀⠀⢱⠀⠀⠜⠀⠁⣾⢒⣡⠔⢉⡴⠻⡄⠀",
    "⠀⢸⠀⠀⣈⣻⣞⡛⠛⢤⡀⠀  ⠀⢀⡠⠟⢛⣓⣟⣉⠀⠀⣧⠀",
    "⠀⢸⣶⢸⣍⡉⠉⠣⡀⠀⠈⢳⣠⣄⡜⠁⠀⢀⡴⠋⠉⠉⡏⢸⡿⠀",
    "⠀⠈⡏⢸⡜⣿⠑⢤⡘⠲⠤⠤⣿⣿⠤⠤⠔⠋⡠⠊⣿⣃⡆⢸⠁⠀",
    "⠀⢀⡿⠋⠙⠿⢷⣤⣹⣦⣀⣠⣼⣧⣄⣀⣠⣎⣤⡾⠿⠋⠙⢺⡄⠀",
    "⠀⠘⣷⠀⠀⢠⠆⠈⢙⡛⢯⣤⠀⠐⣤⡽⠛⠋⠁⠐⡄⠀⢀⣾⠇⠀",
    "⠀⠀⠘⣷⣀⡇⭕ ⣈⡆⢠⠀⠀⠀⢰⣇ ⭕⢸⣀⣼⠏⠀⠀",
    "⠀⠀⠀⣸⡿⣷⣞⠋⠉⢹⠁⢈⠀⠀⠀⠀⡏⠉⠙⣲⣾⢿⣇⠀⠀⠀",
    "⠀⠀⠀⣿⡇⣿⣿⢿⣆⠈⠻⣆⢣⡴⢱⠟⠁⣰⡶⣿⣿⠘⣿⠀⠀⠀",
    "⠀⠀⠀⠹⣆⢈⡿⢸⣿⣻⠦⣼⣦⣴⣯⠴⣞⣿⡇⢻⡇⢸⠏⠀⠀⠀",
    "⠀⠀⠀⠀⠘⣞⣠⢾⣿⣿⣶⣿⣼⣧⣼⣶⣿⣿⡷⢌⢻⡋⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠘⠉⢿⡀⣹🩸🩸🩸🩸⢏⢁⡼⠋⠃⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠈⢻⡟⢿🩸💊🩸⣿⡿⢸⡟⠁⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⢿⡈⢿⣿🩸⣽⡿⠁⣿⣷⣾⣷⣤⣄⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠘⠳⢦⣬⠿⠿⣡⣤⠾⠛⠛⠉⠉⠙⢿⣿⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠦⠴⠞⠁⠀ ⠀⠀⠀⠀⣿⠏⠀⠀",
    "                      ⠟   "
]

def animate():
    flash = True
    duration = 10
    start = time.time()
    i = 0
    try:
        while time.time() - start < duration:
            os.system('cls' if os.name == 'nt' else 'clear')
            color_cycle = COLORS[i % len(COLORS)]

            # Cornes : lignes 0 et 1
            corne_color = Fore.LIGHTRED_EX + Style.BRIGHT if flash else Fore.LIGHTBLUE_EX
            print(corne_color + ascii_base[0])
            print(corne_color + ascii_base[1])
            print(corne_color + ascii_base[2])
            print(corne_color + ascii_base[3])

            for idx, line in enumerate(ascii_base[4:]):
                animated = line

                # Yeux animés ligne 13 (OXO devient ◉◉ ou ●●)
                if "⭕" in animated or "💊" in animated or "🔘" in animated or "🔴" in animated:
                    yeux = "⚫" if flash else "🔴"
                    lang = "🩸" if flash else "💊"
                    # animated = animated.replace("⭕", eye_color + lang + Style.RESET_ALL)
                    eye_color = Fore.LIGHTRED_EX if flash else Fore.LIGHTMAGENTA_EX
                    animated = animated.replace("💊", eye_color + lang + Style.RESET_ALL)
                    animated = animated.replace("⭕", eye_color + yeux + Style.RESET_ALL)
                    animated = animated.replace("🔴", eye_color + yeux + Style.RESET_ALL)

                # Coloration de symboles
                for sym in ["⡿", "⣿", "⢿", "🩸", "⢸", "⣇", "⣷", "⣞"]:
                    animated = animated.replace(sym, color_cycle + sym)

                # Ligne 5 dernières en contour renforcé
                if idx >= len(ascii_base) - 5:
                    animated = C1 + Style.BRIGHT + animated
                else:
                    animated = C1 + animated

                print(animated + Style.RESET_ALL)

            flash = not flash
            i += 1
            time.sleep(0.3)
    except KeyboardInterrupt:
        print(Style.RESET_ALL + "\nAnimation arrêtée.")
    clear_screen()
    print("\n" + f"{Fore.RED}_" * 80 + "\n")
    print(f"""{Fore.RED}
⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣦⠀
⢀⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡄
⣜⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡏⢣
⡿⡀⢿⣆⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⣰⣿⠀⣿
⣇⠁⠘⡌⢷⣀⣠⣴⣾⣟⠉⠉⠉⠉⠉⠉⣻⣷⣦⣄⣀⡴⢫⠃⠈⣸
⢻⡆⠀⠀⠀⠙⠻⣶⢝⢻⣧⡀⠀⠀⢀⣴⡿⡫⣶⠞⠛⠁⠀⠀⣰⡿
⠀⠳⡀⠢⡀⠀⠀⠸⡇⢢⠹⡌⠀⠀⢉⠏⡰⢱⡏⠀⠀⢀⡰⢀⡞⠁
⠀⢀⠟⢦⣈⠲⢌⣲⣿⠀⠀⢱⠀⠀⠜⠀⠁⣾⢒⣡⠔⢉⡴⠻⡄⠀
⠀⢸⠀⠀⣈⣻⣞⡛⠛⢤⡀⠀⠀⠀⠀⢀⡠⠟⢛⣓⣟⣉⠀⠀⣧⠀
⠀⢸⣶⢸⣍⡉⠉⠣⡀⠀⠈⢳⣠⣄⡜⠁⠀⢀⡴⠋⠉⠉⡏⢸⡿⠀
⠀⠈⡏⢸⡜⣿⠑⢤⡘⠲⠤⠤⣿⣿⠤⠤⠔⠋⡠⠊⣿⣃⡆⢸⠁⠀
⠀⢀⡿⠋⠙⠿⢷⣤⣹⣦⣀⣠⣼⣧⣄⣀⣠⣎⣤⡾⠿⠋⠙⢺⡄⠀
⠀⠘⣷⠀⠀⢠⠆⠈⢙⡛⢯⣤⠀⠐⣤⡽⠛⠋⠁⠐⡄⠀⢀⣾⠇⠀
⠀⠀⠘⣷⣀⡇⠀⢀⡀⣈⡆⢠⠀⠀⠀⢰⣇⡀⠀⠀⢸⣀⣼⠏⠀⠀
⠀⠀⠀⣸⡿⣷⣞⠋⠉⢹⠁⢈⠀⠀⠀⠀⡏⠉⠙⣲⣾⢿⣇⠀⠀⠀{Fore.YELLOW}~ {Fore.WHITE}Ominis Osint {Fore.YELLOW}- {Fore.RED}[{Fore.WHITE}Query to web search{Fore.RED}]
⠀⠀⠀⣿⡇⣿⣿⢿⣆⠈⠻⣆⢣⡴⢱⠟⠁⣰⡶⣿⣿⠘⣿⠀⠀⠀{Fore.RED}---------------------------------------
⠀⠀⠀⠹⣆⢈⡿⢸⣿⣻⠦⣼⣦⣴⣯⠴⣞⣿⡇⢻⡇⢸⠏⠀⠀⠀{Fore.YELLOW}~ {Fore.CYAN}Developer{Fore.YELLOW}: {Fore.WHITE} AnonCatalyst {Fore.MAGENTA}<{Fore.RED}
⠀⠀⠀⠀⠘⣞⣠⢾⣿⣿⣶⣿⣼⣧⣼⣶⣿⣿⡷⢌⢻⡋⠀⠀⠀ {Fore.RED}---------------------------------------
⠀⠀⠀⠀⠘⠉⢿⡀⣹⣿⣿⣿⣿⣿⣿⣿⣿⢏⢁⡼⠋⠃⠀⠀⠀⠀{Fore.YELLOW}~ {Fore.CYAN}Github{Fore.YELLOW}:{Fore.BLUE} https://github.com/AnonCatalyst{Fore.RED}
⠀⠀⠀⠀⠀⠀⠈⢻⡟⢿⣿⣿⣿⣿⣿⣿⡿⢸⡟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢿⡈⢿⣿⣿⣿⣽⡿⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⠳⢦⣬⠿⠿⣡⣤⠾⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠦⠴⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")
    print("\n" + f"{Fore.RED}_" * 80 + "\n")
    print(
        f"""
{Fore.YELLOW} {Fore.WHITE}🇴‌🇲‌🇮‌🇳‌🇮‌🇸‌-🇴‌🇸‌🇮‌🇳‌🇹‌ {Fore.CYAN}-by {Fore.MAGENTA}𖨆 {Fore.BLUE}тянα¢кηση {Fore.MAGENTA}𖨆 {Fore.YELLOW}- {Fore.RED}[{Fore.WHITE}Secure Web-Hunter{Fore.RED}]
{Fore.RED} 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {Fore.YELLOW}~ {Fore.CYAN}Developer{Fore.YELLOW}: {Fore.WHITE} AnonCatalyst {Fore.MAGENTA}<{Fore.RED}
    {Fore.RED}------------------------------------------
    {Fore.YELLOW}~ {Fore.CYAN}Modder {Fore.YELLOW} : {Fore.WHITE}   TRHACKNON   {Fore.MAGENTA}<{Fore.RED}
    {Fore.RED}------------------------------------------
    {Fore.YELLOW}~ {Fore.CYAN}Github{Fore.YELLOW}:{Fore.BLUE} https:/github.com/AnonCatalyst/{Fore.RED}
    {Fore.RED}------------------------------------------
    {Fore.YELLOW}~ {Fore.CYAN}Instagram{Fore.YELLOW}:{Fore.BLUE} https:/www.instagram.com/istoleyourbutter/{Fore.RED}
    {Fore.RED}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {Fore.YELLOW}~ {Fore.CYAN}Website{Fore.YELLOW}:{Fore.BLUE} https:/hard2find.dev/{Fore.RED}""")

    print(f"{Fore.RED}_" * 80 + "\n")

    proxies = await scrape_proxies()
    if not proxies:
        logger.error(f" {Fore.RED}No proxies scraped. Exiting...{Style.RESET_ALL}")
        return
    else:
        logger.info(
            f" {Fore.RED}[{Fore.GREEN}+{Fore.RED}]{Fore.WHITE} Beginning proxy validation for proxy rotation{Fore.RED}.{Fore.WHITE}\n")

    valid_proxies = await validate_proxies(proxies)
    if not valid_proxies:
        logger.error(f" {Fore.RED}No valid proxies found. Exiting...{Fore.WHITE}")
        return
    else:
        logger.info(f" >| {Fore.GREEN}Proxies validated successfully{Fore.RED}.{Fore.WHITE}\n")


    print(f"{Fore.RED}_" * 80 + "\n")
    query = input(f" {Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE}  Enter the query to search{Fore.YELLOW}: {Fore.WHITE}")
    language = input(f" {Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE}  Enter the language code (e.g., 'lang_en' for English){Fore.YELLOW}: {Fore.WHITE} ")
    country = input(f" {Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE}  Enter the country code (e.g., 'countryUS' for United States){Fore.YELLOW}: {Fore.WHITE} ")
    start_date = input(f" {Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE}  Enter the start date for the date range (MM/DD/YYYY){Fore.YELLOW}: {Fore.WHITE} ")
    end_date = input(f" {Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE}  Enter the end date for the date range (MM/DD/YYYY){Fore.YELLOW}: {Fore.WHITE} ")
    date_range = (start_date, end_date)
    print(f"{Fore.RED}_" * 80 + "\n")


    await fetch_google_results(query, language, country, date_range, valid_proxies)
    await asyncio.sleep(3)  # Introduce delay between requests

    subprocess.run(["python3", "-m", "src.usr", query])


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    animate()
    asyncio.run(main())
