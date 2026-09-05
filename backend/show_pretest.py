import os
import csv
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

# แสดงผลใน PowerShell
print()
print(f"{'Username':<20} {'Score':<10} {'Completed'}")
print("-" * 45)

for username, score, completed in rows:
    print(f"{username:<20} {str(score):<10} {completed}")

# สร้างไฟล์ CSV
output_file = "pretest_results.csv"

with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Username",
        "Pre-test Score",
        "Completed"
    ])

    for username, score, completed in rows:
        writer.writerow([
            username,
            score,
            completed
        ])

cur.close()
conn.close()

print()
print(f"Exported successfully to: {output_file}")