import pytest
import requests

api_point = 'http://localhost:5000'

def test_batch_one():
    r = requests.get(api_point+'/add/20')
    assert r.content == b'20 events have been added'

def test_batch_second():
    r = requests.get(api_point+'/add/100')
    assert r.content == b'100 events have been added'

def test_batch_third():
    r = requests.get(api_point+'/add/-10')
    assert r.status_code == 404

def test_batch_fourth():
    r = requests.get(api_point+'/add/twenty')
    assert r.status_code == 404

def test_batch_fifth():
    r = requests.get(api_point+'/add')
    assert r.status_code == 404
