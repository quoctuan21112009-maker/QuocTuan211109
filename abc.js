// script.js
const API_BASE = window.API_BASE || ""; // set to "" for same origin, or full URL e.g. https://your-render-app.onrender.com

function appendTerm(text){
  const out = document.getElementById("term-output");
  out.textContent += text + "\n";
  out.scrollTop = out.scrollHeight;
}

document.addEventListener("click", e=>{
  if(e.target && e.target.classList.contains("run-btn")){
    const id = e.target.getAttribute("data-id");
    runId(id);
  }
});

document.getElementById("clear-term").addEventListener("click", ()=>{
  document.getElementById("term-output").textContent = "";
});

async function runId(id){
  appendTerm(`> RUN id=${id} ...`);
  try {
    const resp = await fetch(API_BASE + "/run", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({id: id})
    });
    const data = await resp.json();
    if(!data.ok){
      appendTerm(`[ERROR] ${data.error || JSON.stringify(data)}`);
      return;
    }
    appendTerm(`--- STDOUT ---`);
    appendTerm(data.stdout || "(no stdout)");
    if(data.stderr) {
      appendTerm(`--- STDERR ---`);
      appendTerm(data.stderr);
    }
    appendTerm(`--- returncode: ${data.returncode} ---`);
  } catch(err){
    appendTerm(`[NETWORK ERROR] ${err}`);
  }
}