import requests

for role_id in (1,):
    try:
        r = requests.get(f'http://127.0.0.1:8000/role/roleMenu/{role_id}')
        print(role_id, r.status_code, r.text)
    except Exception as e:
        print('ERROR', e)
