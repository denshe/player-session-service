from flask import Flask
from flask import abort
from itertools import islice 
from cassandra.cluster import Cluster 
from datetime import datetime,timedelta

# connect to Cassandra (run locally)
cassandra_hosts = ['172.17.0.2']
cluster = Cluster(cassandra_hosts)
data_schema = 'session'
session = cluster.connect(data_schema)


# to make fetching work on data in the sample (covering November of 2016), 
# 'current' datetime is set to 2016-12-01
dt_cur = datetime(2016, 12, 1, 0, 0)


# session events are read from the file in batches; simulates stream of player session events
def next_n_lines(file_opened, N):
    return [x.strip() for x in islice(file_opened, N)]  
g = open("raw/player_session_sample.json", 'r')

app = Flask(__name__)

# API specification can be provided here
@app.route('/')
def index():
    return 'Player Sessions app\nAPI:...'

# implements API for receiving event batches (1-100000 events / batch)
@app.route('/add/<int:num_sessions>', methods=['GET'])
def add_sessions(num_sessions):
    # error if more than 10 or less than 1 events requested
    if num_sessions<1 or num_sessions>100000:
        abort(404)
    # read datafile 'player_session_sample.json' in 'raw' dir and insert event to corresponding table, 
    # either 'start' or 'event'
    # ! reads from where it stopped at the previous call, no reading once reaches the end of file 
    for el in next_n_lines(g, num_sessions):
        r = eval(el)
        event_table_name = r.pop('event',None)
        insert_st = "INSERT INTO " + event_table_name + " JSON '" + str(r).replace("'", '"') + "';"
        # print(insert_st)
        session.execute(insert_st)
    return str(num_sessions) + " events have been added"

# implements API for fetching session starts for the last X (X is defined by the user) hours for each country
@app.route('/fetch/<country_name>/<int:num_hours>', methods=['GET'])
def fetch_session_starts(country_name,num_hours):
    # num-hours should be positive
    if num_hours<0:
        abort(404)
    dt_lastXhours = dt_cur - timedelta(hours=num_hours)
    fetch_st = "SELECT ts FROM {} WHERE country='{}' and ts<='{}' and ts>'{}' ALLOW FILTERING;".format('start', country_name, dt_cur.strftime('%Y-%m-%d %H:%M:%S'), dt_lastXhours.strftime('%Y-%m-%d %H:%M:%S')) 
    # print(fetch_st)
    rows = session.execute(fetch_st)
    r = []
    for row in rows:
        session_start = row.ts
        # leave start sessions only if not older than one year
        if session_start > dt_cur - timedelta(days=365):
            r.append(session_start.strftime('%Y-%m-%d %H:%M:%S'))
    return ' ; '.join(r)

# implements API for fetching up to last twenty complete sessions for a given player
@app.route('/complete_sessions/<player_id>', methods=['GET'])
def fetch_complete_sessions(player_id):
    # checks if provided string corresponds to format used for playerIDs
    if len(player_id)<32:
        abort(404)
    # get last X session end events for a given player; X>20 as some end events may have no matching start events or 
    # started earlier than one year ago
    X = 25  
    fetch_lastX = "SELECT player_id,session_id,ts FROM {} WHERE player_id='{}' LIMIT {} ALLOW FILTERING;".format('end', player_id, X) 
    # complete sessions: with start and end session events in db which both timestamps not older than one year
    sessions = []
    rows = session.execute(fetch_lastX)    
    for row in rows:
        r = {}
        r['player_id'] = str(row.player_id)
        r['session_id'] = str(row.session_id)
        r['session_end'] = str(row.ts)
        # get details for session start
        sstart_query = "SELECT country,ts FROM {} WHERE session_id={} ALLOW FILTERING;".format('start', row.session_id)
        sstart_res = session.execute(sstart_query)
        if len(sstart_res.current_rows):
            # checks whether session start is not older than one year calculated based on 'current' datetime defined above 
            if sstart_res[0].ts > dt_cur - timedelta(days=365):
                r['session_start'] = str(sstart_res[0].ts)
                r['country'] = sstart_res[0].country
                sessions.append(r)
    # leave only 20 sessions if more than 20 found 
    if len(sessions)>20:
        sessions = sessions[:20]
    return str(sessions)

if __name__ == '__main__':
    app.run(debug=True)
