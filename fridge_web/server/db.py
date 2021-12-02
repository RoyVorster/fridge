import psycopg2


with open('db_conn', 'r') as f:
    CONN = f.readline().strip()


def exec_query(query, values=()):
    with psycopg2.connect(CONN) as conn:
        cur, data = conn.cursor(), []

        try:
            cur.execute(query, values)
            data = cur.fetchall()
            conn.commit()
        except:
            pass
        finally:
            cur.close()

        return data

def init_db():
    check_query = '''SELECT schema_name FROM information_schema.schemata'''
    res = [r[0] for r in exec_query(check_query)]

    if 'fridge' not in res:
        init_query = '''
            CREATE SCHEMA fridge;
            CREATE TABLE IF NOT EXISTS fridge.sensors (
                id INTEGER PRIMARY KEY,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS fridge.data (
                time TIMESTAMP NOT NULL,
                data FLOAT,
                sensor_id INTEGER REFERENCES fridge.sensors (id),
                UNIQUE (time, sensor_id)
            );
            SELECT create_hypertable('fridge.data', 'time');
            INSERT INTO fridge.sensors VALUES (0, 'Temperature MPC9808');
        '''

        exec_query(init_query)

if __name__ == '__main__':
    init_db()
