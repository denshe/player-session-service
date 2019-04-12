CREATE KEYSPACE session WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
CREATE TABLE session.start (
   session_id uuid,
   player_id varchar,
   country varchar,
   ts timestamp,
   PRIMARY KEY ((player_id),ts)
) WITH CLUSTERING ORDER BY (ts DESC);

CREATE TABLE session.end (
   session_id uuid,
   player_id varchar,
   ts timestamp,
   PRIMARY KEY ((player_id),ts)
) WITH CLUSTERING ORDER BY (ts DESC);
