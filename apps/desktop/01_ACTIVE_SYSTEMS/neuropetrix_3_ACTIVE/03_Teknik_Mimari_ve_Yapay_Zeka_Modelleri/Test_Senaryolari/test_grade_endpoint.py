import requests, pytest, time
BASE = "http://127.0.0.1:8000"
def test_health():
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
def test_grade_score():
    payload = {"title":"Systematic review","abstract":"Randomized controlled.","keywords":["meta-analysis"]}
    r = requests.post(f"{BASE}/grade/score", json=payload, timeout=10)
    assert r.status_code == 200
    js = r.json()
    assert js["rank"] >= 5
