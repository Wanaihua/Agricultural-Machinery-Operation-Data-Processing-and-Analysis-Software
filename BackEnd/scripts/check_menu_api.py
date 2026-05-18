import requests

for u in ('http://127.0.0.1:8000/api/menu/', 'http://127.0.0.1:8000/menu'):
    print('---', u)
    try:
        r = requests.get(u, timeout=10)
        print('status', r.status_code)
        print(r.text[:4000])
    except Exception as e:
        print('ERROR', e)
import requests

for u in ('http://127.0.0.1:8000/api/menu/', 'http://127.0.0.1:8000/menu'):
    print('---', u)
    try:
        r = requests.get(u, timeout=5)
        print('status:', r.status_code)
        print(r.text[:2000])
    except Exception as e:
        print('ERROR:', e)
