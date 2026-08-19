
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from model import predict, get_model
from PIL import Image
import numpy as np, json, datetime, uuid, io, csv

BASE=Path(__file__).parent
UPLOADS=BASE/"uploads"; REPORTS=BASE/"reports"; HISTORY=REPORTS/"history.json"
UPLOADS.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)
app=Flask(__name__)

try:
    history=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
except Exception:
    history=[]

def save_history():
    HISTORY.write_text(json.dumps(history, indent=2), encoding="utf-8")

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def auto_report(result):
    rid=result["id"]
    p=REPORTS/f"ForestGuard_{rid}.txt"
    lines=[
        "FORESTGUARD AI — INVESTIGATION REPORT",
        "="*48,
        f"Report ID: {rid}",
        f"Analysis Type: {result.get('type','')}",
        f"Generated: {result.get('time',now())}",
        "",
    ]
    for k,v in result.items():
        if k not in ("id","type","time"):
            lines.append(f"{k.replace('_',' ').title()}: {v}")
    risk=result.get("risk","")
    if risk in ("CRITICAL","HIGH"):
        action="Priority field verification recommended. Review the source imagery and affected area."
    elif risk=="MEDIUM":
        action="Schedule a closer review and compare with a later image."
    else:
        action="Continue routine monitoring."
    lines += ["",f"Recommendation: {action}"]
    p.write_text("\n".join(lines), encoding="utf-8")
    return p.name

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/predict")
def ai_predict():
    f=request.files.get("image")
    if not f: return jsonify(error="Choose an image first."),400
    path=UPLOADS/f"{uuid.uuid4().hex}.jpg"
    f.save(path)
    result=predict(path)
    result.update({"id":"AI-"+uuid.uuid4().hex[:7].upper(),"type":"AI Detection","time":now()})
    result["report"]=auto_report(result)
    history.append(result); save_history()
    return jsonify(result)

@app.post("/change")
def change():
    before=request.files.get("before"); after=request.files.get("after")
    if not before or not after: return jsonify(error="Choose both images."),400
    pb=UPLOADS/f"{uuid.uuid4().hex}_before.jpg"; pa=UPLOADS/f"{uuid.uuid4().hex}_after.jpg"
    before.save(pb); after.save(pa)
    x=np.asarray(Image.open(pb).convert("RGB").resize((224,224)),float)
    y=np.asarray(Image.open(pa).convert("RGB").resize((224,224)),float)
    vb=x[:,:,1]-(x[:,:,0]+x[:,:,2])/2
    va=y[:,:,1]-(y[:,:,0]+y[:,:,2])/2
    # Actual comparison-derived change percentage.
    loss=float(np.clip(((vb-va)>30).mean()*100,0,100))
    risk="CRITICAL" if loss>=35 else "HIGH" if loss>=20 else "MEDIUM" if loss>=8 else "LOW"
    result={"id":"CH-"+uuid.uuid4().hex[:7].upper(),"type":"Before / After",
            "time":now(),"forest_loss_percent":round(loss,2),
            "risk_score":round(loss,2),"risk":risk}
    result["report"]=auto_report(result)
    history.append(result); save_history()
    return jsonify(result)

@app.get("/analytics")
def analytics():
    ai=[x for x in history if x.get("type")=="AI Detection"]
    ch=[x for x in history if x.get("type")=="Before / After"]
    return jsonify({
        "ai":[{"id":x["id"],"time":x["time"],"value":x.get("risk_score",0),
               "prediction":x.get("prediction",""),"risk":x.get("risk","")} for x in ai],
        "change":[{"id":x["id"],"time":x["time"],"value":x.get("risk_score",0),
                   "risk":x.get("risk","")} for x in ch]
    })

@app.get("/reports")
def reports():
    files=sorted(REPORTS.glob("ForestGuard_*.txt"),key=lambda p:p.stat().st_mtime,reverse=True)
    return jsonify([{"name":p.name,"time":datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
                    for p in files])

@app.get("/csv")
def csv_export():
    keys=sorted({k for row in history for k in row})
    s=io.StringIO(); w=csv.DictWriter(s,fieldnames=keys); w.writeheader(); w.writerows(history)
    return (s.getvalue(),200,{"Content-Type":"text/csv","Content-Disposition":"attachment; filename=forestguard_results.csv"})

@app.post("/clear-history")
def clear_history():
    history.clear(); save_history()
    for p in REPORTS.glob("ForestGuard_*.txt"): p.unlink(missing_ok=True)
    return jsonify(ok=True)

if __name__=="__main__":
    get_model()
    app.run(debug=True)
