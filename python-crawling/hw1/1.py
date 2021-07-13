import requests
import json

def get_data(category):
    by_request = 120
    page = 1
    url = "https://5ka.ru/api/v2/special_offers/?store=&records_per_page={}&page={}&categories={}&ordering=&price_promo__gte=&price_promo__lte=&search=".format(
            by_request, page, category
        )
    results = []
    new_results = True
    while new_results:
        req = requests.get(url)
        res = req.json()['results']
        url = req.json()['next']
        # print(req.json())
        if not res or url is None:
            new_results = False
        else:
            results += res

    return results

def get_categories():
    url = "https://5ka.ru/api/v2/categories/"
    req = requests.get(url)
    categories = req.json()
    return  categories

for category in get_categories():
    category_code = category['parent_group_code']
    data = get_data(category_code)

    with open('%s.json' % category_code, 'w') as f:
        json.dump(data, f)