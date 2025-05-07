from datetime import datetime
import mysql.connector
from mysql.connector import Error
import streamlit as st

def insert_dispute_submission(
    name, email, address, dob, ssn_last4,
    bureau, dispute_reasons, letter_date
):
    connection = None
    try:
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%m/%d/%Y").strftime("%Y-%m-%d")
        if isinstance(letter_date, str):
            letter_date = datetime.strptime(letter_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        connection = mysql.connector.connect(
            host=st.secrets["MYSQL_HOST"],
            port=int(st.secrets["MYSQL_PORT"]),
            user=st.secrets["MYSQL_USER"],
            password=st.secrets["MYSQL_PASSWORD"],
            database=st.secrets["MYSQL_DATABASE"]
        )

        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO dispute_submissions (
                name, email, address, dob, ssn_last4,
                bureau, dispute_reasons, letter_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                name, email, address, dob, ssn_last4,
                bureau, dispute_reasons, letter_date
            ))
            connection.commit()
            return True

    except Error as e:
        st.error(f"MySQL Error: {e}")
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def create_dispute_table():
    try:
        connection = mysql.connector.connect(
            host=st.secrets["MYSQL_HOST"],
            port=int(st.secrets["MYSQL_PORT"]),
            user=st.secrets["MYSQL_USER"],
            password=st.secrets["MYSQL_PASSWORD"],
            database=st.secrets["MYSQL_DATABASE"]
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS dispute_submissions")

            create_query = """
            CREATE TABLE dispute_submissions (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT,
                dob DATE,
                ssn_last4 TEXT,
                bureau TEXT,
                dispute_reasons TEXT,
                letter_date DATE,
                created_at DATE DEFAULT CURRENT_DATE
            )
            """
            cursor.execute(create_query)
            connection.commit()
            st.success("Table created successfully!")

    except Error as e:
        st.error(f"MySQL Error: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

