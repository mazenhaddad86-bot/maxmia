import curl_cffi.requests as req, json

t = open('hf_token.txt', encoding='utf-8-sig').read().strip()
c = open('hf_client.txt', encoding='utf-8-sig').read().strip()
headers = {'Authorization': 'Bearer ' + t}
cookies = {'__client': c, '__client_uat': '1778964580'}

# Try the reference job directly
r = req.get('https://fnf.higgsfield.ai/jobs/93e62bf9-9794-44cb-82d5-084133a49fa6',
            headers=headers, cookies=cookies, impersonate='chrome120')
print('Ref job status:', r.status_code)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:2000])

# Also get all jobs to find Max & Mia images
r2 = req.get('https://fnf.higgsfield.ai/jobs?page=1&per_page=50',
             headers=headers, cookies=cookies, impersonate='chrome120')
print('\nAll jobs:')
jobs = r2.json().get('jobs', [])
for j in jobs:
    t2 = j.get('job_set_type', '')
    result = j.get('result') or {}
    url = result.get('url', '')
    jid = j.get('job_set_id', '')
    print(f'  {t2} | id:{jid[:8]} | url:{url[:70]}')
