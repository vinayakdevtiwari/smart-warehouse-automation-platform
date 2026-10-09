/* ══════════════════════════════════════════════════════════
   Smart Warehouse Automation Platform — app.js
   Full JS: navigation, animations, scheduler algorithms,
   warehouse floor sim, PCB viewer, state diagram, comparison
   ══════════════════════════════════════════════════════════ */

'use strict';

// ──────────────────────────────────────────────────────────
// 1. CONSTANTS & DATA
// ──────────────────────────────────────────────────────────

const TASK_TYPES = [
  { name:'Urgent Order Processing', icon:'🚨', priority:1, pClass:'p1', desc:'Highest-priority customer orders requiring immediate dispatch.' },
  { name:'Normal Order Processing', icon:'📬', priority:2, pClass:'p2', desc:'Standard customer orders processed in sequence.' },
  { name:'Picking',                 icon:'🛒', priority:2, pClass:'p2', desc:'Robot retrieves items from shelves for an order.' },
  { name:'Packing',                 icon:'📦', priority:2, pClass:'p2', desc:'Items packed and labelled for dispatch.' },
  { name:'Dispatch Preparation',    icon:'🚚', priority:2, pClass:'p2', desc:'Final checks and loading for outbound shipments.' },
  { name:'Inventory Update',        icon:'📊', priority:3, pClass:'p3', desc:'Routine database sync of stock levels.' },
  { name:'Restocking',              icon:'🔧', priority:3, pClass:'p3', desc:'Replenish low shelves from warehouse reserves.' },
];

const PRIORITY_LABEL = { 1:'Priority 1 — Urgent', 2:'Priority 2 — Normal', 3:'Priority 3 — Routine' };

const COLORS = ['#E8845A','#3B82F6','#D97706','#DC2626','#7C3AED','#16A34A','#C1613A','#0284C7'];

const TC = {
  tc1:[
    { id:'P1', type:'Restocking',              at:0, bt:8, priority:3 },
    { id:'P2', type:'Urgent Order Processing', at:2, bt:3, priority:1 },
  ],
  tc2:[
    { id:'P1', type:'Packing',                 at:0, bt:6, priority:2 },
    { id:'P2', type:'Inventory Update',         at:1, bt:4, priority:3 },
    { id:'P3', type:'Urgent Order Processing', at:2, bt:2, priority:1 },
    { id:'P4', type:'Normal Order Processing', at:3, bt:3, priority:2 },
  ],
  tc3:[
    { id:'P1', type:'Restocking',              at:0, bt:5, priority:3 },
    { id:'P2', type:'Picking',                 at:1, bt:4, priority:2 },
    { id:'P3', type:'Urgent Order Processing', at:2, bt:3, priority:1 },
    { id:'P4', type:'Packing',                 at:3, bt:2, priority:2 },
    { id:'P5', type:'Dispatch Preparation',    at:4, bt:3, priority:2 },
    { id:'P6', type:'Inventory Update',        at:6, bt:4, priority:3 },
    { id:'P7', type:'Normal Order Processing', at:7, bt:2, priority:2 },
  ],
};

let currentAlgo  = 'priority_p';
let tasks        = JSON.parse(JSON.stringify(TC.tc3));
let pidCounter   = 8;
let comparePreset= 'tc3';

// ──────────────────────────────────────────────────────────
// 2. NAVIGATION
// ──────────────────────────────────────────────────────────

const PAGE_TITLES = {
  dashboard:'Dashboard', warehouse:'Warehouse Floor', pcb:'Task Control Block',
  states:'Process States', scheduler:'CPU Scheduler', compare:'Algorithm Compare', testcases:'Test Cases'
};

function goPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(a => a.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  document.querySelector(`[data-page="${id}"]`).classList.add('active');
  document.getElementById('topbar-title').textContent = PAGE_TITLES[id] || id;
  if (window.innerWidth <= 800) document.getElementById('sidebar').classList.remove('open');
}

