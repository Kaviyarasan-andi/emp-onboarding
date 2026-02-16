from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)


# -----------------------------------
# Database Connection Function
# -----------------------------------
def get_db_connection():
    try:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise Exception("DATABASE_URL not found in environment variables")

        connection = psycopg2.connect(
            database_url,
            sslmode="require"
        )

        return connection

    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# -----------------------------------
# Helper: Convert rows to dict
# -----------------------------------
def fetch_all_as_dict(cursor):
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


# -----------------------------------
# HOME ROUTE
# -----------------------------------
@app.route('/')
def home():
    return jsonify({"message": "Employee API is running successfully"})


# -----------------------------------
# GET ALL EMPLOYEES
# -----------------------------------
@app.route('/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY emp_id")
        employees = fetch_all_as_dict(cursor)
        return jsonify(employees)

    except Exception as e:
        print("❌ Fetch error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# ADD EMPLOYEE
# -----------------------------------
@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON input"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO employees
        (first_name, last_name, department, salary, email, phone_number,
         date_of_birth, address, employment_type, date_of_joining)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('first_name'),
            data.get('last_name'),
            data.get('department'),
            data.get('salary'),
            data.get('email'),
            data.get('phone_number'),
            data.get('date_of_birth'),
            data.get('address'),
            data.get('employment_type'),
            data.get('date_of_joining')
        )

        cursor.execute(query, values)
        conn.commit()

        return jsonify({"message": "Employee added successfully"}), 201

    except Exception as e:
        print("❌ Insert error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# UPDATE EMPLOYEE
# -----------------------------------
@app.route('/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    data = request.get_json()

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        query = """
        UPDATE employees SET
        first_name=%s,
        last_name=%s,
        department=%s,
        salary=%s,
        email=%s,
        phone_number=%s,
        date_of_birth=%s,
        address=%s,
        employment_type=%s,
        date_of_joining=%s
        WHERE emp_id=%s
        """

        values = (
            data.get('first_name'),
            data.get('last_name'),
            data.get('department'),
            data.get('salary'),
            data.get('email'),
            data.get('phone_number'),
            data.get('date_of_birth'),
            data.get('address'),
            data.get('employment_type'),
            data.get('date_of_joining'),
            emp_id
        )

        cursor.execute(query, values)
        conn.commit()

        return jsonify({"message": "Employee updated successfully"})

    except Exception as e:
        print("❌ Update error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# DELETE EMPLOYEE
# -----------------------------------
@app.route('/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE emp_id = %s", (emp_id,))
        conn.commit()

        return jsonify({"message": "Employee deleted successfully"})

    except Exception as e:
        print("❌ Delete error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# RUN APP (Production Ready for Render)
# -----------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
