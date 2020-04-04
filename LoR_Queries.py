import requests

def cards():
    url = "http://127.0.0.1:21337/positional-rectangles"
    try:
        r = requests.get(url = url)
        return r.json()
    except:
        return None
    return None