const SERVER = "http://127.0.0.1:5000";
const CTRL   = "http://127.0.0.1:5001";

const lastUpdatedEl = document.getElementById("lastUpdated");
const statusBadgeEl = document.getElementById("statusBadge");

function el(id) { return document.getElementById(id); }
function setDot(el, status) { el.classList.remove("dot-ok", "dot-warn", "dot-bad"); el.classList.add(status); }
async function fetchJSON(url) { const r = await fetch(url, { cache: "no-store" }); if (!r.ok) throw new Error(`${r.status} ${r.statusText}`); return await r.json(); }
function formatTime(date = new Date()) { return date.toLocaleTimeString(); }

function createPanel(prefix, vehicleId, color = "#60a5fa") {
	const panel = {
		vehicleId,
		serverHealthEl: el(`${prefix}-serverHealth`),
		ctrlHealthEl: el(`${prefix}-ctrlHealth`),
		badgeEl: el(`${prefix}-badge`),
		serverCard: el(`${prefix}-serverCard`),
		ctrlCard: el(`${prefix}-ctrlCard`),
		trendCard: el(`${prefix}-trendCard`),
		metricDistanceCard: el(`${prefix}-metricDistanceCard`),
		metricBearingCard: el(`${prefix}-metricBearingCard`),
		metricDirectionCard: el(`${prefix}-metricDirectionCard`),
		metricVehicleCard: el(`${prefix}-metricVehicleCard`),
		metricDistance: el(`${prefix}-metricDistance`),
		metricBearing: el(`${prefix}-metricBearing`),
		metricDirection: el(`${prefix}-metricDirection`),
		metricVehicle: el(`${prefix}-metricVehicle`),
		sparkCanvas: el(`${prefix}-sparkline`),
		distances: [],
		lastServerTs: null,
		lastPointAtMs: Date.now(),
		color,
	};
	panel.sparkCtx = panel.sparkCanvas.getContext("2d");
	panel.drawSparkline = function(values) {
		const ctx = this.sparkCtx, w = this.sparkCanvas.width, h = this.sparkCanvas.height;
		ctx.clearRect(0, 0, w, h);
		if (!values.length) return;
		const max = Math.max(...values), min = Math.min(...values), span = Math.max(1, max - min);
		const padL = 44, padR = 12, padT = 12, padB = 24, innerW = w - padL - padR, innerH = h - padT - padB;
		ctx.save();
		ctx.strokeStyle = "rgba(255,255,255,.08)"; ctx.fillStyle = "#93a4bd"; ctx.lineWidth = 1; ctx.font = "12px Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
		for (let i = 0; i <= 4; i++) { const t = i/4; const y = padT + innerH - t*innerH; ctx.beginPath(); ctx.moveTo(padL,y); ctx.lineTo(padL+innerW,y); ctx.stroke(); const val = (min + t*span).toFixed(0); ctx.fillText(`${val} m`, 4, y+4); }
		const n = values.length, step = Math.max(1, Math.floor(n/5));
		for (let i = 0; i <= n; i += step) { const x = padL + (i/Math.max(1,n-1))*innerW; ctx.beginPath(); ctx.moveTo(x,padT); ctx.lineTo(x,padT+innerH); ctx.stroke(); const label = i===n?"now":`-${n-i}`; ctx.fillText(label, Math.max(padL,x-10), h-6); }
		ctx.restore();
		ctx.lineWidth = 2; ctx.strokeStyle = this.color; ctx.beginPath();
		values.forEach((v,i)=>{ const x = padL+(i/Math.max(1,values.length-1))*innerW; const y = padT+innerH-((v-min)/span)*innerH; if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y); });
		ctx.stroke();
	};
panel.setMetricState = function(isPriority){
		[this.metricDistanceCard, this.metricBearingCard, this.metricVehicleCard, this.metricDirectionCard].forEach(elm=>{
			elm.classList.remove("priority", "ok");
			elm.classList.add(isPriority ? "priority" : "ok");
		});
	};
	return panel;
}

const amb = createPanel("amb", "AMB001", "#60a5fa");
const fir = createPanel("fir", "FIRT001", "#22c55e");

