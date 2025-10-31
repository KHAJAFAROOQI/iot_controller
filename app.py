from flask import Flask, request, render_template_string
from pymongo import MongoClient

# ---------------- MongoDB connection ----------------
MONGO_URL = "mongodb+srv://farooqi_db_user_:khaja2007@controller-project.9hcro8q.mongodb.net/?appName=controller-project"
client = MongoClient(MONGO_URL)
db = client["controller_project"]
collection = db["ac_status"]

# ---------------- Flask setup ----------------
app = Flask(__name__)

# ---------------- HTML interface ----------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌬️ Smart AC Controller</title>
    <style>
        body {
            font-family: Arial;
            text-align: center;
            background: linear-gradient(135deg, #3a7bd5, #00d2ff);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        h1 { font-size: 36px; margin-bottom: 40px; }
        button {
            padding: 15px 35px;
            font-size: 20px;
            margin: 10px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: white;
        }
        .on { background-color: #28a745; }
        .off { background-color: #dc3545; }
        .temp-up { background-color: #007bff; }
        .temp-down { background-color: #ff9800; }
        .status {
            margin-top: 30px;
            font-size: 22px;
        }
    </style>
</head>
<body>
    <h1>🌬️ Smart AC Controller</h1>

    <div>
        <button class="on" onclick="controlAC('ON')">Turn ON</button>
        <button class="off" onclick="controlAC('OFF')">Turn OFF</button>
    </div>

    <div>
        <button class="temp-down" onclick="changeTemp('decrease')">- Temp</button>
        <button class="temp-up" onclick="changeTemp('increase')">+ Temp</button>
    </div>

    <div class="status">
        Current Status: <span id="statusText">Loading...</span><br>
        Current Temperature: <span id="tempText">--</span>°C
    </div>

    <script>
        function controlAC(state) {
            fetch('/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'state=' + state
            }).then(() => refreshStatus());
        }

        function changeTemp(action) {
            fetch('/temp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=' + action
            }).then(() => refreshStatus());
        }

        function refreshStatus() {
            fetch('/status').then(res => res.json())
            .then(data => {
                document.getElementById('statusText').innerText = data.state;
                document.getElementById('tempText').innerText = data.temperature;
            });
        }

        // Load initial data
        refreshStatus();
        setInterval(refreshStatus, 3000);
    </script>
</body>
</html>
"""

# ---------------- Flask Routes ----------------
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/update', methods=['POST'])
def update_state():
    state = request.form.get('state', 'OFF')
    doc = collection.find_one() or {}
    temperature = doc.get('temperature', 24)
    collection.update_one({}, {'$set': {'state': state, 'temperature': temperature}}, upsert=True)
    return "OK"

@app.route('/temp', methods=['POST'])
def update_temperature():
    action = request.form.get('action')
    doc = collection.find_one() or {'temperature': 24, 'state': 'OFF'}
    temp = doc.get('temperature', 24)

    if action == 'increase' and temp < 24:
        temp += 1
    elif action == 'decrease' and temp > 16:
        temp -= 1

    collection.update_one({}, {'$set': {'temperature': temp}}, upsert=True)
    return "OK"

@app.route('/status')
def get_status():
    data = collection.find_one() or {'state': 'OFF', 'temperature': 24}
    return data

# ---------------- Run Flask Server ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
