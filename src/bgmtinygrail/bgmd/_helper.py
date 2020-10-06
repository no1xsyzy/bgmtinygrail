from bs4 import BeautifulSoup


def crop_mono(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_pages: int = 1
    column_a = soup.find(id='columnA')
    # noinspection SpellCheckingInspection
    # class name is not defined by this project
    cc = column_a.find_all('li', {'class': 'clearit'})
    if (pin := column_a.find('div', {'class': 'page_inner'})) is not None:
        all_pages = max(int(a['href'].rsplit("=", 1)[1]) for a in pin.find_all('a', {'class': 'p'}))
    return [link.find('a', {'class', 'l'})['href'] for link in cc], all_pages


def multi_page(getter, base_url, selector):
    result = []
    soup = BeautifulSoup(getter(base_url).content, 'html.parser')
    result.extend(soup.select(selector))
    if (pin := soup.select_one("div.page_inner")) is not None:
        all_pages = max(int(a['href'].rsplit("=", 1)[1]) for a in pin.find_all('a', {'class': 'p'}))
    else:
        all_pages = 1
    for page in range(2, all_pages + 1):
        soup = BeautifulSoup(getter(base_url, params=(('page', page),)).content, 'html.parser')
        result.extend(soup.select(selector))
    return result


def multi_page_alt(getter, base_url, selector):
    result = []
    page = 1
    has_next_page = True
    while has_next_page:
        soup = BeautifulSoup(getter(base_url, params=(('page', page),)).content, 'html.parser')
        result.extend(soup.select(selector))
        if (pin := soup.select_one("div.page_inner")) is not None:
            has_next_page = (page + 1) in (int(a['href'].rsplit("=", 1)[1]) for a in pin.find_all('a', {'class': 'p'}))
        else:
            has_next_page = False
        page += 1
    return result
