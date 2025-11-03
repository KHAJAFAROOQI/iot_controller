from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URL = "mongodb+srv://farooqi_db_user_:khaja2007@controller-project.9hcro8q.mongodb.net/?appName=controller-project"
client = MongoClient(MONGO_URL)
db = client["ac_controller"]
collection = db["ac_status"]

if collection.count_documents({}) == 0:
    collection.insert_one({"status": "OFF", "temperature": 24})

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Smart AC Controller</title>
  <style>
    body {font-family: Arial; text-align:center; background:#f2f2f2; padding-top:60px;}
    .card {background:white; padding:30px; border-radius:12px; display:inline-block; box-shadow:0 4px 8px rgba(0,0,0,0.2);}
    button {padding:10px 25px; margin:10px; font-size:18px; border:none; border-radius:8px; cursor:pointer;}
    .on{background:#4CAF50;color:white;} .off{background:#f44336;color:white;}
    select {font-size:16px;padding:8px;border-radius:6px;}
  </style>
</head>
<body>
  <div class="card">
    <h2>🌬 Smart AC Controller</h2>
    <p>Status: <span id="status">--</span></p>
    <button id="toggleBtn" class="on">Loading...</button>
    <br><br>
    <label>Temperature:</label>
    <select id="tempSelect"></select><br><br>
    <button id="setBtn">Set Temperature</button>
  </div>
<script>
const statusEl=document.getElementById('status');
const toggleBtn=document.getElementById('toggleBtn');
const tempSel=document.getElementById('tempSelect');
const setBtn=document.getElementById('setBtn');

for(let t=16;t<=26;t++){let o=document.createElement('option');o.value=t;o.text=t+"°C";tempSel.appendChild(o);}

async function refresh(){
  const res=await fetch('/fetch'); const d=await res.json();
  statusEl.textContent=d.status; tempSel.value=d.temperature;
  toggleBtn.textContent=d.status=="ON"?"Turn OFF":"Turn ON";
  toggleBtn.className=d.status=="ON"?"off":"on";
}
toggleBtn.onclick=async()=>{const newS=statusEl.textContent=="ON"?"OFF":"ON"; await update(newS,tempSel.value);};
setBtn.onclick=async()=>{await update(statusEl.textContent,tempSel.value);};
async function update(status,temp){await fetch('/update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status,temperature:temp})});refresh();}
setInterval(refresh,2000); refresh();
</script>
</body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/fetch')
def fetch():
    d=collection.find_one()
    return jsonify({"status":d["status"],"temperature":d["temperature"]})

@app.route('/update',methods=['POST'])
def update():
    data=request.get_json()
    collection.update_one({},{"$set":{"status":data["status"],"temperature":int(data["temperature"])}})
    return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
