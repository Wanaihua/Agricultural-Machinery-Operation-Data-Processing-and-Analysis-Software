import requests

urls = [
    'http://127.0.0.1:8000/api/track/',
    'http://127.0.0.1:8000/api/track/1/',
    'http://127.0.0.1:8000/api/track/1/trackpoints/',
]

for u in urls:
    print('---', u)
    try:
        r = requests.get(u, timeout=10)
        print('status:', r.status_code)
        text = r.text
        if len(text) > 4000:
            print(text[:4000])
            print('... (truncated)')
        else:
            print(text)
    except Exception as e:
        print('ERROR:', e)