document.querySelectorAll('.nav-item').forEach(a => {
  a.addEventListener('click', e => { e.preventDefault(); goPage(a.dataset.page); });
});
document.getElementById('hamburger').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});

// Live clock
function updateClock() {
  const now = new Date();
  document.getElementById('liveTime').textContent =
    now.toTimeString().slice(0,8);
}
updateClock(); setInterval(updateClock, 1000);

// ──────────────────────────────────────────────────────────
// 3. DASHBOARD INIT
// ──────────────────────────────────────────────────────────

function initTaskGrid() {
  const grid = document.getElementById('taskGrid');
  grid.innerHTML = TASK_TYPES.map(t => `
    <div class="task-card">
      <div class="tc-icon-big">${t.icon}</div>
      <div class="tc-name">${t.name}</div>
      <div class="tc-prio ${t.pClass}">${PRIORITY_LABEL[t.priority]}</div>
      <div class="tc-desc">${t.desc}</div>
    </div>`).join('');
}

function initMiniAnim() {
  const el = document.getElementById('miniAnim');
  const icons = ['📦','🚚','🛒','🤖','🔧','📊'];
  let i=0;
  el.textContent = icons[0];
  setInterval(() => { el.textContent = icons[i++ % icons.length]; }, 900);
}

initTaskGrid(); initMiniAnim();

// ──────────────────────────────────────────────────────────
// 4. WAREHOUSE FLOOR SIMULATION
// ──────────────────────────────────────────────────────────

const ZONE_POSITIONS = {
  'Urgent Order Processing': { left:52,  top:48  },
  'Picking':                 { left:200, top:48  },
  'Packing':                 { left:348, top:48  },
  'Dispatch Preparation':    { left:496, top:48  },
  'Inventory Update':        { left:52,  top:238 },
  'Restocking':              { left:200, top:238 },
};
const ZONE_IDS = {
  'Urgent Order Processing':'zone-urgent','Picking':'zone-pick','Packing':'zone-pack',
  'Dispatch Preparation':'zone-dispatch','Inventory Update':'zone-inv','Restocking':'zone-restock'
};

let whTimer = null, whRunning = false;

function warehousePlay() {
  if (whRunning) return;
  whRunning = true;
  document.getElementById('wh-play-btn').textContent = '⏳ Simulating…';
  document.getElementById('wh-log').innerHTML = '';

  const workload = JSON.parse(JSON.stringify(TC.tc3)).sort((a,b) => a.priority - b.priority || a.at - b.at);
  const robot  = document.getElementById('robot');
  const logEl  = document.getElementById('wh-log');
  const status = document.getElementById('whStatusBar');

  const speed = () => Math.max(1, 6 - parseInt(document.getElementById('wh-speed').value));
  let seq = Promise.resolve();

  workload.forEach((task, idx) => {
    seq = seq.then(() => new Promise(resolve => {
      const pos = ZONE_POSITIONS[task.type] || { left:550, top:140 };
      const zid = ZONE_IDS[task.type];

      // Clear all active zones, activate current
      document.querySelectorAll('.wh-zone').forEach(z => z.classList.remove('zone-active'));
      if (zid) document.getElementById(zid).classList.add('zone-active');

      // Move robot to zone centre
      robot.style.left = (pos.left + 44) + 'px';
      robot.style.top  = (pos.top  + 28) + 'px';

      const taskInfo = TASK_TYPES.find(t => t.name === task.type);
      const icon = taskInfo?.icon || '📦';

      // Update status bar
      if (status) status.textContent = `[T=${task.at}] ${icon} ${task.id} → ${task.type} (Prio ${task.priority}) — Burst: ${task.bt}u`;

      addLog(logEl, `[T=${task.at}] ${icon} ${task.id} → ${task.type} (Prio ${task.priority})`, 'log-dispatch');

      // Current task pill
      document.getElementById('wh-current-task').innerHTML = `
        <div class="current-task-pill">
          <span class="ct-icon">${icon}</span>
          <div>
            <div class="ct-title">${task.id} — ${task.type}</div>
            <div class="ct-sub">Burst: ${task.bt} units &nbsp;·&nbsp; ${PRIORITY_LABEL[task.priority]}</div>
          </div>
        </div>`;

      setTimeout(() => {
        const ct = task.at + task.bt;
        addLog(logEl, `[T=${ct}] ✅ ${task.id} completed. CT=${ct}`, 'log-complete');
        resolve();
      }, task.bt * (speed() * 280));
    }));
  });

  seq.then(() => {
    addLog(logEl, '[✓] All warehouse tasks completed.', 'log-complete');
    // Return robot to home position (right side)
    document.querySelectorAll('.wh-zone').forEach(z => z.classList.remove('zone-active'));
    robot.style.left = '';
    robot.style.top  = '';
    if (status) status.textContent = 'Robot idle — all tasks complete ✓';
    document.getElementById('wh-play-btn').textContent = '▶ Start Simulation';
    document.getElementById('wh-current-task').innerHTML = '';
    whRunning = false;
  });
}

