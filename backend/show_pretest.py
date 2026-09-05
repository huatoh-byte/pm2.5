import os
import psycopg2

database_url = os.environ.get("DATABASE_URL")

if not database_url:
    print("DATABASE_URL is not set.")
    exit()

conn = psycopg2.connect(database_url)
cur = conn.cursor()

cur.execute("""
    SELECT username, pretest_score, pretest_completed
    FROM users
    ORDER BY id;
""")

rows = cur.fetchall()

print()
print(f"{'Username':<20} {'Score':<10} {'Completed'}")
print("-" * 45)

for username, score, completed in rows:
    print(f"{username:<20} {str(score):<10} {completed}")

cur.close()
conn.close()