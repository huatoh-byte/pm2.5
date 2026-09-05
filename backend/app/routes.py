import os
import requests
import urllib3
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import db, User
import app
import time

main = Blueprint('main', __name__)

def get_area_list():
    """Reads options from list.txt inside the backend directory."""
    list_path = os.path.join(os.path.dirname(__file__), '..', 'list.txt')
    if os.path.exists(list_path):
        with open(list_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def clean_string(text):
    """Utility to remove whitespace, non-breaking spaces, and commas for flexible matching."""
    if not text:
        return ""
    return text.replace(',', '').replace(' ', '').replace('\xa0', '').strip()


def get_air4thai_data():
    """Fetch Air4Thai data when the cache is empty or older than 1 hour."""

    current_time = time.time()

    # ถ้ามี cache และยังไม่เกิน 1 ชั่วโมง ใช้ข้อมูลเดิมทันที
    if (
        app.latest_aqi_data
        and current_time - app.latest_aqi_updated_at < 3600
    ):
        return app.latest_aqi_data

    try:
        print("[AQI] Fetching data from Air4Thai...")

        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

        # ใช้ Session และปิด trust_env
        # เพื่อหลีกเลี่ยงปัญหาเกี่ยวกับ environment/netrc
        # ที่เคยเกิดใน Render
        session = requests.Session()
        session.trust_env = False

        response = session.get(
            "https://air4thai.pcd.go.th/services/getNewAQI_JSON.php",
            timeout=(5, 12),
            verify=False,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        new_data = response.json()

        # ตรวจว่าข้อมูลที่ได้มี stations จริง
        if not isinstance(new_data, dict) or 'stations' not in new_data:
            raise ValueError("Air4Thai response does not contain stations")

        app.latest_aqi_data.clear()
        app.latest_aqi_data.update(new_data)
        app.latest_aqi_updated_at = current_time

        print(
            f"[AQI] Data updated successfully. "
            f"Stations: {len(new_data.get('stations', []))}"
        )

    except Exception as e:
        print(f"[AQI] Failed to fetch Air4Thai data: {e}")

    # ถ้า fetch ใหม่ไม่สำเร็จ แต่มี cache เก่า
    # ก็ยังคืน cache เก่าได้
    return app.latest_aqi_data

def find_pm25_for_area(user_area):
    """Matches the user's selected area against the Air4Thai API station data."""
    # If the background fetch hasn't completed yet, trigger an immediate backup request

    data = get_air4thai_data()
    if not data:
        print("[AQI] No Air4Thai data available.")
        return None


    stations = data.get('stations', [])
    clean_user_area = clean_string(user_area)

    print(f"[AQI] Cache ready. Stations: {len(stations)}")
    print(f"[AQI] Looking for user area: {user_area}")

    for station in stations:
        area_th = station.get('areaTH', '')
        name_th = station.get('nameTH', '')
        clean_area_th = clean_string(area_th)
        clean_name_th = clean_string(name_th)

        # Match cleaned text strings
        if clean_user_area in clean_area_th or clean_area_th in clean_user_area or clean_user_area in clean_name_th:
            print(f"[AQI] Matched station: {name_th} | {area_th}")
            # Check 'AQILast' key instead of 'LastUpdate'
            aqi_last = station.get('AQILast', {})
            
            pm25_info = aqi_last.get('PM25', {})
            aqi_info = aqi_last.get('AQI', {})

            pm25_val = pm25_info.get('value', 'N/A') if isinstance(pm25_info, dict) else 'N/A'
            aqi_val = aqi_info.get('aqi', 'N/A') if isinstance(aqi_info, dict) else 'N/A'

            date_str = aqi_last.get('date', '')
            time_str = aqi_last.get('time', '')

            return {
                'station_name': name_th or 'Unknown Station',
                'area': area_th,
                'pm25': pm25_val,
                'aqi': aqi_val,
                'updated_at': f"{date_str} {time_str}".strip()
            }
            
    return None

# 1. MAIN DASHBOARD
@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    current_user = User.query.get(session['user_id'])
    if not current_user.pretest_completed:
        return redirect(url_for('main.pretest'))
    air_info = find_pm25_for_area(current_user.area)

    return render_template('index.html', user=current_user, air_info=air_info)

# 2. SIGN-UP
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        selected_area = request.form.get('area')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Try logging in.')
            return redirect(url_for('main.signup'))

        new_user = User(username=username, area=selected_area)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('main.login'))

    areas = get_area_list()
    return render_template('signup.html', areas=areas)

# 3. LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            if not user.pretest_completed:
                return redirect(url_for('main.pretest'))

            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password!')
            
    return render_template('login.html')

# 4. LOGOUT
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))


# 5. ADVICE
@main.route('/advice')
def advice():
    return render_template('advice.html')

# pretest
# 5. PM2.5 PRE-TEST

