from bs4 import BeautifulSoup           # parsing html page
import requests                         # get html page of the website
from random import choice               # choosing quote randomly
from time import sleep                  # delay scraping
from csv import DictWriter, DictReader  # Backup/Restore functionality

# Constant Definitions for the scraper:
QUOTES_WEBSITE_URL = "http://quotes.toscrape.com"
SLEEP_TIME = 0


def get_list_of_quotes(amount_of_pages_to_scrape):
    """
    method for scraping all quotes from the quotes website:
    :param      amount_of_pages_to_scrape: the amount of pages which the scraper needs to scrape the quotes from.
    :return:    list of quotes which found in all the pages.
                The list contain quote information represented in a dictionary format.

                dictionary of quote:
                {
                    "text":         actual quote,
                    "author":       quote author,
                    "author_href":  href for the author biography
                }
    """
    quotes_to_return = []
    page = "/page/1/"

    for i in range(amount_of_pages_to_scrape):

        response = requests.get(QUOTES_WEBSITE_URL + page)
        soup_object = BeautifulSoup(response.text, "html.parser")
        quotes = soup_object.find_all(class_="quote")

        print(f"Now scraping page: {QUOTES_WEBSITE_URL + page}")

        for q in quotes:
            quotes_to_return.append(
                {
                    "text": (q.find(class_="text").get_text()),
                    "author": (q.find(itemprop="author").get_text()),
                    "author_href": (q.find("a")["href"])
                }
            )

        # last page does not have 'next page'.
        if i != amount_of_pages_to_scrape - 1:
            page = soup_object.find(class_="pager").find(class_="next").find("a")["href"]

        sleep(SLEEP_TIME)
    return quotes_to_return


def get_amount_of_pages():
    """
    method to identify how many pages needs to be scrape.
    :return: amount of pages to be scraped.
    """
    flag = True
    page = "/page/1/"
    count = 1

    while flag:
        response = requests.get(QUOTES_WEBSITE_URL + page)
        soup_object = BeautifulSoup(response.text, "html.parser")
        page = soup_object.find(class_="pager").find(class_="next")

        if page:
            page = page.find("a")["href"]
            count += 1
        else:
            flag = False
        sleep(SLEEP_TIME)

    return count


def get_info_about_author(author_href):
    """
    method for resolving information about the author: date and place of birth.
    :param author_href: suffix for the url for resolving information about author.
    :return: tuple of (date_of_birth, place_of_birth)
    """
    response = requests.get(QUOTES_WEBSITE_URL + author_href)
    soup_object = BeautifulSoup(response.text, "html.parser")
    return soup_object.find(class_="author-born-date").get_text(), \
        soup_object.find(class_="author-born-location").get_text()


def print_hint_message(quote, guess, remaining_guesses):
    """
    method for printing a hint message.
    :param quote: information of the quote the user should guess.
    :param guess: the guess of the user.
    :param remaining_guesses: remaining tries for the user.
    :return: doesn't return anything. only printing.
    """
    if guess.lower() == quote["author"].lower():
        print(f'Correct!! the author was: {quote["author"]}')
    elif remaining_guesses == 3:
        author_info = get_info_about_author(quote["author_href"])
        print(f"Hint: The author was born on {author_info[0]} {author_info[1]}")
    elif remaining_guesses == 2 or remaining_guesses == 1:
        author_full_name = quote["author"].split(" ")
        if remaining_guesses == 2:
            print(f'Here\'s a hint: The first name of the author start with {author_full_name[0][0]}')
        elif remaining_guesses == 1:
            print(f'Here\'s a hint: The last name of the author start with {author_full_name[1][0]}')


def backup_quotes(filename, quotes):
    """
    Backing up all quotes which scraped from website.
    :param filename: name of the file which hold backup information.
    :param quotes: quotes to backup.
    :return: void
    """
    with open(filename, "w", encoding='utf-8') as file:
        headers = ["text", "author", "author_href"]
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        for q in quotes:
            csv_writer.writerow(q)


def get_quotes_from_backup(filename):
    """
    get quotes from csv backup file.
    :param filename: name of the file
    :return: list of all quotes information.
    """

    quotes_to_return = []
    try:
        with open(filename, encoding='utf-8') as file:
            csv_reader = DictReader(file)
            next(csv_reader)
            for row in csv_reader:
                quotes_to_return.append(row)

    except FileNotFoundError:
        raise FileNotFoundError("File not found")

    return quotes_to_return


def start_game(list_of_quotes):
    """
    starting the guessing game.
    :param list_of_quotes: all the quotes which scraped.
    :return: void
    """

    guess = ""
    remaining_guesses = 4
    chosen_quote = choice(list_of_quotes)

    print(f"""\nHere is a random quote for you:
        {chosen_quote["text"]}""")

    while guess.lower() != chosen_quote["author"].lower():
        if remaining_guesses == 0:
            print(f'The author was: {chosen_quote["author"]}')
            break
        print(f"\nGuess who sad the quote: \nguesses remaining: {remaining_guesses}")
        print_hint_message(chosen_quote, guess, remaining_guesses)
        guess = input()
        remaining_guesses -= 1


if __name__ == "__main__":

    keep_playing = True

    # Optional - restore quotes from backup:
    # list_of_quotes = get_quotes_from_backup("quotes_backup.csv")

    amount_of_pages = get_amount_of_pages()
    list_of_quotes = get_list_of_quotes(amount_of_pages)
    backup_quotes("quotes_backup.csv", list_of_quotes)

    while keep_playing:
        start_game(list_of_quotes)
        user_answer_for_playing_again = input("Do you want to play again? (y/n) ")
        if user_answer_for_playing_again.lower() not in ("yes", "y"):
            keep_playing = False

    print("Bye bye :)")
