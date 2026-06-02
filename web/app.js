// Custom high-performance HTML5 Canvas Time-Series Chart Class
class TimeSeriesChart {
    constructor(canvasId, options) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = Object.assign({
            maxPoints: 80,
            colors: ['#6366f1'],
            minY: 0.0,
            maxY: 1.0,
            gridCount: 5,
            glow: true
        }, options);
        this.data = []; // Contains items like: { label: 't1', values: [0.55, 0.45] }
        
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.draw();
    }

    clear() {
        this.data = [];
        this.draw();
    }

    addData(label, values) {
        this.data.push({ label, values });
        if (this.data.length > this.options.maxPoints) {
            this.data.shift();
        }
        this.draw();
    }

    draw() {
        const ctx = this.ctx;
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;

        ctx.clearRect(0, 0, width, height);
        if (width === 0 || height === 0) return;

        // Margins/Padding
        const paddingLeft = 45;
        const paddingRight = 15;
        const paddingTop = 20;
        const paddingBottom = 25;

        const chartWidth = width - paddingLeft - paddingRight;
        const chartHeight = height - paddingTop - paddingBottom;

        const minY = this.options.minY;
        const maxY = this.options.maxY;

        // Draw Horizontal Gridlines & Y-Axis Labels
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        ctx.font = '10px monospace';
        ctx.fillStyle = '#64748b';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';

        for (let i = 0; i <= this.options.gridCount; i++) {
            const ratio = i / this.options.gridCount;
            const y = paddingTop + chartHeight * (1 - ratio);
            const val = minY + (maxY - minY) * ratio;

            ctx.beginPath();
            ctx.moveTo(paddingLeft, y);
            ctx.lineTo(width - paddingRight, y);
            ctx.stroke();

            ctx.fillText(val.toFixed(2), paddingLeft - 8, y);
        }

        // Draw Empty State Placeholder
        if (this.data.length === 0) {
            ctx.textAlign = 'center';
            ctx.font = '13px sans-serif';
            ctx.fillStyle = '#475569';
            ctx.fillText('Awaiting data stream...', paddingLeft + chartWidth / 2, paddingTop + chartHeight / 2);
            return;
        }

        // X Coordinate Helper (scrolling right-aligned)
        const getX = (index) => {
            if (this.data.length <= 1) return paddingLeft + chartWidth / 2;
            const maxIdx = this.options.maxPoints - 1;
            const shift = maxIdx - (this.data.length - 1);
            return paddingLeft + chartWidth * ((index + shift) / maxIdx);
        };

        // Y Coordinate Helper
        const getY = (val) => {
            const clamped = Math.max(minY, Math.min(maxY, val));
            const ratio = (clamped - minY) / (maxY - minY);
            return paddingTop + chartHeight * (1 - ratio);
        };

        // Draw X-Axis Timestep Labels (every 10 units)
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = '#475569';

        const labelInterval = Math.max(5, Math.ceil(this.data.length / 6));
        for (let i = 0; i < this.data.length; i++) {
            const stepNum = parseInt(this.data[i].label.substring(1));
            if (stepNum % labelInterval === 0 || i === 0 || i === this.data.length - 1) {
                ctx.fillText(this.data[i].label, getX(i), height - paddingBottom + 6);
            }
        }

        // Draw Datasets
        const numDatasets = this.data[0].values.length;
        for (let d = 0; d < numDatasets; d++) {
            const color = this.options.colors[d % this.options.colors.length];

            // 1. Draw Area Gradient
            ctx.beginPath();
            ctx.moveTo(getX(0), getY(this.data[0].values[d]));
            for (let i = 1; i < this.data.length; i++) {
                ctx.lineTo(getX(i), getY(this.data[i].values[d]));
            }
            ctx.lineTo(getX(this.data.length - 1), getY(minY));
            ctx.lineTo(getX(0), getY(minY));
            ctx.closePath();

            const areaGrad = ctx.createLinearGradient(0, paddingTop, 0, height - paddingBottom);
            areaGrad.addColorStop(0, color + '20'); // ~12% opacity
            areaGrad.addColorStop(1, color + '00'); // Transparent
            ctx.fillStyle = areaGrad;
            ctx.fill();

            // 2. Draw Line Path
            ctx.beginPath();
            ctx.moveTo(getX(0), getY(this.data[0].values[d]));
            for (let i = 1; i < this.data.length; i++) {
                ctx.lineTo(getX(i), getY(this.data[i].values[d]));
            }
            ctx.strokeStyle = color;
            ctx.lineWidth = 2.5;
            if (this.options.glow) {
                ctx.shadowBlur = 6;
                ctx.shadowColor = color;
            }
            ctx.stroke();
            ctx.shadowBlur = 0; // Reset shadow blur

            // 3. Draw Active Glow Point at the endpoint
            const lastIdx = this.data.length - 1;
            const endX = getX(lastIdx);
            const endY = getY(this.data[lastIdx].values[d]);

            ctx.beginPath();
            ctx.arc(endX, endY, 4.5, 0, 2 * Math.PI);
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = color;
            ctx.lineWidth = 2.5;
            ctx.fill();
            ctx.stroke();
        }
    }
}

