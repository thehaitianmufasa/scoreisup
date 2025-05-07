
import mysql.connector
from mysql.connector import Error

def insert_dispute_submission(
    name, email, address, dob, ssn_last4,
    bureau, dispute_reasons, letter_date
):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Paysoz991@#',
            database='credit_app'
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
        print(f"❌ MySQL Error: {e}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