function addLog(el, msg, cls) {
  const d = document.createElement('div');
  d.className = 'log-entry ' + cls;
  d.textContent = msg;
  el.appendChild(d);
  el.parentElement.scrollTop = el.parentElement.scrollHeight;
}

function warehouseReset() {
  if (whTimer) clearInterval(whTimer);
  whRunning = false;
  const robot = document.getElementById('robot');
  robot.style.left = '';
  robot.style.top  = '';
  document.querySelectorAll('.wh-zone').forEach(z => z.classList.remove('zone-active'));
  document.getElementById('wh-log').innerHTML = '';
  document.getElementById('wh-current-task').innerHTML = '';
  document.getElementById('wh-play-btn').textContent = '▶ Start Simulation';
  const status = document.getElementById('whStatusBar');
  if (status) status.textContent = 'Robot idle — awaiting task assignment';
}

document.getElementById('wh-speed').addEventListener('input', function() {
  document.getElementById('wh-speed-val').textContent = this.value + 'x';
});

// ──────────────────────────────────────────────────────────
// 5. PCB VIEWER
// ──────────────────────────────────────────────────────────

function initPCBList() {
  const list = document.getElementById('pcbTaskList');
  list.innerHTML = TC.tc3.map((p, i) => {
    const t = TASK_TYPES.find(x => x.name === p.type);
    return `<button class="pcb-task-btn" onclick="showPCB(${i})" id="pcb-btn-${i}">
      <span class="ptb-icon">${t?.icon||'📦'}</span>
      <div class="ptb-info">
        <div class="ptb-name">${p.id} — ${p.type}</div>
        <div class="ptb-sub">AT=${p.at} · BT=${p.bt} · Prio=${p.priority}</div>
      </div>
    </button>`;
  }).join('');
}

function showPCB(i) {
  const p = TC.tc3[i];
  const t = TASK_TYPES.find(x => x.name === p.type);
  document.querySelectorAll('.pcb-task-btn').forEach(b => b.classList.remove('selected'));
  document.getElementById('pcb-btn-'+i).classList.add('selected');

  const stateLabel = 'READY';
  const stateClass = 'ready';

  document.getElementById('pcbViewer').innerHTML = `
    <div class="pcb-header-row">📋 Task Control Block — ${p.id} · ${t?.icon||''} ${p.type}</div>
    ${pcbRow('Process ID (PID)', p.id, 'mono')}
    ${pcbRow('Task Type', p.type)}
    ${pcbRow('Process State', `<span class="pfr-val state-chip ${stateClass}">${stateLabel}</span>`, 'raw')}
    ${pcbRow('Priority', `${p.priority} — ${PRIORITY_LABEL[p.priority]}`)}
    ${pcbRow('Arrival Time (AT)', p.at + ' units')}
    ${pcbRow('Burst Time (BT)', p.bt + ' units')}
    ${pcbRow('Remaining Burst', p.bt + ' units', 'mono')}
    ${pcbRow('Program Counter', '0x00' + (0x401000 + i*0x100).toString(16).toUpperCase(), 'mono')}
    ${pcbRow('Memory Base', '0x' + (0x1000 + i*0x500).toString(16).toUpperCase(), 'mono')}
    ${pcbRow('Open Files', 'stdin, stdout, warehouse.db')}
    ${pcbRow('Parent PID', 'warehouse-scheduler (PID 1)')}
    ${pcbRow('Completion Time (CT)', '—')}
    ${pcbRow('Turnaround Time (TAT)', '—')}
    ${pcbRow('Waiting Time (WT)', '—')}
    ${pcbRow('Response Time (RT)', '—')}
  `;
}

