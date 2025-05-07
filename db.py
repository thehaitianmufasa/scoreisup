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
        # Ensure dates are not None
        if not dob or not letter_date:
            st.error("Date of Birth and Letter Date must be provided.")
            return False

        # Convert MM/DD/YYYY to YYYY-MM-DD
        dob = datetime.strptime(dob, "%m/%d/%Y").strftime("%Y-%m-%d")
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
