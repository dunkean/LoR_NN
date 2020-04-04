import requests

def is_available():
    url = "http://127.0.0.1:21337/positional-rectangles"
    try:
        requests.get(url = url)
        return True
    except:
        return False
    return False