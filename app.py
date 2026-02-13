from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)   # ✅ IMPORTANT FOR REACT


# -----------------------------------
# Database Connection Function
# -----------------------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mindz@123",
            database="emp_onboarding"
        )
        return connection
    except Error as e:
        print("Database connection error:", e)
        return None


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
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        return jsonify(employees)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# GET EMPLOYEE BY ID
# -----------------------------------
@app.route('/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees WHERE emp_id = %s", (emp_id,))
        employee = cursor.fetchone()

        if employee:
            return jsonify(employee)
        else:
            return jsonify({"message": "Employee not found"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# FILTER BY DEPARTMENT
# -----------------------------------
@app.route('/employees/department/<string:dept>', methods=['GET'])
def get_by_department(dept):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees WHERE department = %s", (dept,))
        result = cursor.fetchall()
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# PAGINATION
# -----------------------------------
@app.route('/employees/page', methods=['GET'])
def get_paginated():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    offset = (page - 1) * limit

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees LIMIT %s OFFSET %s", (limit, offset))
        result = cursor.fetchall()
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# ADD NEW EMPLOYEE
# -----------------------------------
@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON input"}), 400

    required_fields = ["first_name", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

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

    except Error as e:
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

    if not data:
        return jsonify({"error": "Invalid JSON input"}), 400

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

        if cursor.rowcount == 0:
            return jsonify({"message": "Employee not found"}), 404

        return jsonify({"message": "Employee updated successfully"})

    except Error as e:
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

        if cursor.rowcount == 0:
            return jsonify({"message": "Employee not found"}), 404

        return jsonify({"message": "Employee deleted successfully"})

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------------------------
# RUN APPLICATION
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
