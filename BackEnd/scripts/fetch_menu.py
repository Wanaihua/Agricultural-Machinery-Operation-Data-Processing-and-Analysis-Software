import requests, json

def main():
    r = requests.get('http://127.0.0.1:8000/api/menu/')
    print('status', r.status_code)
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        print('response text:', r.text[:2000])

if __name__ == '__main__':
    main()
