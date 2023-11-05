from bs4 import BeautifulSoup
import re
import pandas as pd
from requests_html import HTMLSession

# Create DataFrame
df = pd.DataFrame(columns=["Title", "Author(s)", "Pages", "Genre(s)"])

# Set initial variables
next_page = True
pg_num = 0

# create an HTML Session object
session = HTMLSession()

# Cycle through pages
while next_page:
    pg_num += 1
    url = f"https://app.thestorygraph.com/to-read/katieconrad?page={pg_num}"

    # Use the HTML Session object to connect to webpage
    resp = session.get(url)

    # Run JavaScript code on webpage
    resp.html.render(timeout=20)

    soup = BeautifulSoup(resp.html.html, "html.parser")

    # Isolate to-read list (prevents books in "Up Next" list from being counted twice)
    all_books = soup.find_all(class_="to-read-books-panes")
    for div in all_books:
        # Isolate each book and create a list with all required elements for each one
        books = div.find_all(class_="mt-5")
        if len(books) != 0:
            for item in books:
                book_content = item.find_all(class_="book-pane-content")
                for book in book_content:
                    # Create a list to store the book info
                    new_entry = []
                    # Isolate the section that contains the title and author
                    title_author = book.find_all(class_="book-title-author-and-series")
                    for result in title_author:
                        # Remove duplicates caused by storygraph having two versions of title
                        h3s = result.find_all(class_="text-base")
                        for header in h3s:
                            # Isolate book title and add to list
                            title = header.find("a", href=re.compile("books"))
                            new_entry.append(title.text)
                        # Isolate book author(s) and if there is more than one author, join them - then add to list
                        authors = result.find_all("a", href=re.compile("authors"))
                        authors = [name.text for name in authors]
                        author_combo = ", ".join(authors)
                        new_entry.append(author_combo)
                    # Isolate the section that contains the page numbers
                    pages = book.find("p", class_="text-darkestGrey")
                    pages = pages.text.strip().split(" ")[0]
                    new_entry.append(pages)
                    # Isolate the section that contains the genre tags
                    tag_section = book.find_all(class_="book-pane-tag-section")
                    for section in tag_section:
                        tags = book.find_all(class_="my-1")
                        for tag_group in tags:
                            genres = tag_group.find_all(class_="text-teal-700")
                            genres = [genre.text for genre in genres]
                            genre_combo = ", ".join(genres)
                            new_entry.append(genre_combo)
                    df.loc[len(df)] = new_entry
        # Stop when it reaches a page with no results
        else:
            next_page = False

# Convert df to csv
with open("books_list.txt", "w") as csv_file:
    df.to_csv(path_or_buf=csv_file, index=False)
