import os
import datetime
from typing import Dict, List, Optional, Union, Any

import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest, NotFound
from flask_cors import CORS  # You'll need to install this package


load_dotenv()
app = Flask(__name__)
CORS(app)
# Database connection parameters
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_db_connection():
    """Create and return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)


def validate_sale_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and process sale data for insertion/update"""
    errors = []

    # Required fields
    required_fields = ["cash_type", "card", "money", "coffee_name"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        raise BadRequest({"errors": errors})

    # Process and validate fields
    processed_data = {
        "cash_type": data["cash_type"],
        "card": data["card"],
        "money": float(data["money"]) if isinstance(data["money"], (str, int)) else data["money"],
        "coffee_name": data["coffee_name"],
        # Datetime will be generated if not provided
        "datetime": data.get("datetime", datetime.datetime.now().isoformat())
    }

    # Additional validation
    if not isinstance(processed_data["money"], (int, float)):
        errors.append("Money must be a number")

    if errors:
        raise BadRequest({"errors": errors})

    return processed_data


@app.route('/add_student/api/sales', methods=['GET'])
def get_sales():
    """Get all sales or filter by query parameters"""
    # Extract query parameters
    coffee_name = request.args.get('coffee_name')
    date = request.args.get('date')
    card = request.args.get('card')

    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            query = "SELECT * FROM tbl_javohir_sales"
            params = []
            conditions = []

            # Add filters if provided
            if coffee_name:
                conditions.append("coffee_name = %s")
                params.append(coffee_name)

            if date:
                conditions.append("DATE(datetime) = %s")
                params.append(date)

            if card:
                conditions.append("card = %s")
                params.append(card)

            # Build WHERE clause if needed
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Add ordering to ensure consistent results
            query += " ORDER BY datetime DESC"

            cur.execute(query, params)
            sales = [dict(row) for row in cur.fetchall()]

            return jsonify({
                "success": True,
                "data": sales,
                "count": len(sales)
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/add_student/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    """Get a single sale by ID"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM tbl_javohir_sales WHERE id = %s", (sale_id,))
            sale = cur.fetchone()

            if not sale:
                return jsonify({
                    "success": False,
                    "error": f"Sale with ID {sale_id} not found"
                }), 404

            return jsonify({
                "success": True,
                "data": dict(sale)
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/add_student/api/sales', methods=['POST'])
def add_sale():
    """Add a new sale record"""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    try:
        # Validate data
        validated_data = validate_sale_data(data)

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Generate current datetime if not provided
            if "datetime" not in validated_data:
                validated_data["datetime"] = datetime.datetime.now()

            # Insert data
            cur.execute(
                """
                INSERT INTO tbl_javohir_sales
                    (datetime, cash_type, card, money, coffee_name)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
                """,
                (
                    validated_data["datetime"],
                    validated_data["cash_type"],
                    validated_data["card"],
                    validated_data["money"],
                    validated_data["coffee_name"]
                )
            )
            new_id = cur.fetchone()[0]
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Sale added successfully",
                "id": new_id
            }), 201
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/add_student/api/sales/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    """Update an existing sale record"""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    try:
        # Validate data
        validated_data = validate_sale_data(data)

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if record exists
            cur.execute("SELECT 1 FROM tbl_javohir_sales WHERE id = %s", (sale_id,))
            if not cur.fetchone():
                return jsonify({
                    "success": False,
                    "error": f"Sale with ID {sale_id} not found"
                }), 404

            # Update record
            cur.execute(
                """
                UPDATE tbl_javohir_sales
                SET datetime    = %s,
                    cash_type   = %s,
                    card        = %s,
                    money       = %s,
                    coffee_name = %s
                WHERE id = %s
                """,
                (
                    validated_data["datetime"],
                    validated_data["cash_type"],
                    validated_data["card"],
                    validated_data["money"],
                    validated_data["coffee_name"],
                    sale_id
                )
            )
            conn.commit()

            return jsonify({
                "success": True,
                "message": f"Sale with ID {sale_id} updated successfully"
            })
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/add_student/api/sales/delete-by-date', methods=['DELETE'])
def delete_sale_by_datetime():
    """Delete a sale record based on datetime"""
    try:
        # Get the datetime from request parameters
        sale_date = request.args.get('datetime')

        if not sale_date:
            return jsonify({
                "success": False,
                "error": "Missing datetime parameter"
            }), 400

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if record exists with the given datetime
            cur.execute("SELECT id FROM tbl_javohir_sales WHERE sale_date = %s", (sale_date,))
            records = cur.fetchall()

            if not records:
                return jsonify({
                    "success": False,
                    "error": f"No sales found with datetime {sale_date}"
                }), 404

            # Delete record(s) with the given datetime
            cur.execute("DELETE FROM tbl_javohir_sales WHERE sale_date = %s", (sale_date,))
            deleted_count = cur.rowcount
            conn.commit()

            return jsonify({
                "success": True,
                "message": f"{deleted_count} sale(s) with datetime {sale_date} deleted successfully"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()
@app.route('/add_student/api/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    """Delete a sale record"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if record exists
            cur.execute("SELECT 1 FROM tbl_javohir_sales WHERE id = %s", (sale_id,))
            if not cur.fetchone():
                return jsonify({
                    "success": False,
                    "error": f"Sale with ID {sale_id} not found"
                }), 404

            # Delete record
            cur.execute("DELETE FROM tbl_javohir_sales WHERE id = %s", (sale_id,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": f"Sale with ID {sale_id} deleted successfully"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/add_student/api/sales/bulk', methods=['POST'])
def bulk_add_sales():
    """Add multiple sale records in a single request"""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "success": False,
            "error": "Request must be a JSON array of sale objects"
        }), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            inserted_ids = []

            for item in data:
                # Validate each item
                validated_item = validate_sale_data(item)

                # Insert data
                cur.execute(
                    """
                    INSERT INTO tbl_javohir_sales
                        (datetime, cash_type, card, money, coffee_name)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """,
                    (
                        validated_item["datetime"],
                        validated_item["cash_type"],
                        validated_item["card"],
                        validated_item["money"],
                        validated_item["coffee_name"]
                    )
                )
                inserted_ids.append(cur.fetchone()[0])

            conn.commit()

            return jsonify({
                "success": True,
                "message": f"Added {len(inserted_ids)} sales records",
                "ids": inserted_ids
            }), 201
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

# Fix for get_coffee_stats() function in the backend
@app.route('/add_student/api/stats/coffee', methods=['GET'])
def get_coffee_stats():
    """Get statistics about coffee sales"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get counts and totals by coffee type
            # Add CAST to ensure money is treated as numeric
            cur.execute("""
                SELECT 
                    coffee_name,
                    COUNT(*) as count,
                    SUM(CAST(money AS NUMERIC)) as total_sales
                FROM tbl_javohir_sales
                GROUP BY coffee_name
                ORDER BY count DESC
            """)

            coffee_stats = [dict(row) for row in cur.fetchall()]

            return jsonify({
                "success": True,
                "data": coffee_stats
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

# Fix for get_daily_stats() function too (has the same issue)
@app.route('/add_student/api/stats/daily', methods=['GET'])
def get_daily_stats():
    """Get daily sales statistics"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get counts and totals by date with CAST for money
            cur.execute("""
                SELECT
                    DATE(datetime) as sale_date,
                    COUNT(*) as count,
                    SUM(CAST(money AS NUMERIC)) as total_sales
                FROM tbl_javohir_sales
                GROUP BY DATE(datetime)
                ORDER BY sale_date DESC
            """)

            daily_stats = [dict(row) for row in cur.fetchall()]

            return jsonify({
                "success": True,
                "data": daily_stats
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({
        "success": False,
        "error": "Resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")