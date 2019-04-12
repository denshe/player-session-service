import pytest
import requests

api_point = 'http://localhost:5000'

def test_fetch_one():
    r = requests.get(api_point+'/fetch/FI/0')
    assert r.content == b''

def test_fetch_second():
    r = requests.get(api_point+'/fetch/XXXX/10')
    assert r.content == b''

def test_fetch_third():
    r = requests.get(api_point+'/fetch/1.5')
    assert r.status_code == 404

def test_fetch_fourth():
    r = requests.get(api_point+'/fetch/20')
    assert r.status_code == 404

def test_fetch_fifth():
    r = requests.get(api_point+'/fetch/FI')
    assert r.status_code == 404
