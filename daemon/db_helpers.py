import psycopg2

CONNECTION = 'postgres://rvorster:secret@localhost:5432/rvorster'

def execute_query(query, values=()):
    with psycopg2.connect(CONNECTION) as conn:
        cur = conn.cursor()
        cur.execute(query, values)
        data = cur.fetchall()

        conn.commit()
        cur.close()
        return data

def init_db():
    query = '''
        CREATE TABLE IF NOT EXISTS fridge_sensors (
            sensor_id INTEGER PRIMARY KEY,
            sensor_descr TEXT
        );

        CREATE TABLE IF NOT EXISTS fridge_data (
            sensor_id INTEGER REFERENCES fridge_sensors (sensor_id),
            time TIMESTAMP NOT NULL,
            data DOUBLE PRECISION,
            UNIQUE (time, sensor_id)
        );

        SELECT create_hypertable('fridge_data', 'time');

        INSERT INTO fridge_sensors VALUES (0, 'Temperature');
    '''

    execute_query(query);

if __name__ == '__main__':
    init_db()
