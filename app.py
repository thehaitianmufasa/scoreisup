from datetime import datetime
import mysql.connector
from mysql.connector import Error
import streamlit as st
import bcrypt

# 🚀 Insert dispute submission
def insert_dispute_submission(
    name, email, address, dob, ssn_last4,
    bureau, dispute_reasons, letter_date
):
    try:
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%m/%d/%Y").strftime("%Y-%m-%d")
        if isinstance(letter_date, str):
            letter_date = datetime.strptime(letter_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        connection = mysql.connector.connect(
            host=st.secrets["MYSQLHOST"],
            port=int(st.secrets["MYSQLPORT"]),
            user=st.secrets["MYSQLUSER"],
            password=st.secrets["MYSQLPASSWORD"],
            database=st.secrets["MYSQLDATABASE"]
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
        st.error(f"MySQL Error (Insert Dispute): {e}")
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# 🔐 Insert a new user account
def insert_user(email, password):
    try:
        connection = mysql.connector.connect(
            host=st.secrets["MYSQLHOST"],
            port=int(st.secrets["MYSQLPORT"]),
            user=st.secrets["MYSQLUSER"],
            password=st.secrets["MYSQLPASSWORD"],
            database=st.secrets["MYSQLDATABASE"]
        )

        if connection.is_connected():
            cursor = connection.cursor()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            insert_query = """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(insert_query, (email, password_hash))
            connection.commit()
            return True

    except Error as e:
        st.error(f"MySQL Error (Insert User): {e}")
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# 🔍 Fetch user by email
def get_user_by_email(email):
    try:
        connection = mysql.connector.connect(
            host=st.secrets["MYSQLHOST"],
            port=int(st.secrets["MYSQLPORT"]),
            user=st.secrets["MYSQLUSER"],
            password=st.secrets["MYSQLPASSWORD"],
            database=st.secrets["MYSQLDATABASE"]
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT id, email, password_hash FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result

    except Error as e:
        st.error(f"MySQL Error (Get User): {e}")
        return None

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