function pcbRow(key, val, cls='') {
  const valHtml = cls === 'raw' ? val : `<span class="pfr-val ${cls}">${val}</span>`;
  return `<div class="pcb-field-row"><span class="pfr-key">${key}</span>${valHtml}</div>`;
}

initPCBList();

// ──────────────────────────────────────────────────────────
// 6. PROCESS STATE DIAGRAM
// ──────────────────────────────────────────────────────────

const STATE_INFO = {
  new: {
    title:'🆕 NEW — Task Submitted',
    desc:'Warehouse task has been received. TCB (PCB) is created and memory is partially allocated. Waiting to be admitted to the Ready Queue.',
    attrs:[['TCB Created','Yes'],['In Ready Queue','Not Yet'],['Robot Active','No'],['Warehouse Action','Order received']]
  },
  ready:{
    title:'✅ READY — In Task Queue',
    desc:'Task is loaded in memory and waiting in the Ready Queue for the robot (CPU) to be allocated by the Short-Term Scheduler.',
    attrs:[['In Queue','Yes'],['Waiting For','Robot (CPU)'],['Scheduler','Short-Term'],['Warehouse Action','Queued for robot']]
  },
  run:{
    title:'▶️ RUNNING — Robot Executing',
    desc:'The robot (CPU) has been dispatched to this task. Program counter is active and burst time is being consumed.',
    attrs:[['Robot Active','Yes'],['PC Active','Yes'],['Can Preempt','Yes (if P1 arrives)'],['Warehouse Action','Robot working on task']]
  },
  done:{
    title:'✅ DONE — Task Terminated',
    desc:'Task fully executed. CT, TAT, WT and RT are calculated and stored. TCB is freed. Warehouse reports task completion.',
    attrs:[['Robot Active','No'],['TCB','Being freed'],['Exit Code','Sent to scheduler'],['Warehouse Action','Order dispatched/done']]
  }
};

function svClick(state) {
  document.querySelectorAll('.sv-node').forEach(n => n.classList.remove('active-sv'));
  document.getElementById('svn-'+state).classList.add('active-sv');
  const info = STATE_INFO[state];
  document.getElementById('statePanel').innerHTML = `
    <div class="sip-title">${info.title}</div>
    <div class="sip-desc">${info.desc}</div>
    ${info.attrs.map(([k,v]) => `<div class="sip-attr"><span class="sip-k">${k}</span><span class="sip-v">${v}</span></div>`).join('')}
  `;
}

// ──────────────────────────────────────────────────────────
// 7. SCHEDULER
// ──────────────────────────────────────────────────────────

