from flask import Flask, request, jsonify, render_template_string
import threading, pexpect

app = Flask(__name__)

process = None
logs = []

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CKR PRO</title>

<style>
body{
    margin:0;
    font-family:-apple-system;
    background:#0d1117;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    color:white;
}

.box{
    width:100%;
    max-width:360px;
    padding:15px;
    border-radius:20px;
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(20px);
}

input{
    width:100%;
    padding:10px;
    border:none;
    border-radius:10px;
    margin-top:10px;
    background:#161b22;
    color:white;
}

button{
    width:100%;
    padding:10px;
    margin-top:10px;
    border:none;
    border-radius:10px;
    font-weight:bold;
}

.start{background:#00ff99;color:black;}
.stop{background:#ff3b3b;}

#terminal{
    margin-top:10px;
    height:240px;
    overflow:auto;
    background:black;
    padding:10px;
    border-radius:10px;
    font-family:monospace;
    font-size:12px;
}
</style>
</head>

<body>

<div class="box">
<h3>CKR PRO</h3>

<input id="uid" placeholder="Enter UID">

<button class="start" onclick="start()">START</button>
<button class="stop" onclick="stop()">STOP</button>

<div id="terminal"></div>
</div>

<script>
function start(){
    fetch("/start",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            uid:document.getElementById("uid").value
        })
    });
}

function stop(){
    fetch("/stop",{method:"POST"});
}

function logs(){
    fetch("/logs")
    .then(r=>r.json())
    .then(d=>{
        let t=document.getElementById("terminal");
        t.innerHTML=d.logs.join("<br>");
        t.scrollTop=t.scrollHeight;
    });
}

setInterval(logs,800);
</script>

</body>
</html>
"""

# 🔥 REAL FIX USING PEXPECT
def run_script(uid):
    global process, logs

    logs.clear()

    process = pexpect.spawn("python ckr.py", encoding="utf-8")

    try:
        # wait for input prompt
        process.expect("uid", timeout=10)
        process.sendline(uid)
    except:
        process.sendline(uid)

    while True:
        try:
            line = process.readline().strip()
            if line:
                logs.append(line)
        except:
            break


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/start", methods=["POST"])
def start():
    uid = request.json.get("uid")

    threading.Thread(target=run_script, args=(uid,), daemon=True).start()

    return jsonify({"msg":"started"})


@app.route("/stop", methods=["POST"])
def stop():
    global process

    if process:
        process.terminate(force=True)

    return jsonify({"msg":"stopped"})


@app.route("/logs")
def get_logs():
    return jsonify({"logs": logs[-300:]})


app.run(host="0.0.0.0", port=5000)