async function refresh() {
	try {
		const [ambEvent, firEvent, ctrlState] = await Promise.all([
			fetchJSON(`${SERVER}/api/last_event?id=${amb.vehicleId}`),
			fetchJSON(`${SERVER}/api/last_event?id=${fir.vehicleId}`),
			fetchJSON(`${CTRL}/api/state`),
		]);

		function updatePanel(p, serverEvent) {
			el(`${p === amb ? 'amb' : 'fir'}-serverEvent`).textContent = JSON.stringify(serverEvent, null, 2);
			el(`${p === amb ? 'amb' : 'fir'}-ctrlState`).textContent = JSON.stringify(ctrlState, null, 2);
			const distance = (serverEvent?.distance_m ?? null);
			const bearing = (serverEvent?.bearing ?? null);
			const direction = (ctrlState?.direction ?? serverEvent?.direction ?? "—");
			p.metricDistance.textContent = typeof distance === 'number' ? `${distance.toFixed(1)} m` : '—';
			p.metricBearing.textContent = typeof bearing === 'number' ? `${bearing.toFixed(1)}°` : '—';
			p.metricDirection.textContent = direction;
			p.metricVehicle.textContent = p.vehicleId;
			const serverTs = serverEvent?.ts ?? null;
			if (typeof distance === 'number' && serverTs && serverTs !== p.lastServerTs) {
				p.lastServerTs = serverTs; p.lastPointAtMs = Date.now(); p.distances.push(distance); while (p.distances.length > 50) p.distances.shift();
			}
			p.drawSparkline(p.distances);
			// Per-vehicle priority: based on this vehicle's distance <= threshold and > 1 m (not idle)
			const isPriority = (typeof distance === 'number') && distance > 1 && distance <= THRESHOLD_METERS;
			const priorityClass = (p === amb) ? (isPriority ? "priority-amb" : null) : (isPriority ? "priority-fir" : null);
			p.serverCard.classList.remove("priority", "priority-amb", "priority-fir");
			p.ctrlCard.classList.remove("priority", "priority-amb", "priority-fir");
			if (priorityClass) { p.serverCard.classList.add(priorityClass); p.ctrlCard.classList.add(priorityClass); }
			p.serverCard.classList.add("active"); p.ctrlCard.classList.add("active"); p.trendCard.classList.toggle("active", true);
			setDot(p.serverHealthEl, "dot-ok"); setDot(p.ctrlHealthEl, "dot-ok");
            p.setMetricState(isPriority);
			if (p.badgeEl) {
				const isAmb = (p === amb);
				p.badgeEl.textContent = isPriority ? "PRIORITY" : "NORMAL";
				p.badgeEl.className = `badge ${isAmb ? 'badge-amb' : 'badge-fir'}${isPriority ? ' priority' : ''}`;
			}
			return { priority: isPriority, idle: Date.now() - p.lastPointAtMs > 6000 };
		}

		const ambState = updatePanel(amb, ambEvent);
		const firState = updatePanel(fir, firEvent);

		const anyPriority = ambState.priority || firState.priority;
		const allIdle = ambState.idle && firState.idle;
		if (allIdle) {
			statusBadgeEl.textContent = "PAUSED";
			statusBadgeEl.style.color = "#93a4bd";
			statusBadgeEl.style.background = "rgba(147,164,189,.12)";
			statusBadgeEl.style.borderColor = "rgba(147,164,189,.35)";
		} else {
			statusBadgeEl.textContent = anyPriority ? "PRIORITY" : "NORMAL";
			statusBadgeEl.style.color = anyPriority ? "#f59e0b" : "#22c55e";
			statusBadgeEl.style.background = anyPriority ? "rgba(245,158,11,.15)" : "rgba(34,197,94,.15)";
			statusBadgeEl.style.borderColor = anyPriority ? "rgba(245,158,11,.35)" : "rgba(34,197,94,.35)";
		}
		lastUpdatedEl.textContent = `Updated ${formatTime()}`;
	} catch (e) {
		statusBadgeEl.textContent = "DISCONNECTED";
		statusBadgeEl.style.color = "#ef4444";
		statusBadgeEl.style.background = "rgba(239,68,68,.15)";
		statusBadgeEl.style.borderColor = "rgba(239,68,68,.35)";
	}
}

// Adaptive refresh: slow down when a priority vehicle is near (<= THRESHOLD_METERS)
const THRESHOLD_METERS = 200;
const NORMAL_INTERVAL_MS = 2000;
const SLOW_INTERVAL_MS = 4000; // slower updates so the trend progresses clearly

let currentTimer = null;
let lastDistances = { amb: Infinity, fir: Infinity };

