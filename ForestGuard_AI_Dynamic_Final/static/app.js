
function show(id){
 document.querySelectorAll("section").forEach(x=>x.classList.add("hide"));
 document.getElementById(id).classList.remove("hide");
 const titles={dash:"Forest Intelligence Center",ai:"AI Detection",chg:"Before / After Change Detection",analytics:"Dynamic Risk Analytics",rep:"Investigation Reports"};
 document.getElementById("title").textContent=titles[id]||"ForestGuard AI";
 if(id==="analytics")loadAnalytics();
 if(id==="rep")loadReports();
}
function toast(t){const x=document.getElementById("toast");x.textContent=t;x.classList.add("show");setTimeout(()=>x.classList.remove("show"),1800)}
async function predict(){
 const f=document.getElementById("img").files[0]; if(!f)return toast("Choose an image first");
 const d=new FormData();d.append("image",f);
 const r=await fetch("/predict",{method:"POST",body:d}).then(x=>x.json());
 document.getElementById("ao").innerHTML=`<div class="result">
 <span class="tag">${r.type}</span><h3>${r.prediction}</h3><div class="big">${r.risk_score}%</div>
 <p>Actual deforestation risk score · confidence ${r.confidence}%</p><b class="risk ${r.risk}">${r.risk} RISK</b>
 <p>${r.time} · ${r.id}</p><p>Report automatically created: ${r.report}</p>
 <button onclick="show('analytics')">See Updated AI Graph</button></div>`;
 toast("AI result saved and graph updated");
}
async function changeDetect(){
 const b=document.getElementById("bf").files[0],a=document.getElementById("af").files[0];
 if(!b||!a)return toast("Choose both images");
 const d=new FormData();d.append("before",b);d.append("after",a);
 const r=await fetch("/change",{method:"POST",body:d}).then(x=>x.json());
 document.getElementById("co").innerHTML=`<div class="result">
 <span class="tag">${r.type}</span><h3>Vegetation Change Detected</h3><div class="big">${r.forest_loss_percent}%</div>
 <p>Actual calculated forest-loss risk</p><b class="risk ${r.risk}">${r.risk} RISK</b>
 <p>${r.time} · ${r.id}</p><p>Report automatically created: ${r.report}</p>
 <button onclick="show('analytics')">See Updated Before/After Graph</button></div>`;
 toast("Comparison saved and graph updated");
}
async function loadAnalytics(){
 const data=await fetch("/analytics").then(x=>x.json());
 drawLine("aiChart",data.ai.map(x=>Number(x.value)||0),"AI Detection Risk");
 drawLine("changeChart",data.change.map(x=>Number(x.value)||0),"Before / After Risk");
 const a=data.ai,c=data.change;
 document.getElementById("aiMeta").textContent=a.length?`${a.length} actual reading(s) · latest ${Number(a.at(-1).value).toFixed(1)}%`:"No AI readings yet";
 document.getElementById("changeMeta").textContent=c.length?`${c.length} actual reading(s) · latest ${Number(c.at(-1).value).toFixed(1)}%`:"No comparison readings yet";
}
function drawLine(id,vals,label){
 const c=document.getElementById(id),ctx=c.getContext("2d"),dpr=devicePixelRatio||1;
 const w=Math.max(600,c.clientWidth||800),h=320;c.width=w*dpr;c.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
 ctx.fillStyle="#07140d";ctx.fillRect(0,0,w,h);
 const L=60,R=25,T=48,B=50,W=w-L-R,H=h-T-B;
 ctx.font="12px Arial";ctx.fillStyle="#8ab89b";ctx.fillText(label,20,25);
 ctx.strokeStyle="#183a28";ctx.lineWidth=1;
 for(let n=0;n<=100;n+=20){let y=T+H-(n/100)*H;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(L+W,y);ctx.stroke();ctx.fillStyle="#648875";ctx.fillText(n+"%",20,y+4)}
 if(!vals.length){ctx.fillStyle="#6f907d";ctx.font="14px Arial";ctx.fillText("Run an analysis to create the first real reading.",L+15,T+H/2);return}
 const x=i=>vals.length===1?L+W/2:L+i*W/(vals.length-1),y=v=>T+H-(Math.max(0,Math.min(100,v))/100)*H;
 ctx.strokeStyle="#62df98";ctx.lineWidth=3;ctx.beginPath();
 vals.forEach((v,i)=>i?ctx.lineTo(x(i),y(v)):ctx.moveTo(x(i),y(v)));ctx.stroke();
 vals.forEach((v,i)=>{ctx.fillStyle="#62df98";ctx.beginPath();ctx.arc(x(i),y(v),5,0,Math.PI*2);ctx.fill();ctx.fillStyle="#edf9f0";ctx.font="11px Arial";ctx.fillText(v.toFixed(1)+"%",x(i)-15,y(v)-12);ctx.fillStyle="#668a76";ctx.fillText("#"+(i+1),x(i)-9,T+H+22)});
}
async function loadReports(){
 const r=await fetch("/reports").then(x=>x.json());
 document.getElementById("reports").innerHTML=r.length?r.map(x=>`<div class="reportrow">▣ <b>${x.name}</b><small>${x.time}</small></div>`).join(""):"<p>No reports yet.</p>";
}
async function clearHistory(){if(!confirm("Clear all saved test readings and generated reports?"))return;await fetch("/clear-history",{method:"POST"});loadAnalytics();loadReports();toast("History cleared")}
window.addEventListener("resize",()=>{if(!document.getElementById("analytics").classList.contains("hide"))loadAnalytics()});
