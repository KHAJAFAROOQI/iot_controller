import os
import lirc
from flask import Flask, request, jsonify, Response
from pymongo import MongoClient

app = Flask(__name__)

# --- MongoDB Connection ---
MONGO_URL = "mongodb+srv://farooqi_db_user_:khaja2007@controller-project.9hcro8q.mongodb.net/?appName=controller-project"
client = MongoClient(MONGO_URL)
db = client["controller_project"]
collection = db["ac_status"]

# --- Initialize LIRC ---
sock_id = lirc.init("ac_remote")

# --- Initialize Mongo if empty ---
if collection.count_documents({}) == 0:
    collection.insert_one({"status": "OFF", "temperature": 24})


# --- Serve Web UI directly ---
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Smart AC Controller</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: linear-gradient(135deg, #eef2f3, #8e9eab);
          text-align: center;
          padding-top: 70px;
        }
        .card {
          background: white;
          padding: 40px;
          border-radius: 16px;
          display: inline-block;
          box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        button {
          padding: 12px 30px;
          font-size: 16px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          margin: 10px;
          transition: 0.3s;
        }
        .on { background: #4CAF50; color: white; }
        .off { background: #f44336; color: white; }
        select {
          padding: 10px;
          font-size: 16px;
          border-radius: 6px;
          border: 1px solid #ccc;
        }
        h2 { color: #333; }
      </style>
    </head>
    <body>
      <div class="card">
        <h2>🌬 Smart AC Controller</h2>
        <p><strong>Status:</strong> <span id="status">--</span></p>
        <button id="toggleBtn" class="on">Loading...</button>
        <br><br>
        <label><strong>Temperature:</strong></label><br>
        <select id="tempSelect"></select>
        <br><br>
        <button id="saveBtn">Set Temperature</button>
      </div>

      <script>
        const statusEl = document.getElementById('status');
        const toggleBtn = document.getElementById('toggleBtn');
        const tempSelect = document.getElementById('tempSelect');
        const saveBtn = document.getElementById('saveBtn');

        // Fill dropdown 16–26
        for (let t = 16; t <= 26; t++) {
          const opt = document.createElement('option');
          opt.value = t;
          opt.textContent = t + "°C";
          tempSelect.appendChild(opt);
        }

        async function fetchData() {
          const res = await fetch('/fetch');
          const data = await res.json();
          statusEl.textContent = data.status;
          tempSelect.value = data.temperature;
          toggleBtn.textContent = data.status === "ON" ? "Turn OFF" : "Turn ON";
          toggleBtn.className = data.status === "ON" ? "off" : "on";
        }

        toggleBtn.addEventListener('click', async () => {
          const newStatus = statusEl.textContent === "ON" ? "OFF" : "ON";
          await updateData(newStatus, parseInt(tempSelect.value));
        });

        saveBtn.addEventListener('click', async () => {
          await updateData(statusEl.textContent, parseInt(tempSelect.value));
        });

        async function updateData(status, temperature) {
          await fetch('/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status, temperature})
          });
          fetchData();
        }

        setInterval(fetchData, 2000);
        fetchData();
      </script>
    </body>
    </html>
    '''
    return Response(html, mimetype='text/html')


# --- Fetch Current Data ---
@app.route('/fetch', methods=['GET'])
def fetch():
    data = collection.find_one()
    return jsonify({"status": data["status"], "temperature": data["temperature"]})


# --- Update Data and send IR commands ---
@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    status = data["status"].upper()
    temp = int(data["temperature"])

    # Update DB
    collection.update_one({}, {"$set": {"status": status, "temperature": temp}})

    # --- Send IR Commands through LIRC ---
    try:
        if status == "ON":
            lirc.send_once("ac_remote", "POWER_ON")
        else:
            lirc.send_once("ac_remote", "POWER_OFF")

        # Send temperature IR code (like TEMP_16 ... TEMP_26)
        if 16 <= temp <= 26:
            cmd = f"TEMP_{temp}"
            lirc.send_once("ac_remote", cmd)

        print(f"Sent IR: {status} | Temperature: {temp}°C")

    except Exception as e:
        print("LIRC Error:", e)

    return jsonify({"ok": True, "status": status, "temperature": temp})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