async function adaptiveLoop() {
	try {
        // Reuse refresh logic but also capture latest distances to decide next delay
        const [ambEvent, firEvent, ctrlState] = await Promise.all([
            fetchJSON(`${SERVER}/api/last_event?id=${amb.vehicleId}`),
            fetchJSON(`${SERVER}/api/last_event?id=${fir.vehicleId}`),
            fetchJSON(`${CTRL}/api/state`),
        ]);

        function updatePanel(p, serverEvent) {
            el(`${p === amb ? 'amb' : 'fir'}-serverEvent`).textContent = JSON.stringify(serverEvent, null, 2);
            el(`${p === amb ? 'amb' : 'fir'}-ctrlState`).textContent = JSON.stringify(ctrlState, null, 2);
            const distance = (serverEvent?.distance_m ?? null);
            const bearing = (serverEvent?.bearing ?? null);
            const direction = (ctrlState?.direction ?? serverEvent?.direction ?? "—");
            p.metricDistance.textContent = typeof distance === 'number' ? `${distance.toFixed(1)} m` : '—';
            p.metricBearing.textContent = typeof bearing === 'number' ? `${bearing.toFixed(1)}°` : '—';
            p.metricDirection.textContent = direction;
            p.metricVehicle.textContent = p.vehicleId;
            const serverTs = serverEvent?.ts ?? null;
            if (typeof distance === 'number' && serverTs && serverTs !== p.lastServerTs) {
                p.lastServerTs = serverTs; p.lastPointAtMs = Date.now(); p.distances.push(distance); while (p.distances.length > 50) p.distances.shift();
            }
            p.drawSparkline(p.distances);
            const isPriority = (typeof distance === 'number') && distance > 1 && distance <= THRESHOLD_METERS;
            const priorityClass = (p === amb) ? (isPriority ? "priority-amb" : null) : (isPriority ? "priority-fir" : null);
            p.serverCard.classList.remove("priority", "priority-amb", "priority-fir");
            p.ctrlCard.classList.remove("priority", "priority-amb", "priority-fir");
            if (priorityClass) { p.serverCard.classList.add(priorityClass); p.ctrlCard.classList.add(priorityClass); }
            p.serverCard.classList.add("active"); p.ctrlCard.classList.add("active"); p.trendCard.classList.toggle("active", true);
            setDot(p.serverHealthEl, "dot-ok"); setDot(p.ctrlHealthEl, "dot-ok");
            p.setMetricState(isPriority);
            if (p.badgeEl) {
                const isAmb = (p === amb);
                p.badgeEl.textContent = isPriority ? "PRIORITY" : "NORMAL";
                p.badgeEl.className = `badge ${isAmb ? 'badge-amb' : 'badge-fir'}${isPriority ? ' priority' : ''}`;
            }
            return { distance, priority: isPriority, idle: Date.now() - p.lastPointAtMs > 6000 };
        }

        const ambState = updatePanel(amb, ambEvent);
        const firState = updatePanel(fir, firEvent);

        const anyPriority = ambState.priority || firState.priority;
        const allIdle = ambState.idle && firState.idle;
        if (allIdle) {
            statusBadgeEl.textContent = "PAUSED";
            statusBadgeEl.style.color = "#93a4bd";
            statusBadgeEl.style.background = "rgba(147,164,189,.12)";
            statusBadgeEl.style.borderColor = "rgba(147,164,189,.35)";
        } else {
            statusBadgeEl.textContent = anyPriority ? "PRIORITY" : "NORMAL";
            statusBadgeEl.style.color = anyPriority ? "#f59e0b" : "#22c55e";
            statusBadgeEl.style.background = anyPriority ? "rgba(245,158,11,.15)" : "rgba(34,197,94,.15)";
            statusBadgeEl.style.borderColor = anyPriority ? "rgba(245,158,11,.35)" : "rgba(34,197,94,.35)";
        }
        lastUpdatedEl.textContent = `Updated ${formatTime()}`;

        lastDistances.amb = typeof ambState.distance === 'number' ? ambState.distance : Infinity;
        lastDistances.fir = typeof firState.distance === 'number' ? firState.distance : Infinity;

    } catch (e) {
        statusBadgeEl.textContent = "DISCONNECTED";
        statusBadgeEl.style.color = "#ef4444";
        statusBadgeEl.style.background = "rgba(239,68,68,.15)";
        statusBadgeEl.style.borderColor = "rgba(239,68,68,.35)";
        lastDistances.amb = lastDistances.fir = Infinity;
    } finally {
        const nearest = Math.min(lastDistances.amb, lastDistances.fir);
        const delay = nearest <= THRESHOLD_METERS ? SLOW_INTERVAL_MS : NORMAL_INTERVAL_MS;
        currentTimer = setTimeout(adaptiveLoop, delay);
    }
}

// start the adaptive loop
adaptiveLoop();