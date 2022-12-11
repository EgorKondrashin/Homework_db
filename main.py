import psycopg2


def create_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS name_client(
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phone_client(
        "client_id" INTEGER NOT NULL REFERENCES name_client(client_id),
        phone VARCHAR(40)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS email_client(
        "client_id" INTEGER NOT NULL REFERENCES name_client(client_id),
        email VARCHAR(40) UNIQUE
    );
    """)


def add_client(cur, first_name, last_name, email, phones=None):
    cur.execute("""
    INSERT INTO name_client(first_name, last_name) VALUES(%s, %s) RETURNING client_id;
    """, (first_name, last_name, ))
    returning_id = cur.fetchone()[0]
    cur.execute("""
    INSERT INTO email_client(client_id, email) VALUES(%s, %s);
    """, (returning_id, email, ))
    cur.execute("""
    INSERT INTO phone_client(client_id, phone) VALUES(%s, %s);
    """, (returning_id, phones, ))


def add_phone(cur, client_id, phone):
    cur.execute("""
    INSERT INTO phone_client(client_id, phone) VALUES(%s, %s);
    """, (client_id, phone, ))


def change_client(cur, client_id, first_name=None, last_name=None, email=None, phones=None):
    if first_name is not None:
        cur.execute("""
        UPDATE name_client SET first_name=%s WHERE client_id=%s;
        """, (first_name, client_id, ))
    if last_name is not None:
        cur.execute("""
        UPDATE name_client SET last_name=%s WHERE client_id=%s;
        """, (last_name, client_id, ))
    if email is not None:
        cur.execute("""
        UPDATE email_client SET email=%s WHERE client_id=%s;
        """, (email, client_id, ))
    if phones is not None:
        cur.execute("""
        UPDATE phone_client SET phone=%s WHERE client_id=%s;
        """, (phones, client_id, ))


def delete_phone(cur, client_id, phone):
    cur.execute("""
    DELETE FROM phone_client WHERE client_id=%s AND phone=%s;
    """, (client_id, phone, ))


def delete_client(cur, client_id):
    cur.execute("""
    DELETE FROM phone_client WHERE client_id=%s;
    """, (client_id, ))
    cur.execute("""
    DELETE FROM email_client WHERE client_id=%s;
    """, (client_id, ))
    cur.execute("""
    DELETE FROM name_client WHERE client_id=%s;
    """, (client_id, ))


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if first_name is not None:
        if last_name is not None:
            if email is not None:
                if phone is not None:
                    cur.execute("""
                    SELECT client_id, first_name, last_name, phone, email FROM phone_client
                    JOIN name_client USING(client_id)
                    JOIN email_client USING(client_id)
                    WHERE first_name=%s AND last_name=%s AND email=%s AND phone=%s;
                    """, (first_name, last_name, email, phone,))
                    print(cur.fetchall())
                else:
                    cur.execute("""
                    SELECT client_id, first_name, last_name, email FROM name_client
                    JOIN email_client USING(client_id)
                    WHERE first_name=%s AND last_name=%s AND email=%s;
                    """, (first_name, last_name, email, ))
                    print(cur.fetchall())
            else:
                cur.execute("""
                SELECT client_id, first_name, last_name FROM name_client
                WHERE first_name=%s AND last_name=%s;
                """, (first_name, last_name, ))
                print(cur.fetchall())
        else:
            cur.execute("""
            SELECT client_id, first_name FROM name_client
            WHERE first_name=%s;
            """, (first_name, ))
            print(cur.fetchall())
    else:
        return


def delete_db(cur):
    cur.execute("""
    DROP TABLE email_client;
    DROP TABLE phone_client;
    DROP TABLE name_client;
    """)


if __name__ == "__main__":
    with psycopg2.connect(database="clients", user="postgres", password="") as conn:
        with conn.cursor() as cur:
            conn.commit()

    conn.close()
