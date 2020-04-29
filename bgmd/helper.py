from bs4 import BeautifulSoup


def crop_mono(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_pages: int = 1
    column_a = soup.find(id='columnA')
    cc = column_a.find_all('li', {'class': 'clearit'})
    if (pin := column_a.find('div', {'class': 'page_inner'})) is not None:
        all_pages = max(int(a['href'].rsplit("=", 1)[1]) for a in pin.find_all('a', {'class': 'p'}))
    return [link.find('a', {'class', 'l'})['href'] for link in cc], all_pages
