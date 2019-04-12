import pytest
import requests

api_point = 'http://localhost:5000'

# present in first 100000 records of sample
player_id_test = '78e64bcc68cf45118f39fa71b24a1a80'

# not passing if cassandra db not populated
def test_complete_one():
    r = requests.get(api_point+'/complete_sessions/' + player_id_test)
    assert player_id_test in r.text

def test_complete_second():
    r = requests.get(api_point+'/complete_sessions/')
    assert r.status_code == 404

def test_complete_third():
    r = requests.get(api_point+'/complete_sessions/' + player_id_test[:15])
    assert r.status_code == 404

def test_complete_fourth():
    r = requests.get(api_point+'/complete_sessions/player-1234')
    assert r.status_code == 404

