document.addEventListener('DOMContentLoaded', () => {
    const aqiContainer = document.getElementById('aqiContainer');
    
    if (aqiContainer && aqiContainer.dataset.pm25) {
        const pm25Value = parseFloat(aqiContainer.dataset.pm25);
        console.log('PM2.5 Value:', pm25Value);
        
        const div = document.getElementById("level");
        div.classList.add("aqi-status"); // Optional: add class for CSS styling
        const advice = document.getElementById("advice");
    
        if (pm25Value <= 50) {
            div.textContent += "Good";
            div.style.color = "green";
            advice.textContent += "คุณภาพอากาศดี สามารถทำกิจกรรมกลางแจ้งได้ปกติ";
            advice.style.color = "green";
        } else if (pm25Value <= 100) {
            div.textContent += "Moderate";
            div.style.color = "gold";
            advice.textContent += "คุณภาพอากาศปานกลาง ผู้ที่ไวต่อมลพิษควรสังเกตอาการ";
            advice.style.color = "gold";
        } else if (pm25Value <= 150) {
            div.textContent += "Unhealthy for Sensitive Groups";
            div.style.color = "orange";
            advice.textContent += "กลุ่มเสี่ยงควรลดกิจกรรมกลางแจ้งที่ใช้แรงหรือเวลานาน";
            advice.style.color = "orange";
        } else if (pm25Value <= 200) {
            div.textContent += "Unhealthy";
            div.style.color = "red";
            advice.textContent += "ควรลดกิจกรรมกลางแจ้ง กลุ่มเสี่ยงควรลดกิจกรรมที่อยู่นอกอาคาร";
            advice.style.color = "red";
        } else if (pm25Value <= 300) {
            div.textContent += "Very Unhealthy";
            div.style.color = "purple";
            advice.textContent += "ควรหลีกเลี่ยงกิจกรรมกลางแจ้ง กลุ่มเสี่ยงควรอยู่ภายในอาคาร";\
            advice.style.color = "purple";
        } else {
            div.textContent += "Hazardous";
            div.style.color = "brown";
            advice.textContent += "หลีกเลี่ยงการออกภายนอกอาคาร อยู่ในพื้นที่อากาศสะอาด และ ติดตามประกาศทางการ";
            advice.style.color = "brown";
        }
    }
});
