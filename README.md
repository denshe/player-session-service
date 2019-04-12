# player-session-service

Service functionaluty:
* API for receiving event batches (1-100000 events / batch)
* API for fetching session starts for the last X (X is defined by the user) hours for each country
* API for fetching last (up to twenty) complete sessions for a given player
* Data older than one year is discarded

### Implementation details
* One node Cassandra cluster is run as docker container: `docker run -e DS_LICENSE=accept --memory 4g --name my-dse -d datastax/dse-server -p 9042:9042`
* API is implemented as Flask app, see 'app.py'
* Data modelling is as follows: start and end session events go to tables 'session.start' and 'session.end'
    * partitioning done by 'player_id'
    * 'ts' is used as clustering column, so given player_id records are sorted by 'ts' in a such way that those with latest 'ts' go first
* No data is deleted from Cassandra. Discarding one year old (and older) happens in the app (records' timstamps are checked and discard if older than one year)
* As provided dataset covering November 2016, 'current' datetime is set to 2016-12-01


### Starting service
1. Start Cassandra: `docker run -e DS_LICENSE=accept --memory 4g --name my-dse -d datastax/dse-server -p 9042:9042sudo do`
2. Create data schema in Cassandra (keyspace and two tables 'start' and 'event'): `docker cp schema.cql my-dse:schema.cql; docker exec -it my-dse bin/cqlsh -f /schema.cql`
3. (Optionally) Start Datastax Studio: `docker run -e DS_LICENSE=accept --link my-dse -p 9091:9091 --memory 1g --name my-studio -d datastax/dse-studio`
4. Copy full dataset to 'raw' folder (in this repo the file includes 100000 events)
5. Start API server: `python app.py`
6. Add events to Cassandra by multiple calls to API: `curl -i http://localhost:5000/add/100`
7. API testing (in tests/ dir) is provided. To test: `pytest` (one test may not pass if db not populated)

### API requests
##### Add events: 
`curl -i http://localhost:5000/add/10`
>HTTP/1.0 200 OK
>Content-Type: text/html; charset=utf-8
>...

>10 events have been added

##### Fetch session starts
`curl -i http://localhost:5000/fetch/FI/4`
>HTTP/1.0 200 OK
>Content-Type: text/html; charset=utf-8
>...

>2016-11-30 23:56:24 ; 2016-11-30 22:40:07 ; 2016-11-30 19:26:40 ; 2016-11-30 17:51:51 ; 2016-11-30 17:39:46

##### Fetch last 20 complete sessions
`curl -i http://localhost:5000/complete_sessions/2a279b9197da4a2cb7578fce45c63b2c`
>HTTP/1.0 200 OK
>Content-Type: text/html; charset=utf-8
>...

>[{'player_id': '3e20991caf5947f78373f63178fa90de', 'session_id': '494ce55a-d209-4023-b3c2-145078607968', 'session_end': '2016-11-06 02:43:23', 'session_start': '2016-11-06 02:35:22', 'country': 'EE'}, {'player_id': '3e20991caf5947f78373f63178fa90de', 'session_id': '47aaf37e-986e-4803-92ed-657be5759080', 'session_end': '2016-11-04 04:50:08', 'session_start': '2016-11-04 03:03:18', 'country': 'EE'}]

### Notes
* To scale: add nodes to Cassandra cluster; add one/more app servers (running Flask)
* Fetching last twenty sessions can be improved by combining twenty requests for sessions into one