function setAlgo(btn) {
  document.querySelectorAll('.algo-pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  currentAlgo = btn.dataset.algo;
  document.getElementById('rrRow').style.display = currentAlgo === 'rr' ? 'flex' : 'none';
  const showPrio = currentAlgo.startsWith('priority');
  document.getElementById('th-prio').style.display = showPrio ? '' : 'none';
  document.querySelectorAll('.prio-td').forEach(td => { td.style.display = showPrio ? '' : 'none'; });
}

function loadPreset(key) {
  tasks = JSON.parse(JSON.stringify(TC[key]));
  pidCounter = tasks.length + 1;
  renderTaskTable();
}

function addTask() {
  tasks.push({ id:'P'+pidCounter++, type:'Picking', at:0, bt:3, priority:2 });
  renderTaskTable();
}

function renderTaskTable() {
  const showPrio = currentAlgo.startsWith('priority');
  const body = document.getElementById('taskBody');
  body.innerHTML = tasks.map((t, i) => `
    <tr>
      <td style="font-family:var(--mono);color:var(--teal);font-weight:700">${t.id}</td>
      <td>
        <select onchange="tasks[${i}].type=this.value;tasks[${i}].priority=getDefaultPrio(this.value)">
          ${TASK_TYPES.map(tt => `<option value="${tt.name}" ${t.type===tt.name?'selected':''}>${tt.icon} ${tt.name}</option>`).join('')}
        </select>
      </td>
      <td><input type="number" value="${t.at}" min="0" max="30" onchange="tasks[${i}].at=+this.value"/></td>
      <td><input type="number" value="${t.bt}" min="1" max="20" onchange="tasks[${i}].bt=+this.value"/></td>
      <td class="prio-td" style="display:${showPrio?'':'none'}">
        <input type="number" value="${t.priority}" min="1" max="3" onchange="tasks[${i}].priority=+this.value"/>
      </td>
      <td><button class="btn-del" onclick="deleteTask(${i})">✕</button></td>
    </tr>`).join('');
  document.getElementById('th-prio').style.display = showPrio ? '' : 'none';
}

function getDefaultPrio(type) {
  const t = TASK_TYPES.find(x => x.name === type);
  return t ? t.priority : 2;
}

function deleteTask(i) { tasks.splice(i,1); renderTaskTable(); }

function resetSim() {
  tasks = []; pidCounter = 1; renderTaskTable();
  document.getElementById('schedRight').innerHTML = `<div class="empty-panel"><div class="ep-icon">📊</div><p>Select algorithm, add tasks, then click <strong>▶ Run Simulation</strong></p></div>`;
}

function runSim() {
  if (!tasks.length) { alert('Add at least one task!'); return; }
  const q = +document.getElementById('quantum').value || 2;
  const result = runAlgorithm(tasks, currentAlgo, q);
  renderOutput(document.getElementById('schedRight'), result, currentAlgo, q, tasks);
}

renderTaskTable();

// ──────────────────────────────────────────────────────────
// 8. ALGORITHMS
// ──────────────────────────────────────────────────────────

function runAlgorithm(procs, algo, q=2) {
  switch(algo) {
    case 'fcfs':        return { gantt: algoFCFS(procs).gantt,       metrics: algoFCFS(procs).metrics };
    case 'sjf':         return { gantt: algoSJF(procs).gantt,        metrics: algoSJF(procs).metrics };
    case 'srtf':        return { gantt: algoSRTF(procs).gantt,       metrics: algoSRTF(procs).metrics };
    case 'rr':          return { gantt: algoRR(procs,q).gantt,       metrics: algoRR(procs,q).metrics };
    case 'priority_np': return { gantt: algoPrioNP(procs).gantt,     metrics: algoPrioNP(procs).metrics };
    case 'priority_p':  return { gantt: algoPrioP(procs).gantt,      metrics: algoPrioP(procs).metrics };
    default:            return { gantt: algoFCFS(procs).gantt,       metrics: algoFCFS(procs).metrics };
  }
}

function algoFCFS(procs) {
  const sorted = [...procs].sort((a,b)=>a.at-b.at);
  const gantt=[], metrics=[];
  let t=0;
  sorted.forEach(p=>{
    if(t<p.at) t=p.at;
    const s=t; t+=p.bt;
    gantt.push({pid:p.id,type:p.type,start:s,end:t});
    metrics.push({...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt,rt:s-p.at});
  });
  return {gantt,metrics};
}

function algoSJF(procs) {
  const gantt=[], metrics=[];
  let t=0, rem=[...procs];
  while(rem.length){
    const av=rem.filter(p=>p.at<=t);
    if(!av.length){t=rem.sort((a,b)=>a.at-b.at)[0].at;continue;}
    av.sort((a,b)=>a.bt-b.bt||a.at-b.at);
    const p=av[0]; rem=rem.filter(x=>x.id!==p.id);
    const s=t; t+=p.bt;
    gantt.push({pid:p.id,type:p.type,start:s,end:t});
    metrics.push({...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt,rt:s-p.at});
  }
  return {gantt,metrics};
}

function algoSRTF(procs) {
  const gantt=[], metricsMap={};
  const rem=procs.map(p=>({...p,r:p.bt,rt:null}));
  let t=0;
  const maxT=procs.reduce((s,p)=>s+p.bt,0)+Math.max(...procs.map(p=>p.at))+1;
  while(t<maxT){
    const av=rem.filter(p=>p.at<=t&&p.r>0);
    if(!av.length){t++;continue;}
    av.sort((a,b)=>a.r-b.r||a.at-b.at);
    const p=av[0];
    if(p.rt===null) p.rt=t-p.at;
    if(gantt.length&&gantt[gantt.length-1].pid===p.id) gantt[gantt.length-1].end=t+1;
    else gantt.push({pid:p.id,type:p.type,start:t,end:t+1});
    p.r--; t++;
    if(p.r===0) metricsMap[p.id]={...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt,rt:p.rt};
  }
  return {gantt, metrics:procs.map(p=>metricsMap[p.id]||{...p,ct:0,tat:0,wt:0,rt:0})};
}

function algoRR(procs,q) {
  const gantt=[], metricsMap={};
  let t=0; const rem=procs.map(p=>({...p,r:p.bt,rt:null}));
  const queue=[]; const added=new Set();
  rem.sort((a,b)=>a.at-b.at);
  rem.filter(p=>p.at===0).forEach(p=>{queue.push(p);added.add(p.id);});
  while(queue.length){
    const p=queue.shift();
    if(p.rt===null) p.rt=t-p.at;
    const ex=Math.min(q,p.r);
    gantt.push({pid:p.id,type:p.type,start:t,end:t+ex});
    t+=ex; p.r-=ex;
    rem.filter(x=>!added.has(x.id)&&x.at<=t).forEach(x=>{queue.push(x);added.add(x.id);});
    if(p.r>0) queue.push(p);
    else metricsMap[p.id]={...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt};
  }
  return {gantt, metrics:procs.map(p=>metricsMap[p.id]||{...p,ct:0,tat:0,wt:0,rt:0})};
}

function algoPrioNP(procs) {
  // Priority 1 = Highest (as per warehouse spec)
  const gantt=[], metrics=[];
  let t=0, rem=[...procs];
  while(rem.length){
    const av=rem.filter(p=>p.at<=t);
    if(!av.length){t=rem.sort((a,b)=>a.at-b.at)[0].at;continue;}
    av.sort((a,b)=>a.priority-b.priority||a.at-b.at);
    const p=av[0]; rem=rem.filter(x=>x.id!==p.id);
    const s=t; t+=p.bt;
    gantt.push({pid:p.id,type:p.type,start:s,end:t});
    metrics.push({...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt,rt:s-p.at});
  }
  return {gantt,metrics};
}

function algoPrioP(procs) {
  const gantt=[], metricsMap={};
  const rem=procs.map(p=>({...p,r:p.bt,rt:null}));
  let t=0;
  const maxT=procs.reduce((s,p)=>s+p.bt,0)+Math.max(...procs.map(p=>p.at))+1;
  while(t<maxT){
    const av=rem.filter(p=>p.at<=t&&p.r>0);
    if(!av.length){t++;continue;}
    av.sort((a,b)=>a.priority-b.priority||a.at-b.at);
    const p=av[0];
    if(p.rt===null) p.rt=t-p.at;
    if(gantt.length&&gantt[gantt.length-1].pid===p.id) gantt[gantt.length-1].end=t+1;
    else gantt.push({pid:p.id,type:p.type,start:t,end:t+1});
    p.r--; t++;
    if(p.r===0) metricsMap[p.id]={...p,ct:t,tat:t-p.at,wt:t-p.at-p.bt,rt:p.rt};
  }
  return {gantt, metrics:procs.map(p=>metricsMap[p.id]||{...p,ct:0,tat:0,wt:0,rt:0})};
}

// ──────────────────────────────────────────────────────────
// 9. RENDER OUTPUT
// ──────────────────────────────────────────────────────────

const ALGO_NAMES = {
  fcfs:'FCFS — First Come First Served',
  sjf:'SJF — Shortest Job First',
  srtf:'SRTF — Shortest Remaining Time',
  rr:'Round Robin',
  priority_np:'Non-Preemptive Priority Scheduling',
  priority_p:'Preemptive Priority Scheduling'
};

function renderOutput(container, result, algo, q, procs) {
  const {gantt, metrics} = result;
  const pidIdx = {}; procs.forEach((p,i)=>pidIdx[p.id]=i);
  const totalT = Math.max(...gantt.map(b=>b.end));

  const avgTAT = avg(metrics.map(m=>m.tat||0));
  const avgWT  = avg(metrics.map(m=>m.wt||0));
  const avgRT  = avg(metrics.map(m=>m.rt||0));

  const ganttBars = gantt.map(b=>{
    const w = ((b.end-b.start)/totalT*100).toFixed(2);
    const c = COLORS[pidIdx[b.pid] % COLORS.length];
    return `<div class="g-block" style="width:${w}%;background:${c};" title="${b.pid} (${b.type}): T${b.start}–T${b.end}">${b.pid}</div>`;
  }).join('');

  // Build axis ticks
  const axisTicks = gantt.map(b=>{
    const w = ((b.end-b.start)/totalT*100).toFixed(2);
    return `<div class="g-tick" style="width:${w}%;">${b.start}</div>`;
  }).join('') + `<div class="g-tick" style="width:0;padding-left:0;">${totalT}</div>`;

  const metricsRows = metrics.map(m=>{
    const t = TASK_TYPES.find(x=>x.name===m.type);
    const pClass = m.priority===1?'p1-bg':m.priority===3?'p3-bg':'p2-bg';
    return `<tr>
      <td style="font-family:var(--mono);font-weight:700;color:var(--teal)">${m.id}</td>
      <td>${t?.icon||''} <span style="font-size:.78rem">${m.type}</span></td>
      <td><span class="prio-chip p${m.priority}" style="font-size:.68rem">${m.priority}</span></td>
      <td>${m.at}</td><td>${m.bt}</td>
      <td style="color:var(--teal);font-weight:700">${m.ct??'—'}</td>
      <td style="color:var(--amber);font-weight:700">${m.tat??'—'}</td>
      <td style="color:var(--p2);font-weight:700">${m.wt??'—'}</td>
      <td style="color:var(--purple);font-weight:700">${m.rt??'—'}</td>
    </tr>`;
  }).join('');

  container.innerHTML = `
    <div class="gantt-section">
      <div class="gantt-heading">
        📊 Gantt Chart
        <span class="algo-badge">${ALGO_NAMES[algo]}${algo==='rr'?' (q='+q+')':''}</span>
      </div>
      <div class="gantt-wrap">
        <div class="gantt-bar">${ganttBars}</div>
      </div>
    </div>
    <div class="metrics-section">
      <div class="gantt-heading">📋 Process Performance Table</div>
      <div class="metrics-table-wrap">
        <table class="metrics-table">
          <thead><tr>
            <th>PID</th><th>Task Type</th><th>Prio</th>
            <th>AT</th><th>BT</th><th>CT</th><th>TAT</th><th>WT</th><th>RT</th>
          </tr></thead>
          <tbody>${metricsRows}</tbody>
        </table>
      </div>
      <div class="summary-boxes">
        <div class="sum-box"><div class="sum-val">${avgTAT}</div><div class="sum-label">Avg Turnaround Time</div></div>
        <div class="sum-box"><div class="sum-val">${avgWT}</div><div class="sum-label">Avg Waiting Time</div></div>
        <div class="sum-box"><div class="sum-val">${avgRT}</div><div class="sum-label">Avg Response Time</div></div>
      </div>
    </div>`;
}

function avg(arr) { return (arr.reduce((s,v)=>s+v,0)/arr.length).toFixed(2); }

// ──────────────────────────────────────────────────────────
// 10. COMPARISON
// ──────────────────────────────────────────────────────────

function loadComparePreset(key, btn) {
  comparePreset = key;
  document.querySelectorAll('.cc-preset-row .qbtn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
}

function runComparison() {
  const procs = JSON.parse(JSON.stringify(TC[comparePreset]));
  const np = algoPrioNP(procs);
  const pp = algoPrioP(procs);

  const npAvg = { tat:avg(np.metrics.map(m=>m.tat||0)), wt:avg(np.metrics.map(m=>m.wt||0)), rt:avg(np.metrics.map(m=>m.rt||0)) };
  const ppAvg = { tat:avg(pp.metrics.map(m=>m.tat||0)), wt:avg(pp.metrics.map(m=>m.wt||0)), rt:avg(pp.metrics.map(m=>m.rt||0)) };

  const out = document.getElementById('compareOutput');

  out.innerHTML = `
    <div class="cmp-side-by-side">
      <div class="cmp-algo-block np-block" id="cmp-np">
        <div class="cmp-title">📋 Non-Preemptive Priority Scheduling</div>
      </div>
      <div class="cmp-algo-block p-block" id="cmp-p">
        <div class="cmp-title">⚡ Preemptive Priority Scheduling</div>
      </div>
    </div>
    <div class="final-compare-table">
      <div class="fct-title">⚖️ Side-by-Side Summary — ${comparePreset.toUpperCase()}</div>
      <table class="fct-table">
        <thead><tr><th>Metric</th><th>Non-Preemptive</th><th>Preemptive</th><th>Winner</th></tr></thead>
        <tbody>
          <tr><td>Avg Turnaround Time (TAT)</td>
            <td>${npAvg.tat}</td><td>${ppAvg.tat}</td>
            <td><span class="winner">${+ppAvg.tat<+npAvg.tat?'⚡ Preemptive':+npAvg.tat<+ppAvg.tat?'📋 Non-Preemptive':'= Tie'}</span></td></tr>
          <tr><td>Avg Waiting Time (WT)</td>
            <td>${npAvg.wt}</td><td>${ppAvg.wt}</td>
            <td><span class="winner">${+ppAvg.wt<+npAvg.wt?'⚡ Preemptive':+npAvg.wt<+ppAvg.wt?'📋 Non-Preemptive':'= Tie'}</span></td></tr>
          <tr><td>Avg Response Time (RT)</td>
            <td>${npAvg.rt}</td><td>${ppAvg.rt}</td>
            <td><span class="winner">${+ppAvg.rt<+npAvg.rt?'⚡ Preemptive':+npAvg.rt<+ppAvg.rt?'📋 Non-Preemptive':'= Tie'}</span></td></tr>
        </tbody>
      </table>
    </div>`;

  // Render gantt+metrics into each block
  renderOutput(document.getElementById('cmp-np'), np, 'priority_np', 2, procs);
  renderOutput(document.getElementById('cmp-p'),  pp, 'priority_p',  2, procs);
}

// ──────────────────────────────────────────────────────────
// 11. TEST CASES PAGE
// ──────────────────────────────────────────────────────────

function goTC(n) {
  const key = 'tc'+n;
  loadPreset(key);
  // set preemptive priority
  document.querySelectorAll('.algo-pill').forEach(p=>p.classList.remove('active'));
  document.querySelector('[data-algo="priority_p"]').classList.add('active');
  currentAlgo = 'priority_p';
  renderTaskTable();
  goPage('scheduler');
}
