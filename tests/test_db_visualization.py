#!/usr/bin/env python3
"""
Database Visualization Test Script
Displays all user information stored in bot_database.db
"""

import sqlite3
from datetime import datetime
import os

def visualize_database():
    """Connect to database and display user information"""
    db_path = "../bot_database.db"

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            print("📊 Database Visualization")
            print("=" * 50)
            print(f"Database: {db_path}")
            print(f"Tables found: {len(tables)}")
            print()

            # Display users table
            if ('users',) in tables:
                print("👥 USERS TABLE")
                print("-" * 50)

                # Get all users
                cursor.execute("""
                    SELECT user_id, first_name, username, chat_id,
                           image_credits, video_credits, current_plan, plan_expiry_date, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)

                users = cursor.fetchall()

                if not users:
                    print("📭 No users found in database")
                    return

                print(f"Total users: {len(users)}")
                print()

                for i, user in enumerate(users, 1):
                    user_id, first_name, username, chat_id, image_credits, video_credits, current_plan, plan_expiry_date, created_at = user

                    print(f"👤 User #{i}")
                    print(f"   User ID: {user_id}")
                    print(f"   Name: {first_name or 'N/A'}")
                    print(f"   Username: @{username or 'N/A'}")
                    print(f"   Chat ID: {chat_id}")
                    print(f"   Image Credits: {image_credits}")
                    print(f"   Video Credits: {video_credits}")
                    print(f"   Current Plan: {current_plan or 'None'}")
                    print(f"   Plan Expiry: {plan_expiry_date or 'N/A'}")
                    print(f"   Created: {created_at}")
                    print("-" * 30)

            else:
                print("❌ Users table not found!")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_table_schema():
    """Display the database schema"""
    db_path = "../bot_database.db"

    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            print("📋 DATABASE SCHEMA")
            print("=" * 50)

            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
            schema = cursor.fetchone()

            if schema and schema[0]:
                print("Users Table Schema:")
                print(schema[0])
            else:
                print("❌ Could not retrieve schema")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🔍 Database Visualization Test")
    print("=" * 50)
    print()

    # Show schema first
    # show_table_schema()
    # print()

    # Show data
    visualize_database()

    print()
    print("✅ Database visualization complete!")
