document.addEventListener('DOMContentLoaded', function () {
    const aqiContainer = document.getElementById('aqiContainer');

    if (!aqiContainer) {
        return;
    }

    const aqi = parseFloat(aqiContainer.dataset.aqi);

    if (Number.isNaN(aqi)) {
        return;
    }

    const level = document.getElementById('level');
    const advice = document.getElementById('advice');

    if (aqi <= 25) {
        level.textContent = 'ระดับ: ดีมาก';
        advice.textContent =
            'คุณภาพอากาศดีมาก สามารถทำกิจกรรมกลางแจ้งและใช้ชีวิตได้ตามปกติ';

        level.className = 'aqi-very-good';
        advice.className = 'aqi-very-good';

    } else if (aqi <= 50) {
        level.textContent = 'ระดับ: ดี';
        advice.textContent =
            'คุณภาพอากาศดี สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ โดยผู้ที่มีความเสี่ยงควรสังเกตอาการผิดปกติของตนเอง';

        level.className = 'aqi-good';
        advice.className = 'aqi-good';

    } else if (aqi <= 100) {
        level.textContent = 'ระดับ: ปานกลาง';
        advice.textContent =
            'ประชาชนทั่วไปควรลดกิจกรรมกลางแจ้งที่ใช้แรงมาก ส่วนกลุ่มเสี่ยงควรลดระยะเวลาทำกิจกรรมกลางแจ้งและสวมหน้ากากป้องกัน PM2.5 เมื่อออกนอกอาคาร';

        level.className = 'aqi-moderate';
        advice.className = 'aqi-moderate';

    } else if (aqi <= 200) {
        level.textContent = 'ระดับ: เริ่มมีผลกระทบต่อสุขภาพ';
        advice.textContent =
            'ควรลดระยะเวลาหรือความหนักของกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน PM2.5 โดยเฉพาะผู้ที่อยู่ในกลุ่มเสี่ยงควรระมัดระวังเป็นพิเศษ';

        level.className = 'aqi-sensitive';
        advice.className = 'aqi-sensitive';

    } else {
        level.textContent = 'ระดับ: มีผลกระทบต่อสุขภาพ';
        advice.textContent =
            'ควรหลีกเลี่ยงกิจกรรมกลางแจ้งและพื้นที่ที่มีมลพิษทางอากาศสูง หากจำเป็นต้องออกนอกอาคารควรใช้อุปกรณ์ป้องกันตนเอง โดยเฉพาะผู้ที่อยู่ในกลุ่มเสี่ยง';

        level.className = 'aqi-unhealthy';
        advice.className = 'aqi-unhealthy';
    }
});