// Initialize Charts
const chartDem = new TimeSeriesChart('chart-democratic-index', {
    colors: ['#6366f1', '#f43f5e'],
    maxPoints: 80,
    minY: 0.0,
    maxY: 1.0
});

const chartSocEco = new TimeSeriesChart('chart-social-economic', {
    colors: ['#10b981', '#06b6d4'],
    maxPoints: 80,
    minY: 0.0,
    maxY: 1.0
});

const chartParams = new TimeSeriesChart('chart-parameter-drift', {
    colors: ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ef4444'],
    maxPoints: 80,
    minY: 0.0,
    maxY: 1.0
});

// State Management
let eventSource = null;
let isRunning = false;
let totalDecisions = 0;

// Element Selections
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnReset = document.getElementById('btn-reset');

const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

const metricStep = document.getElementById('metric-step');
const metricIndex = document.getElementById('metric-index');
const metricRisk = document.getElementById('metric-risk');
const metricDecisions = document.getElementById('metric-decisions');

const decisionFeedList = document.getElementById('decision-feed-list');
const consoleLog = document.getElementById('console-log');

// Select Slider Parameters
const sliders = [
    { el: document.getElementById('slider-soul-count'), val: document.getElementById('val-soul-count'), format: (v) => v },
    { el: document.getElementById('slider-trust'), val: document.getElementById('val-trust'), format: (v) => parseFloat(v).toFixed(2) },
    { el: document.getElementById('slider-altruism'), val: document.getElementById('val-altruism'), format: (v) => parseFloat(v).toFixed(2) },
    { el: document.getElementById('slider-ambition'), val: document.getElementById('val-ambition'), format: (v) => parseFloat(v).toFixed(2) },
    { el: document.getElementById('slider-curiosity'), val: document.getElementById('val-curiosity'), format: (v) => parseFloat(v).toFixed(2) },
    { el: document.getElementById('slider-fear'), val: document.getElementById('val-fear'), format: (v) => parseFloat(v).toFixed(2) },
    { el: document.getElementById('slider-lr'), val: document.getElementById('val-lr'), format: (v) => parseFloat(v).toFixed(3) },
    { el: document.getElementById('slider-delay'), val: document.getElementById('val-delay'), format: (v) => parseFloat(v).toFixed(2) }
];

// Initialize Sliders
sliders.forEach(s => {
    s.el.addEventListener('input', (e) => {
        s.val.textContent = s.format(e.target.value);
    });
});

// Logger
function logConsole(message, type = '') {
    const line = document.createElement('div');
    line.className = 'console-line';
    if (type) line.classList.add(`text-${type}`);
    line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    consoleLog.appendChild(line);
    consoleLog.scrollTop = consoleLog.scrollHeight;
}

// Toggle Parameter Inputs state
function toggleInputs(disabled) {
    sliders.forEach(s => {
        s.el.disabled = disabled;
    });
}

// Inject Active Decisions
function addDecision(decision) {
    totalDecisions++;
    metricDecisions.textContent = totalDecisions;

    // Remove placeholder
    const placeholder = decisionFeedList.querySelector('.empty-feed-placeholder');
    if (placeholder) {
        decisionFeedList.removeChild(placeholder);
    }

    const item = document.createElement('div');
    item.className = 'feed-item';

    let priClass = 'pri-low';
    let priLabel = 'Low';
    if (decision.priority === 3) {
        priClass = 'pri-medium';
        priLabel = 'Med';
    } else if (decision.priority >= 4) {
        priClass = 'pri-high';
        priLabel = 'High';
    }

    item.innerHTML = `
        <span class="col-id">${decision.id}</span>
        <span class="col-type">${decision.type.replace(/_/g, ' ')}</span>
        <span class="col-pri"><span class="pri-badge ${priClass}">${priLabel}</span></span>
        <span class="col-action">${decision.action}</span>
        <span class="col-rationale" title="${decision.rationale}">${decision.rationale}</span>
    `;

    decisionFeedList.insertBefore(item, decisionFeedList.firstChild);
    logConsole(`Policy recommendation triggered: ${decision.id} - ${decision.action}`, 'orange');
}