PRETEST_QUESTIONS = [
    {
        'question': 'PM2.5 หมายถึงข้อใด',
        'options': {
            'A': 'ฝุ่นที่มีเส้นผ่านศูนย์กลางไม่เกิน 25 ไมโครเมตร',
            'B': 'ฝุ่นที่มีเส้นผ่านศูนย์กลางไม่เกิน 2.5 ไมโครเมตร',
            'C': 'ก๊าซพิษที่เกิดจากรถยนต์เท่านั้น',
            'D': 'ฝุ่นที่สามารถมองเห็นได้ด้วยตาเปล่าเท่านั้น'
        },
        'answer': 'B'
    },
    {
        'question': 'ข้อใดเป็นแหล่งกำเนิด PM2.5',
        'options': {
            'A': 'การเผาขยะและเศษวัสดุในที่โล่ง',
            'B': 'ไอเสียจากยานพาหนะ',
            'C': 'กระบวนการเผาไหม้จากกิจกรรมบางประเภท',
            'D': 'ถูกทุกข้อ'
        },
        'answer': 'D'
    },
    {
        'question': 'กลุ่มใดมีความเสี่ยงต่อผลกระทบจาก PM2.5 มากกว่าคนทั่วไป',
        'options': {
            'A': 'เด็ก ผู้สูงอายุ และผู้ป่วยโรคหัวใจหรือทางเดินหายใจ',
            'B': 'ผู้ที่เล่นกีฬาเท่านั้น',
            'C': 'ผู้ที่ทำงานในเวลากลางคืนเท่านั้น',
            'D': 'ผู้ที่อาศัยอยู่ต่างจังหวัดเท่านั้น'
        },
        'answer': 'A'
    },
    {
        'question': 'หากค่า Thai AQI เท่ากับ 120 คุณภาพอากาศอยู่ในระดับใด',
        'options': {
            'A': 'ดีมาก',
            'B': 'ดี',
            'C': 'ปานกลาง',
            'D': 'เริ่มมีผลกระทบต่อสุขภาพ'
        },
        'answer': 'C'
    },
    {
        'question': 'เมื่อ Thai AQI อยู่ในช่วง 101–150 กลุ่มเสี่ยงควรทำอย่างไร',
        'options': {
            'A': 'เพิ่มการออกกำลังกายกลางแจ้ง',
            'B': 'ลดกิจกรรมกลางแจ้งที่ใช้แรงหรือใช้เวลานาน',
            'C': 'เปิดหน้าต่างเพื่อรับอากาศจากภายนอกให้มากขึ้น',
            'D': 'ไม่จำเป็นต้องเปลี่ยนพฤติกรรมใด ๆ'
        },
        'answer': 'B'
    },
    {
        'question': 'หาก Thai AQI อยู่ในช่วง 201–300 ข้อใดเหมาะสมที่สุด',
        'options': {
            'A': 'คุณภาพอากาศดี สามารถทำกิจกรรมได้ตามปกติ',
            'B': 'เฉพาะผู้สูงอายุเท่านั้นที่ต้องระวัง',
            'C': 'ทุกคนควรลดหรือหลีกเลี่ยงกิจกรรมกลางแจ้งที่ใช้แรง โดยเฉพาะกลุ่มเสี่ยง',
            'D': 'ควรออกกำลังกายกลางแจ้งเพื่อให้ร่างกายปรับตัว'
        },
        'answer': 'C'
    },
    {
        'question': 'พฤติกรรมใดช่วยลดการเกิดมลพิษทางอากาศได้',
        'options': {
            'A': 'ติดเครื่องยนต์รถยนต์ทิ้งไว้ขณะจอด',
            'B': 'เผาใบไม้แทนการนำไปจัดการด้วยวิธีอื่น',
            'C': 'ใช้ระบบขนส่งสาธารณะเมื่อสามารถทำได้',
            'D': 'เผาขยะครั้งละน้อยเพื่อให้เกิดควันน้อยลง'
        },
        'answer': 'C'
    },
    {
        'question': 'ข้อใดกล่าวถูกต้องเกี่ยวกับการตรวจสอบ AQI',
        'options': {
            'A': 'ใช้เพื่อทราบระดับคุณภาพอากาศและช่วยวางแผนกิจกรรมได้',
            'B': 'ใช้เพื่อบอกอุณหภูมิของอากาศเท่านั้น',
            'C': 'ถ้าไม่เห็นฝุ่นด้วยตาเปล่า ไม่จำเป็นต้องตรวจ AQI',
            'D': 'AQI ไม่มีความเกี่ยวข้องกับผลกระทบต่อสุขภาพ'
        },
        'answer': 'A'
    }
]


@main.route('/pretest', methods=['GET', 'POST'])
def pretest():
    # ต้อง login ก่อน
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    # เผื่อ account ถูกลบหรือหาไม่เจอ
    if user is None:
        session.pop('user_id', None)
        return redirect(url_for('main.login'))

    # ถ้าเคยทำแล้ว ห้ามกลับมาทำอีก
    if user.pretest_completed:
        return redirect(url_for('main.index'))

    # เมื่อกด Submit
    if request.method == 'POST':
        score = 0
        selected_answers = []

        # อ่านคำตอบทุกข้อ
        for i, question in enumerate(PRETEST_QUESTIONS, start=1):
            selected_answer = request.form.get(f'question_{i}')
            selected_answers.append(selected_answer)

        # ป้องกันกรณีส่งคำตอบมาไม่ครบ
        if any(answer is None for answer in selected_answers):
            flash('กรุณาตอบคำถามให้ครบทุกข้อ')
            return render_template(
                'pretest.html',
                questions=PRETEST_QUESTIONS
            )

        # ตรวจคำตอบ
        for selected_answer, question in zip(
            selected_answers,
            PRETEST_QUESTIONS
        ):
            if selected_answer == question['answer']:
                score += 1

        # บันทึกคะแนน แต่ไม่แสดงให้ user
        user.pretest_score = score
        user.pretest_completed = True

        db.session.commit()

        # ทำเสร็จแล้วเข้า Dashboard ทันที
        return redirect(url_for('main.index'))

    # GET: แสดงข้อสอบตามปกติ
    return render_template(
        'pretest.html',
        questions=PRETEST_QUESTIONS
    )