document.addEventListener('DOMContentLoaded', () => {

    const aqiContainer = document.getElementById('aqiContainer');

    if (!aqiContainer || !aqiContainer.dataset.pm25) {
        return;
    }

    const aqiValue = parseFloat(aqiContainer.dataset.pm25);

    console.log('AQI Value:', aqiValue);

    const level = document.getElementById('level');
    const advice = document.getElementById('advice');

    if (!level || !advice || Number.isNaN(aqiValue)) {
        return;
    }

    // Remove the original labels so we can rebuild them
    level.innerHTML = '<strong>Level:</strong> ';
    advice.innerHTML = '<strong>Advice:</strong> ';

    if (aqiValue <= 50) {

        level.innerHTML += 'Good';
        level.className = 'aqi-good';

        advice.innerHTML +=
            'คุณภาพอากาศดี สามารถทำกิจกรรมกลางแจ้งได้ปกติ';

        advice.className = 'aqi-good';

    } else if (aqiValue <= 100) {

        level.innerHTML += 'Moderate';
        level.className = 'aqi-moderate';

        advice.innerHTML +=
            'คุณภาพอากาศปานกลาง ผู้ที่ไวต่อมลพิษควรสังเกตอาการ';

        advice.className = 'aqi-moderate';

    } else if (aqiValue <= 150) {

        level.innerHTML += 'Unhealthy for Sensitive Groups';
        level.className = 'aqi-sensitive';

        advice.innerHTML +=
            'กลุ่มเสี่ยงควรลดกิจกรรมกลางแจ้งที่ใช้แรงหรือเวลานาน';

        advice.className = 'aqi-sensitive';

    } else if (aqiValue <= 200) {

        level.innerHTML += 'Unhealthy';
        level.className = 'aqi-unhealthy';

        advice.innerHTML +=
            'ควรลดกิจกรรมกลางแจ้ง กลุ่มเสี่ยงควรลดกิจกรรมที่อยู่นอกอาคาร';

        advice.className = 'aqi-unhealthy';

    } else if (aqiValue <= 300) {

        level.innerHTML += 'Very Unhealthy';
        level.className = 'aqi-very-unhealthy';

        advice.innerHTML +=
            'ควรหลีกเลี่ยงกิจกรรมกลางแจ้ง กลุ่มเสี่ยงควรอยู่ภายในอาคาร';

        advice.className = 'aqi-very-unhealthy';

    } else {

        level.innerHTML += 'Hazardous';
        level.className = 'aqi-hazardous';

        advice.innerHTML +=
            'หลีกเลี่ยงการออกภายนอกอาคาร อยู่ในพื้นที่อากาศสะอาด และติดตามประกาศทางการ';

        advice.className = 'aqi-hazardous';
    }

});