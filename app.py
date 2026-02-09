from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row
from config import Config
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Database connection function
def get_db_connection():
    conn = psycopg.connect(
        host=Config.DB_HOST,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        row_factory=dict_row,
    )
    return conn


# Helper function to check and level up employee
def check_and_level_up(employee_id, conn):
    """Check if employee should level up based on current XP"""
    cur = conn.cursor()

    # Get employee's current XP and level
    cur.execute(
        "SELECT total_xp, current_level FROM employees WHERE id = %s", (employee_id,)
    )
    employee = cur.fetchone()

    if not employee:
        return False

    current_xp = employee["total_xp"]
    current_level = employee["current_level"]

    # Find the highest level they qualify for
    cur.execute(
        """
        SELECT level_number 
        FROM levels 
        WHERE xp_required <= %s 
        ORDER BY level_number DESC 
        LIMIT 1
    """,
        (current_xp,),
    )

    result = cur.fetchone()
    new_level = result["level_number"] if result else 1

    # Update if they leveled up
    if new_level > current_level:
        cur.execute(
            "UPDATE employees SET current_level = %s WHERE id = %s",
            (new_level, employee_id),
        )
        conn.commit()
        cur.close()
        return True

    cur.close()
    return False


# Home endpoint
@app.route("/")
def home():
    return jsonify(
        {
            "message": "Welcome to LevelUp API",
            "version": "0.3.0",
            "endpoints": {
                "GET /employees": "Get all employees",
                "POST /employees": "Create new employee",
                "GET /employees/<id>": "Get specific employee",
                "GET /employees/<id>/tasks": "Get employee's task history",
                "POST /tasks": "Log a completed task",
                "GET /leaderboard": "Get global leaderboard",
                "GET /leaderboard/<department>": "Get department leaderboard",
                "GET /stats": "Get system statistics",
            },
        }
    )


# Get all employees
@app.route("/employees", methods=["GET"])
def get_employees():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                e.id, 
                e.name, 
                e.email, 
                e.department, 
                e.current_level, 
                e.total_xp,
                l.rank_title
            FROM employees e
            JOIN levels l ON e.current_level = l.level_number
            ORDER BY e.total_xp DESC
        """)
        employees = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(employees)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create new employee
@app.route("/employees", methods=["POST"])
def create_employee():
    try:
        data = request.get_json()

        if not data.get("name") or not data.get("email"):
            return jsonify({"error": "Name and email are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO employees (name, email, department, hire_date)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, email, department, current_level, total_xp
        """,
            (
                data["name"],
                data["email"],
                data.get("department", "General"),
                data.get("hire_date", datetime.now().date()),
            ),
        )

        new_employee = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify(new_employee), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get specific employee
@app.route("/employees/<int:employee_id>")
def get_employee(employee_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                e.id, 
                e.name, 
                e.email, 
                e.department, 
                e.hire_date,
                e.current_level, 
                e.total_xp,
                l.rank_title,
                l.xp_required
            FROM employees e
            JOIN levels l ON e.current_level = l.level_number
            WHERE e.id = %s
        """,
            (employee_id,),
        )
        employee = cur.fetchone()
        cur.close()
        conn.close()

        if employee:
            return jsonify(employee)
        else:
            return jsonify({"error": "Employee not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create task
@app.route("/tasks", methods=["POST"])
def create_task():
    try:
        data = request.get_json()

        if not data.get("employee_id") or not data.get("task_name"):
            return jsonify({"error": "employee_id and task_name are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        quality_score = float(data.get("quality_score", 3.0))
        was_on_time = data.get("was_on_time", True)

        base_xp = 10
        quality_multiplier = quality_score / 2.5
        punctuality_multiplier = 1.5 if was_on_time else 1.0
        xp_earned = int(base_xp * quality_multiplier * punctuality_multiplier)

        cur.execute(
            """
            INSERT INTO tasks 
            (employee_id, task_name, completion_date, quality_score, xp_earned, status, was_on_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, employee_id, task_name, xp_earned
        """,
            (
                data["employee_id"],
                data["task_name"],
                datetime.now(),
                quality_score,
                xp_earned,
                "completed",
                was_on_time,
            ),
        )

        new_task = cur.fetchone()

        cur.execute(
            """
            UPDATE employees 
            SET total_xp = total_xp + %s 
            WHERE id = %s
        """,
            (xp_earned, data["employee_id"]),
        )

        conn.commit()

        leveled_up = check_and_level_up(data["employee_id"], conn)

        cur.close()
        conn.close()

        response = {"task": new_task, "xp_earned": xp_earned, "leveled_up": leveled_up}

        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get leaderboard
@app.route("/leaderboard")
def get_leaderboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                e.id,
                e.name, 
                e.department,
                e.current_level, 
                e.total_xp,
                l.rank_title,
                RANK() OVER (ORDER BY e.total_xp DESC) as rank
            FROM employees e
            JOIN levels l ON e.current_level = l.level_number
            ORDER BY e.total_xp DESC
        """)
        leaderboard = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get employee's task history
@app.route("/employees/<int:employee_id>/tasks")
def get_employee_tasks(employee_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                id,
                task_name,
                completion_date,
                quality_score,
                xp_earned,
                status,
                was_on_time
            FROM tasks
            WHERE employee_id = %s
            ORDER BY completion_date DESC
        """,
            (employee_id,),
        )
        tasks = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get leaderboard filtered by department
@app.route("/leaderboard/<department>")
def get_department_leaderboard(department):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                e.id,
                e.name, 
                e.department,
                e.current_level, 
                e.total_xp,
                l.rank_title,
                RANK() OVER (ORDER BY e.total_xp DESC) as rank
            FROM employees e
            JOIN levels l ON e.current_level = l.level_number
            WHERE e.department = %s
            ORDER BY e.total_xp DESC
        """,
            (department,),
        )
        leaderboard = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get statistics overview
@app.route("/stats")
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Total employees
        cur.execute("SELECT COUNT(*) as total FROM employees")
        total_employees = cur.fetchone()["total"]

        # Total tasks completed
        cur.execute("SELECT COUNT(*) as total FROM tasks WHERE status = 'completed'")
        total_tasks = cur.fetchone()["total"]

        # Average XP per employee
        cur.execute("SELECT AVG(total_xp) as avg_xp FROM employees")
        avg_xp = round(cur.fetchone()["avg_xp"] or 0, 2)

        # Top performer
        cur.execute("""
            SELECT name, total_xp 
            FROM employees 
            ORDER BY total_xp DESC 
            LIMIT 1
        """)
        top_performer = cur.fetchone()

        # Department breakdown
        cur.execute("""
            SELECT department, COUNT(*) as count, AVG(total_xp) as avg_xp
            FROM employees
            GROUP BY department
            ORDER BY avg_xp DESC
        """)
        departments = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(
            {
                "total_employees": total_employees,
                "total_tasks_completed": total_tasks,
                "average_xp": avg_xp,
                "top_performer": top_performer,
                "departments": departments,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
