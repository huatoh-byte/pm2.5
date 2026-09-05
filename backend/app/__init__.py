import os
import threading
import time
import requests
import urllib3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

db = SQLAlchemy()

# Global memory storage for the latest Air4Thai API data
latest_aqi_data = {}
latest_aqi_updated_at = 0

def start_hourly_aqi_fetch():
    global latest_aqi_data
    def fetch_job():
        global latest_aqi_data
        url = "https://air4thai.pcd.go.th/services/getNewAQI_JSON.php"
        while True:
            try:
                print("[AQI Fetcher] Requesting data from Air4Thai...")
                response = requests.get(
                    url,
                    timeout=10,
                    verify=False
               )
                if response.status_code == 200:
                   new_data = response.json()
                   
                   latest_aqi_data.clear()
                   latest_aqi_data.update(new_data)
                   
                   print(
                    f"[AQI Fetcher] Data updated successfully! "
                    f"Stations: {len(latest_aqi_data.get('stations', []))}"
                )
                   
                   # Fetch สำเร็จแล้ว รอ 1 ชั่วโมงก่อนอัปเดตใหม่
                   time.sleep(3600)

                else:
                    print(f"[AQI Fetcher] HTTP error: {response.status_code}")
                    # ถ้า Air4Thai ตอบ error ลองใหม่ใน 1 นาที
                    time.sleep(60)

            except Exception as e:
                print(f"[AQI Fetcher] Error fetching data: {e}")
                # ถ้า connection error / timeout ลองใหม่ใน 1 นาที
                time.sleep(60)

    thread = threading.Thread(target=fetch_job, daemon=True)
    thread.start()

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates', 
                static_folder='../../frontend/static')
    
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()



    return app