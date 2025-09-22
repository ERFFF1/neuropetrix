import json

def handler(request):
    # Basit sağlık uç noktası (Vercel Python Function)
    body = {"neuropetrix": "online", "platform": "vercel", "service": "backend"}
    return {
        "status": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body)
    }
