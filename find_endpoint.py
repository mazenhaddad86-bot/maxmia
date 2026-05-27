import curl_cffi.requests as req, re

r = req.get('https://higgsfield.ai/ai/image', impersonate='chrome120')
js_urls = re.findall(r'/_next/static/chunks/[^"]+\.js', r.text)

for url in js_urls:
    full_url = 'https://higgsfield.ai' + url
    try:
        js = req.get(full_url, impersonate='chrome120', timeout=10)
        text = js.text
        if 'nano-banana-pro' in text or 'nano_banana_pro' in text:
            print(f'\n=== FOUND in {url.split("/")[-1]} ===')
            # Show 300 chars of context around each hit
            for m in re.finditer(r'.{0,200}nano.banana.pro.{0,200}', text):
                print(m.group())
                print('---')
    except:
        pass
