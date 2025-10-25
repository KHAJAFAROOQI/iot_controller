from flask import Flask, request, render_template_string
from pymongo import MongoClient

# ---------------- MongoDB connection ----------------
MONGO_URL = "mongodb+srv://farooqi_db_user_:khaja2007@controller-project.9hcro8q.mongodb.net/?appName=controller-project"
client = MongoClient(MONGO_URL)
db = client["controller_project"]
collection = db["ac_status"]

# ---------------- Flask setup ----------------
app = Flask(__name__)

# ---------------- HTML interface (inline) ----------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Smart AC Controller</title>
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
        h1 { font-size: 40px; margin-bottom: 40px; }
        button {
            padding: 15px 40px;
            font-size: 20px;
            margin: 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: white;
        }
        .on { background-color: #28a745; }
        .off { background-color: #dc3545; }
        .status {
            margin-top: 30px;
            font-size: 24px;
        }
    </style>
</head>
<body>
    <h1>🌬️ Smart AC Controller</h1>
    <button class="on" onclick="controlAC('ON')">Turn ON</button>
    <button class="off" onclick="controlAC('OFF')">Turn OFF</button>

    <div class="status">
        Current Status: <span id="statusText">Loading...</span>
    </div>

    <script>
        function controlAC(state) {
            fetch('/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'state=' + state
            }).then(res => res.text())
              .then(txt => {
                  document.getElementById('statusText').innerText = state;
              });
        }

        // Fetch initial status
        fetch('/status').then(res => res.text())
        .then(txt => { document.getElementById('statusText').innerText = txt; });
    </script>
</body>
</html>
"""

# ---------------- Routes ----------------

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/update', methods=['POST'])
def update_state():
    state = request.form.get('state')
    if state:
        collection.update_one({}, {'$set': {'state': state}}, upsert=True)
    return "OK"

@app.route('/status')
def get_status():
    data = collection.find_one()
    if data and 'state' in data:
        return data['state']
    return "OFF"

# ---------------- Run server ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