// Controller Actions
function startSimulation() {
    if (isRunning) return;

    isRunning = true;
    btnStart.disabled = true;
    btnPause.disabled = false;
    btnStart.textContent = 'Simulating...';

    statusDot.className = 'status-dot running';
    statusText.textContent = 'SYSTEM RUNNING';

    // Gather values
    const soulCount = document.getElementById('slider-soul-count').value;
    const trust = document.getElementById('slider-trust').value;
    const altruism = document.getElementById('slider-altruism').value;
    const ambition = document.getElementById('slider-ambition').value;
    const curiosity = document.getElementById('slider-curiosity').value;
    const fear = document.getElementById('slider-fear').value;
    const lr = document.getElementById('slider-lr').value;
    const delay = document.getElementById('slider-delay').value;

    const query = `soulCount=${soulCount}&trustWeight=${trust}&altruismWeight=${altruism}&ambitionWeight=${ambition}&curiosityWeight=${curiosity}&fearWeight=${fear}&learningRate=${lr}&delay=${delay}&steps=1000`;

    logConsole('Establishing connection to simulation data stream...');
    toggleInputs(true);

    eventSource = new EventSource(`/api/run?${query}`);

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // Update Metrics Readouts
            metricStep.textContent = data.timestep;
            metricIndex.textContent = data.overall_index.toFixed(3);
            metricRisk.textContent = data.collapse_risk.toFixed(3);

            // Add points to charts
            chartDem.addData(data.timestep, [data.overall_index, data.collapse_risk]);
            chartSocEco.addData(data.timestep, [data.social_cohesion, data.economic_health]);
            chartParams.addData(data.timestep, [
                data.trust_weight,
                data.altruism_weight,
                data.ambition_weight,
                data.curiosity_weight,
                data.fear_weight
            ]);

            // Console output optimization (log every 25 timesteps to prevent clutter)
            const stepNum = parseInt(data.timestep.substring(1));
            if (stepNum % 25 === 0 || stepNum === 1) {
                logConsole(`Step ${data.timestep}: Democratic Index = ${data.overall_index.toFixed(3)}, Collapse Risk = ${data.collapse_risk.toFixed(3)}`);
            }

            // Append triggered decisions
            if (data.decisions && data.decisions.length > 0) {
                data.decisions.forEach(d => addDecision(d));
            }

        } catch (e) {
            logConsole(`Error parsing simulation stream chunk: ${e}`, 'red');
        }
    };

    eventSource.onerror = (error) => {
        if (eventSource.readyState === EventSource.CLOSED) {
            logConsole('Simulation stream connection closed.');
            stopSimulation();
        } else {
            logConsole('Stream encountered a connection drop. Reconnecting...', 'red');
        }
    };
}

function pauseSimulation() {
    if (!isRunning) return;

    logConsole('Simulation paused. Connection closed.');
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    isRunning = false;
    btnStart.disabled = false;
    btnStart.textContent = 'Resume Simulation';
    btnPause.disabled = true;

    statusDot.className = 'status-dot paused';
    statusText.textContent = 'SYSTEM PAUSED';
    toggleInputs(false);
}

function stopSimulation() {
    isRunning = false;
    btnStart.disabled = false;
    btnStart.textContent = 'Start Simulation';
    btnPause.disabled = true;

    statusDot.className = 'status-dot idle';
    statusText.textContent = 'SYSTEM IDLE';

    toggleInputs(false);
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }
}

function resetSimulation() {
    stopSimulation();

    // Reset readouts
    metricStep.textContent = 't--';
    metricIndex.textContent = '0.000';
    metricRisk.textContent = '0.000';
    metricDecisions.textContent = '0';
    totalDecisions = 0;

    // Reset charts
    chartDem.clear();
    chartSocEco.clear();
    chartParams.clear();

    // Reset lists
    decisionFeedList.innerHTML = '<div class="empty-feed-placeholder">No policy decisions triggered yet. Start the simulation.</div>';
    consoleLog.innerHTML = '<div class="console-line text-muted">[system] Dashboard reset. Awaiting connection...</div>';

    logConsole('Simulator reset. Ready.');
}

// Wire Event Listeners
btnStart.addEventListener('click', startSimulation);
btnPause.addEventListener('click', pauseSimulation);
btnReset.addEventListener('click', resetSimulation);

logConsole('Dashboard initialized. Adjust parameters and click "Start Simulation".');
