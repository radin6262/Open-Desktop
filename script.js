/* --- STATE MANAGEMENT --- */
let pinnedApps = [];
let allApps = [];
let lastDockDataString = ""; // Stores state to prevent "Dancing Icons"
let clickLock = false;       // Prevents loop from overwriting clicks

/* --- BRIDGE --- */
function sendToPython(data) {
    if (window.webkit && window.webkit.messageHandlers.bridge) {
        window.webkit.messageHandlers.bridge.postMessage(JSON.stringify(data));
    }
}

/* --- CLOCK --- */
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById("clock");
    if(clockEl) {
        clockEl.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
}
setInterval(updateClock, 1000);
updateClock();

/* --- START MENU --- */
function toggleStartMenu() {
    const menu = document.getElementById('start-menu');
    const isHidden = menu.classList.toggle('hidden');
    if (!isHidden) {
        const searchInput = document.getElementById('start-search');
        searchInput.value = ""; 
        renderApps(allApps);
        setTimeout(() => searchInput.focus(), 50); 
    }
}

document.getElementById('desktop').addEventListener('click', () => {
    document.getElementById('start-menu').classList.add('hidden');
});

document.getElementById('start-menu').addEventListener('click', (e) => e.stopPropagation());

function filterApps() {
    const query = document.getElementById('start-search').value.toLowerCase();
    const filtered = allApps.filter(app => app.name.toLowerCase().includes(query));
    renderApps(filtered);
}

function renderApps(appsToDisplay) {
    const container = document.getElementById("start-apps-list");
    if (!container) return;
    container.innerHTML = "";
    appsToDisplay.forEach(app => {
        const item = document.createElement("div");
        item.className = "start-app-item";
        item.innerHTML = `<img src="${app.icon || 'assets/generic.png'}" onerror="this.src='assets/generic.png'"> <span>${app.name}</span>`;
        item.onclick = (e) => {
            e.stopPropagation();
            sendToPython({ action: "launch_app", command: app.exec });
            toggleStartMenu();
        };
        container.appendChild(item);
    });
}

/* --- PYTHON RECEIVERS --- */
function receiveDockData(apps) {
    pinnedApps = apps;
    lastDockDataString = ""; // Force refresh on first load
    updateRunningIndicators([]); 
}

function receiveStartMenuApps(apps) {
    allApps = apps;
    renderApps(allApps);
}

function applyBackground(path) {
    document.getElementById('desktop').style.backgroundImage = `url('${path}')`;
}

function receiveSavedBackground(path) { applyBackground(path); }

/* --- THE DOCK LOGIC (FIXED) --- */
function updateRunningIndicators(runningWindows) {
    // 1. If we just clicked, don't let the Python update mess up the UI
    if (clickLock) return;

    const container = document.getElementById("dock-container");
    if (!container) return;

    // 2. State Check: Only rebuild if windows actually changed (Fixes Dancing/Flicker)
    const currentStateString = JSON.stringify(runningWindows) + JSON.stringify(pinnedApps);
    if (currentStateString === lastDockDataString) return;
    lastDockDataString = currentStateString;

    container.innerHTML = "";

    // 3. Render Pinned Apps
    pinnedApps.forEach(app => {
        const win = runningWindows.find(w => 
            app.exec.toLowerCase().includes(w.class.toLowerCase()) || 
            w.class.toLowerCase().includes(app.exec.toLowerCase())
        );

        const isRunning = !!win;
        const isFocused = win && win.focused;

        const appEl = document.createElement("div");
        
        // Logical Classing: Only 'running' (indicator) if NOT currently focused
        let statusClass = "";
        if (isFocused) statusClass = "active";
        else if (isRunning) statusClass = "running";

        appEl.className = `app ${statusClass}`;
        appEl.innerHTML = `<img src="${app.icon_path}" onerror="this.src='assets/generic.png'">`;
        
        appEl.onclick = (e) => {
            e.stopPropagation();
            clickLock = true; // Set lock to prevent flickering during window shift
            
            if (isRunning) {
                // Instant Visual feedback
                if (isFocused) {
                    appEl.classList.remove('active');
                    appEl.classList.add('running');
                } else {
                    appEl.classList.add('active');
                    appEl.classList.remove('running');
                }
                sendToPython({ action: "focus_app_by_command", command: app.exec });
            } else {
                sendToPython({ action: "launch_app", command: app.exec });
                appEl.classList.add('running');
            }

            // Release lock after 450ms (allows OS to finish window state change)
            setTimeout(() => { clickLock = false; }, 450);
        };
        container.appendChild(appEl);
    });

    // 4. Render Unpinned Running Apps
    runningWindows.forEach(win => {
        const isPinned = pinnedApps.some(p => 
            p.exec.toLowerCase().includes(win.class.toLowerCase()) || 
            win.class.toLowerCase().includes(p.exec.toLowerCase())
        );

        if (!isPinned) {
            const appEl = document.createElement("div");
            let statusClass = win.focused ? "active" : "running";
            appEl.className = `app unpinned ${statusClass}`;
            appEl.innerHTML = `<img src="${win.icon || 'assets/generic.png'}" onerror="this.src='assets/generic.png'">`;
            
            appEl.onclick = (e) => {
                e.stopPropagation();
                clickLock = true;
                sendToPython({ action: "focus_app", xid: win.xid });
                setTimeout(() => { clickLock = false; }, 450);
            };
            container.appendChild(appEl);
        }
    });
}

/* --- INITIALIZATION --- */
window.onload = () => {
    sendToPython({ action: "get_dock_apps" });
    sendToPython({ action: "get_start_apps" });
    sendToPython({ action: "get_saved_background" });
};

// Selection Protection
['taskbar-top', 'taskbar-bottom'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('mousedown', e => { if(e.target.tagName !== 'INPUT') e.preventDefault(); });
        el.addEventListener('selectstart', e => { if(e.target.tagName !== 'INPUT') e.preventDefault(); });
    }
});
