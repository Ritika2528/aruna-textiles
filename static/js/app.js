/*
  app.js
  Shared client-side logic for the Production Monitoring demo.
  - Supports navigation between pages
  - Provides a simple "login" mechanism without a backend
  - Stores sample data in localStorage so it persists between reloads
  - Provides reusable helpers for rendering tables and stats
*/

const App = (function () {
  const STORAGE_KEY = {
    loggedIn: 'pm_logged_in',
  };

  // ── API base (same origin) ────────────────────────────────────────────────
  const API = {
    customers:    '/api/customers',
    production:   '/api/production',
    sales:        '/api/sales',
    stats:        '/api/stats',
    notifications:'/api/notifications',
    suppliers:    '/api/suppliers',
    shipments:    '/api/shipments',
    inventory:    '/api/inventory',
    transactions: '/api/transactions',
    workforce:    '/api/workforce',
  };

  // ── Generic fetch helpers ─────────────────────────────────────────────────
  const apiFetch = async (url, opts = {}) => {
    try {
      const res = await fetch(url, {
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        ...opts,
      });
      if (res.status === 401) {
        localStorage.removeItem(STORAGE_KEY.loggedIn);
        if (!window.location.pathname.endsWith('login.html')) {
          window.location.href = 'login.html';
        }
        throw new Error('Authentication required. Please log in.');
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || res.statusText);
      }
      return await res.json();
    } catch (err) {
      if (err.message && err.message.includes('Authentication required')) throw err;
      console.warn("API unreachable, falling back to localStorage for:", url);
      
      const parts = url.replace('/api/', '').split('/');
      const resourceName = parts[0];
      const resourceId = parts.length > 1 ? parts[1] : null;
      const storageKey = `pm_fallback_${resourceName}`;
      
      let data = JSON.parse(localStorage.getItem(storageKey) || '[]');
      const method = opts.method || 'GET';
      
      if (method === 'GET') {
        if (resourceId) return data.find(d => String(d.id) === String(resourceId));
        return data;
      }
      
      if (method === 'POST') {
        const newItem = JSON.parse(opts.body);
        if (!newItem.id) newItem.id = Date.now();
        data.push(newItem);
        localStorage.setItem(storageKey, JSON.stringify(data));
        return newItem;
      }
      
      if (method === 'PUT') {
        const updateItem = JSON.parse(opts.body);
        data = data.map(d => String(d.id) === String(resourceId) ? { ...d, ...updateItem } : d);
        localStorage.setItem(storageKey, JSON.stringify(data));
        return updateItem;
      }
      
      if (method === 'DELETE') {
        data = data.filter(d => String(d.id) !== String(resourceId));
        localStorage.setItem(storageKey, JSON.stringify(data));
        return { success: true };
      }
      
      throw err;
    }
  };

  // ── Customers ─────────────────────────────────────────────────────────────
  const getCustomers = () => apiFetch(API.customers);

  const saveCustomers = async (customers) => {
    // saveCustomers is called with the full array after a local delete.
    // We map deletes: find which IDs were removed vs the DB.
    const remote = await getCustomers();
    const localIds = new Set(customers.map(c => c.id));
    const toDelete = remote.filter(r => !localIds.has(r.id));
    await Promise.all(toDelete.map(r => apiFetch(`${API.customers}/${r.id}`, { method: 'DELETE' })));
  };

  const addCustomer = (customer) => apiFetch(API.customers, {
    method: 'POST', body: JSON.stringify(customer),
  });

  const deleteCustomer = (id) => apiFetch(`${API.customers}/${id}`, { method: 'DELETE' });

  const updateCustomer = (id, data) => apiFetch(`${API.customers}/${id}`, {
    method: 'PUT', body: JSON.stringify(data),
  });

  // ── Production ────────────────────────────────────────────────────────────
  const getProduction = () => apiFetch(API.production);

  const saveProduction = async (production) => {
    const remote = await getProduction();
    const localIds = new Set(production.map(p => p.id));
    const toDelete = remote.filter(r => !localIds.has(r.id));
    await Promise.all(toDelete.map(r => apiFetch(`${API.production}/${r.id}`, { method: 'DELETE' })));
  };

  const addProduction = (record) => apiFetch(API.production, {
    method: 'POST', body: JSON.stringify(record),
  });

  const deleteProduction = (id) => apiFetch(`${API.production}/${id}`, { method: 'DELETE' });

  const updateProduction = (id, data) => apiFetch(`${API.production}/${id}`, {
    method: 'PUT', body: JSON.stringify(data),
  });

  // ── Sales ─────────────────────────────────────────────────────────────────
  const getSales = () => apiFetch(API.sales);

  const saveSales = async (sales) => {
    const remote = await getSales();
    const localIds = new Set(sales.map(s => s.id));
    const toDelete = remote.filter(r => !localIds.has(r.id));
    await Promise.all(toDelete.map(r => apiFetch(`${API.sales}/${r.id}`, { method: 'DELETE' })));
  };

  const addSale = (sale) => apiFetch(API.sales, {
    method: 'POST', body: JSON.stringify(sale),
  });

  const deleteSale = (id) => apiFetch(`${API.sales}/${id}`, { method: 'DELETE' });

  const updateSale = (id, data) => apiFetch(`${API.sales}/${id}`, {
    method: 'PUT', body: JSON.stringify(data),
  });

  // ── Stats ─────────────────────────────────────────────────────────────────
  const getStats = () => apiFetch(API.stats);

  // ── Suppliers ─────────────────────────────────────────────────────────────
  const getSuppliers = () => apiFetch(API.suppliers);
  const addSupplier = (supplier) => apiFetch(API.suppliers, {
    method: 'POST', body: JSON.stringify(supplier),
  });
  const deleteSupplier = (id) => apiFetch(`${API.suppliers}/${id}`, { method: 'DELETE' });

  // ── Shipments ─────────────────────────────────────────────────────────────
  const getShipments = () => apiFetch(API.shipments);
  const addShipment = (shipment) => apiFetch(API.shipments, {
    method: 'POST', body: JSON.stringify(shipment),
  });
  const deleteShipment = (id) => apiFetch(`${API.shipments}/${id}`, { method: 'DELETE' });

  // ── Inventory ─────────────────────────────────────────────────────────────
  const getInventory = () => apiFetch(API.inventory);
  const addInventoryItem = (item) => apiFetch(API.inventory, {
    method: 'POST', body: JSON.stringify(item),
  });
  const deleteInventoryItem = (category, id) => apiFetch(`${API.inventory}/${category}/${id}`, { method: 'DELETE' });

  // ── Transactions ──────────────────────────────────────────────────────────
  const getTransactions = () => apiFetch(API.transactions);
  const addTransaction = (txn) => apiFetch(API.transactions, {
    method: 'POST', body: JSON.stringify(txn),
  });
  const deleteTransaction = (id) => apiFetch(`${API.transactions}/${id}`, { method: 'DELETE' });

  // ── Workforce ─────────────────────────────────────────────────────────────
  const getWorkforce = () => apiFetch(API.workforce);
  const addOperator = (op) => apiFetch(`${API.workforce}/operator`, {
    method: 'POST', body: JSON.stringify(op),
  });
  const saveAttendance = (data) => apiFetch(`${API.workforce}/attendance`, {
    method: 'PUT', body: JSON.stringify(data),
  });
  const saveShifts = (data) => apiFetch(`${API.workforce}/shifts`, {
    method: 'PUT', body: JSON.stringify(data),
  });

  // ── Legacy helpers (kept for backward compatibility) ──────────────────────
  const initStorage = () => {}; // no-op — DB is remote now

  const getNextId = (items) => {
    if (!items || items.length === 0) return 1;
    return Math.max(...items.map(i => i.id || 0)) + 1;
  };

  const isLoggedIn = () => {
    return localStorage.getItem(STORAGE_KEY.loggedIn) === 'true';
  };

  const getMe = async () => {
    try {
      const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
      if (res.ok) {
        const data = await res.json();
        return data.user;
      }
    } catch(e) {}
    return null;
  };

  const login = async (username, password) => {
    const u = (username || '').trim();
    const p = (password || '');
    if (!u || !p) return { success: false, error: 'Username and password are required.' };

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        return { success: false, error: data.error || 'Invalid credentials' };
      }
      localStorage.setItem(STORAGE_KEY.loggedIn, 'true');
      if (data.user) {
        localStorage.setItem('pm_user', JSON.stringify(data.user));
      }
      return { success: true, user: data.user };
    } catch (err) {
      console.warn("Server login request failed, falling back to local credentials:", err);
      // Resilient fallback for standalone offline demos
      const validUser = u.toLowerCase() === 'admin' && (p === 'admin123' || p === '12345' || p === 'admin');
      if (validUser) {
        localStorage.setItem(STORAGE_KEY.loggedIn, 'true');
        return { success: true, user: { username: 'admin', role: 'admin' } };
      }
      return { success: false, error: 'Authentication failed. Please verify credentials.' };
    }
  };

  const quickLogin = async () => {
    const res = await login('admin', 'admin123');
    if (res.success) {
      window.location.href = 'dashboard.html';
    }
    return res;
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
    } catch(e) {}
    localStorage.removeItem(STORAGE_KEY.loggedIn);
    localStorage.removeItem('pm_user');
    window.location.href = 'login.html';
  };

  const requireLogin = async () => {
    if (!isLoggedIn()) {
      window.location.href = 'login.html';
      return;
    }
    // Verify session with server asynchronously
    try {
      const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
      if (res.status === 401) {
        localStorage.removeItem(STORAGE_KEY.loggedIn);
        window.location.href = 'login.html';
      }
    } catch(e) {
      // offline development mode
    }
  };

  const redirectIfLoggedIn = async () => {
    if (isLoggedIn()) {
      try {
        const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
        if (res.ok) {
          window.location.href = 'dashboard.html';
        } else {
          localStorage.removeItem(STORAGE_KEY.loggedIn);
        }
      } catch (e) {
        window.location.href = 'dashboard.html';
      }
    }
  };

  const renderTable = ({ containerId, rows, columns }) => {
    const body = document.getElementById(containerId);
    if (!body) return;

    body.innerHTML = '';
    rows.forEach(row => {
      const tr = document.createElement('tr');
      columns.forEach(col => {
        const td = document.createElement('td');
        const value = typeof col.value === 'function' ? col.value(row) : row[col.value];
        td.textContent = value ?? '';
        tr.appendChild(td);
      });
      if (columns.some(col => col.actions)) {
        const actionCell = document.createElement('td');
        columns
          .filter(col => col.actions)
          .forEach(col => {
            const button = document.createElement('button');
            button.className = 'btn-secondary btn-sm';
            button.textContent = col.actions.label;
            button.addEventListener('click', () => col.actions.onClick(row));
            actionCell.appendChild(button);
          });
        tr.appendChild(actionCell);
      }
      body.appendChild(tr);
    });
  };

  // Theme Management
  const THEME_KEYS = ['app-theme', 'pm_theme'];
  let inMemoryTheme = null;

  const getSavedTheme = () => {
    try {
      for (const key of THEME_KEYS) {
        const val = localStorage.getItem(key);
        if (val === 'light' || val === 'dark') return val;
      }
    } catch (e) {
      console.warn("localStorage inaccessible for theme:", e);
    }
    return inMemoryTheme;
  };

  const getTheme = () => {
    const saved = getSavedTheme();
    if (saved) return saved;
    // Follow OS preference if available, fallback to Light Mode (default reference)
    try {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    } catch (e) {}
    return 'light';
  };

  const syncChartJsDefaults = (theme) => {
    if (typeof Chart !== 'undefined' && Chart.defaults) {
      const isDark = theme === 'dark';
      const textColor = isDark ? '#C1C4BA' : '#57534A';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(107, 91, 65, 0.12)';
      try {
        if (Chart.defaults.color !== undefined) Chart.defaults.color = textColor;
        if (Chart.defaults.borderColor !== undefined) Chart.defaults.borderColor = gridColor;
        if (Chart.defaults.plugins && Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
          Chart.defaults.plugins.legend.labels.color = textColor;
        }
      } catch (e) {}
    }
  };

  const setTheme = (theme) => {
    inMemoryTheme = theme;
    try {
      THEME_KEYS.forEach(k => localStorage.setItem(k, theme));
    } catch (e) {
      console.warn("Unable to persist theme to localStorage:", e);
    }
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.dataset.theme = theme;
    updateThemeToggleUI(theme);
    syncChartJsDefaults(theme);
    try {
      window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    } catch (e) {}
  };

  const toggleTheme = () => {
    const current = getTheme();
    const newTheme = current === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  };

  const updateThemeToggleUI = (theme) => {
    const btns = document.querySelectorAll('#themeToggleBtn, .theme-toggle-btn');
    if (!btns || btns.length === 0) return;
    
    btns.forEach(btn => {
      const isDark = theme === 'dark';
      btn.setAttribute('aria-label', `Current theme: ${isDark ? 'Dark' : 'Light'} Mode. Click to toggle theme.`);
      btn.setAttribute('title', `Switch to ${isDark ? 'Light' : 'Dark'} Mode`);
      btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
      
      const icon = btn.querySelector('i');
      if (icon) {
        if (isDark) {
          icon.className = 'fas fa-moon';
        } else {
          icon.className = 'fas fa-sun';
        }
      }
    });
  };

  const initTheme = () => {
    const theme = getTheme();
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.dataset.theme = theme;
    syncChartJsDefaults(theme);
    
    const bindToggle = () => {
      updateThemeToggleUI(theme);
      const btns = document.querySelectorAll('#themeToggleBtn, .theme-toggle-btn');
      btns.forEach(btn => {
        btn.removeEventListener('click', toggleTheme);
        btn.addEventListener('click', toggleTheme);
      });
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', bindToggle);
    } else {
      bindToggle();
    }
  };

  // Run theme initialization immediately
  initTheme();

  // ==================== IN-APP SMARTPHONE NOTIFICATIONS ====================
  let localNotifications = [];
  let isSoundEnabled = localStorage.getItem('pm_notif_sound') !== 'false';
  let ws = null;
  let wsReconnectTimer = null;
  let simulatedTimer = null;

  const playChime = () => {
    if (!isSoundEnabled) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const now = ctx.currentTime;
      
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(587.33, now); // D5
      osc1.frequency.exponentialRampToValueAtTime(880, now + 0.12); // A5
      
      gain1.gain.setValueAtTime(0.08, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.3);
      
      setTimeout(() => {
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(880, ctx.currentTime); // A5
        osc2.frequency.exponentialRampToValueAtTime(1174.66, ctx.currentTime + 0.15); // D6
        
        gain2.gain.setValueAtTime(0.08, ctx.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
        
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start();
        osc2.stop(ctx.currentTime + 0.4);
      }, 70);
    } catch (e) {
      console.warn("AudioContext chime error: ", e);
    }
  };

  const getNotifIcon = (type) => {
    switch(type) {
      case 'success': return 'fa-check-circle';
      case 'warning': return 'fa-exclamation-triangle';
      case 'error': return 'fa-exclamation-circle';
      default: return 'fa-info-circle';
    }
  };

  const showToast = (notif) => {
    const container = document.getElementById('notificationToastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `notification-toast notif-${notif.type}`;
    toast.dataset.id = notif.id;

    toast.innerHTML = `
        <div class="notif-icon-wrap">
            <i class="fas ${getNotifIcon(notif.type)}"></i>
        </div>
        <div class="notif-content-wrap">
            <span class="notif-title">${notif.title}</span>
            <span class="notif-message">${notif.message}</span>
        </div>
        <div class="notif-right-wrap">
            <span class="notif-time">${notif.timestamp}</span>
            <button class="notif-close-btn" title="Close">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="notif-new-dot"></div>
        <div class="notif-progress-bar" style="width: 100%"></div>
    `;

    container.appendChild(toast);
    playChime();

    // Bell shake animation
    const bellBtn = document.getElementById('notificationBellBtn');
    if (bellBtn) {
        bellBtn.classList.remove('shaking');
        void bellBtn.offsetWidth; // reflow to restart animation
        bellBtn.classList.add('shaking');
        setTimeout(() => bellBtn.classList.remove('shaking'), 700);
    }

    // Auto dismiss setup — 7 seconds for enterprise readability
    let dismissTime = 7000;
    let startTime = Date.now();
    let remainingTime = dismissTime;
    let autoDismissTimeout = null;
    let progressInterval = null;

    const progressBar = toast.querySelector('.notif-progress-bar');
    const updateProgress = () => {
        let elapsed = Date.now() - startTime;
        let pct = Math.max(0, 100 - (elapsed / dismissTime) * 100);
        progressBar.style.width = `${pct}%`;
        if (pct <= 0) clearInterval(progressInterval);
    };

    const startTimer = () => {
        startTime = Date.now();
        autoDismissTimeout = setTimeout(() => closeToast(toast), remainingTime);
        progressInterval = setInterval(updateProgress, 30);
    };

    const pauseTimer = () => {
        clearTimeout(autoDismissTimeout);
        clearInterval(progressInterval);
        remainingTime -= (Date.now() - startTime);
        if (remainingTime < 0) remainingTime = 0;
    };

    startTimer();

    toast.addEventListener('mouseenter', pauseTimer);
    toast.addEventListener('mouseleave', () => {
        if (remainingTime > 0) startTimer();
    });

    const closeBtn = toast.querySelector('.notif-close-btn');
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearTimeout(autoDismissTimeout);
        clearInterval(progressInterval);
        closeToast(toast);
    });

    toast.addEventListener('click', () => {
        markAsRead(notif.id);
        clearTimeout(autoDismissTimeout);
        clearInterval(progressInterval);
        closeToast(toast);
    });
  };

  const closeToast = (toast) => {
    toast.classList.add('dismissing');
    // remove after animation completes (~380ms)
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 500);
  };

  const renderDropdown = () => {
    const listContainer = document.getElementById('notificationCenterList');
    if (!listContainer) return;

    listContainer.innerHTML = '';
    const sorted = [...localNotifications].sort((a, b) => b.id - a.id);

    if (sorted.length === 0) {
        listContainer.innerHTML = `
            <div class="nc-empty">
                <i class="fas fa-bell-slash"></i>
                <span>No notifications yet</span>
            </div>
        `;
        return;
    }

    sorted.forEach(notif => {
        const item = document.createElement('div');
        item.className = `nc-item notif-${notif.type} ${notif.read ? '' : 'unread'}`;
        item.dataset.id = notif.id;

        item.innerHTML = `
            <div class="nc-item-icon-wrap">
                <i class="fas ${getNotifIcon(notif.type)}"></i>
            </div>
            <div class="nc-item-content">
                <span class="nc-item-title">${notif.title}</span>
                <span class="nc-item-message">${notif.message}</span>
                <div class="nc-item-meta">
                    <span class="nc-item-time">${notif.timestamp}</span>
                    <button class="nc-item-delete" title="Delete">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;

        item.addEventListener('click', (e) => {
            if (e.target.closest('.nc-item-delete')) return;
            markAsRead(notif.id);
        });

        const deleteBtn = item.querySelector('.nc-item-delete');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteOneNotification(notif.id);
        });

        listContainer.appendChild(item);
    });
  };

  const updateBadge = () => {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;

    const unreadCount = localNotifications.filter(n => !n.read).length;
    badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
    
    if (unreadCount > 0) {
        badge.classList.add('has-notifications');
    } else {
        badge.classList.remove('has-notifications');
    }
  };

  const markAsRead = (id) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "mark_read", id }));
    } else {
        const notif = localNotifications.find(n => n.id === id);
        if (notif) {
            notif.read = true;
            saveLocalNotifications();
            renderDropdown();
            updateBadge();
        }
    }
  };

  const markAllRead = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "mark_all_read" }));
    } else {
        localNotifications.forEach(n => n.read = true);
        saveLocalNotifications();
        renderDropdown();
        updateBadge();
    }
  };

  const clearAllNotifications = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "clear_all" }));
    } else {
        localNotifications = [];
        saveLocalNotifications();
        renderDropdown();
        updateBadge();
    }
  };

  const deleteOneNotification = (id) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "delete_one", id }));
    } else {
        localNotifications = localNotifications.filter(n => n.id !== id);
        saveLocalNotifications();
        renderDropdown();
        updateBadge();
    }
  };

  const saveLocalNotifications = () => {
    localStorage.setItem('pm_notifications', JSON.stringify(localNotifications));
  };

  const loadLocalNotifications = () => {
    const raw = localStorage.getItem('pm_notifications');
    if (raw) {
        try {
            localNotifications = JSON.parse(raw);
        } catch (e) {
            localNotifications = [];
        }
    } else {
        localNotifications = [];
    }
  };

  const connectWebSocket = () => {
    if (wsReconnectTimer) clearTimeout(wsReconnectTimer);

    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!isLocalhost) {
        // In cloud deployment (e.g. Render/Railway), use seamless client simulation for notifications
        startClientSimulation();
        return;
    }

    try {
        ws = new WebSocket('ws://localhost:5001');

        ws.onopen = () => {
            console.log("Connected to Real-time Notification WebSocket server!");
            if (simulatedTimer) {
                clearInterval(simulatedTimer);
                simulatedTimer = null;
            }
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const action = data.action;

            if (action === 'history') {
                localNotifications = data.data;
                saveLocalNotifications();
                renderDropdown();
                updateBadge();
            } else if (action === 'new_notification') {
                const notif = data.notification;
                if (!localNotifications.some(n => n.id === notif.id)) {
                    localNotifications.push(notif);
                    saveLocalNotifications();
                    showToast(notif);
                    renderDropdown();
                    updateBadge();
                }
            } else if (action === 'mark_read') {
                const notif = localNotifications.find(n => n.id === data.id);
                if (notif) {
                    notif.read = true;
                    saveLocalNotifications();
                    renderDropdown();
                    updateBadge();
                }
            } else if (action === 'mark_all_read') {
                localNotifications.forEach(n => n.read = true);
                saveLocalNotifications();
                renderDropdown();
                updateBadge();
            } else if (action === 'clear_all') {
                localNotifications = [];
                saveLocalNotifications();
                renderDropdown();
                updateBadge();
            } else if (action === 'delete_one') {
                localNotifications = localNotifications.filter(n => n.id !== data.id);
                saveLocalNotifications();
                renderDropdown();
                updateBadge();
            }
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected. Retrying in 5 seconds...");
            ws = null;
            wsReconnectTimer = setTimeout(connectWebSocket, 5000);
            startClientSimulation();
        };

        ws.onerror = (err) => {
            ws.close();
        };

    } catch (e) {
        console.warn("WebSocket connection error: ", e);
        wsReconnectTimer = setTimeout(connectWebSocket, 5000);
        startClientSimulation();
    }
  };

  const triggerNotification = (title, message, type = 'info') => {
    const notif = {
        type: type,
        title: title,
        message: message,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        created_at: new Date().toISOString()
    };

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            action: "new_notification",
            notification: notif
        }));
    } else {
        notif.id = Date.now();
        notif.read = false;
        localNotifications.push(notif);
        saveLocalNotifications();
        showToast(notif);
        renderDropdown();
        updateBadge();
    }
  };

  const startClientSimulation = () => {
    if (simulatedTimer) return;

    console.log("Starting offline client-side simulation.");
    const simulatedAlerts = [
        { title: "Employee Present", message: "Ritika has marked attendance for today at 9:02 AM.", type: "success" },
        { title: "Leave Request Submitted", message: "Kumar has submitted a leave request for July 10.", type: "info" },
        { title: "Machine Stopped", message: "Machine #4 has been inactive for 15 minutes.", type: "error" },
        { title: "Task Completed", message: "Quality Inspection Report has been completed.", type: "success" },
        { title: "Low Stock Warning", message: "Cotton Inventory is below the minimum threshold.", type: "warning" }
    ];

    simulatedTimer = setInterval(() => {
        const item = simulatedAlerts[Math.floor(Math.random() * simulatedAlerts.length)];
        triggerNotification(item.title, item.message, item.type);
    }, 45000);
  };

  const setupNotificationEvents = () => {
    const bellBtn = document.getElementById('notificationBellBtn');
    const dropdown = document.getElementById('notificationCenterDropdown');
    const soundToggle = document.getElementById('soundToggleCheckbox');
    const soundIcon = document.getElementById('soundToggleIcon');
    const markReadBtn = document.getElementById('markAllReadBtn');
    const clearAllBtn = document.getElementById('clearAllNotificationsBtn');

    if (bellBtn && dropdown) {
        bellBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !bellBtn.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    }

    if (soundToggle) {
        soundToggle.checked = isSoundEnabled;
        if (soundIcon) {
            soundIcon.className = isSoundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        }

        soundToggle.addEventListener('change', () => {
            isSoundEnabled = soundToggle.checked;
            localStorage.setItem('pm_notif_sound', isSoundEnabled ? 'true' : 'false');
            if (soundIcon) {
                soundIcon.className = isSoundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
            }
            if (isSoundEnabled) playChime();
        });
    }

    if (markReadBtn) {
        markReadBtn.addEventListener('click', markAllRead);
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllNotifications);
    }

    loadLocalNotifications();
    renderDropdown();
    updateBadge();
    connectWebSocket();
  };

  const initNotifications = () => {
    // Check login state
    if (!isLoggedIn()) return;

    // Toast container (allows toast alerts on UI)
    const toastContainer = document.createElement('div');
    toastContainer.className = 'notification-toast-container';
    toastContainer.id = 'notificationToastContainer';
    document.body.appendChild(toastContainer);

    // Allow individual pages to opt out of the dropdown bell in the header
    if (document.body.dataset.noBell === 'true') {
      loadLocalNotifications();
      connectWebSocket();
      return;
    }

    // Bell and dropdown in header
    const headerInfo = document.querySelector('.header-info');
    if (!headerInfo) {
      loadLocalNotifications();
      connectWebSocket();
      return;
    }

    const bellContainer = document.createElement('div');
    bellContainer.className = 'notification-bell-container';
    bellContainer.innerHTML = `
        <button class="notification-bell-btn" id="notificationBellBtn" title="Notifications">
            <i class="fas fa-bell"></i>
            <span class="notification-badge" id="notificationBadge">0</span>
        </button>
        <div class="notification-center-dropdown" id="notificationCenterDropdown">
            <div class="nc-header">
                <h3>Notifications</h3>
                <div class="nc-actions">
                    <button id="markAllReadBtn" class="nc-action-btn">Mark all read</button>
                    <button id="clearAllNotificationsBtn" class="nc-action-btn">Clear all</button>
                </div>
            </div>
            <div class="nc-list" id="notificationCenterList"></div>
            <div class="nc-footer">
                <label class="nc-setting-toggle">
                    <span><i class="fas fa-volume-up" id="soundToggleIcon"></i> Notification Sound</span>
                    <span class="nc-switch">
                        <input type="checkbox" id="soundToggleCheckbox" checked>
                        <span class="nc-slider"></span>
                    </span>
                </label>
            </div>
        </div>
    `;

    const userInfo = headerInfo.querySelector('.user-info');
    if (userInfo) {
        headerInfo.insertBefore(bellContainer, userInfo);
    } else {
        headerInfo.appendChild(bellContainer);
    }

    setupNotificationEvents();
  };

  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotifications);
  } else {
    initNotifications();
  }

  return {
    getTheme,
    setTheme,
    toggleTheme,
    initStorage,
    // Customers
    getCustomers,
    saveCustomers,
    addCustomer,
    deleteCustomer,
    updateCustomer,
    // Production
    getProduction,
    saveProduction,
    addProduction,
    deleteProduction,
    updateProduction,
    // Sales
    getSales,
    saveSales,
    addSale,
    deleteSale,
    updateSale,
    // Stats
    getStats,
    // Suppliers
    getSuppliers,
    addSupplier,
    deleteSupplier,
    // Shipments
    getShipments,
    addShipment,
    deleteShipment,
    // Inventory
    getInventory,
    addInventoryItem,
    deleteInventoryItem,
    // Transactions
    getTransactions,
    addTransaction,
    deleteTransaction,
    // Workforce
    getWorkforce,
    addOperator,
    saveAttendance,
    saveShifts,
    // Utilities
    getNextId,
    isLoggedIn,
    getMe,
    login,
    quickLogin,
    logout,
    requireLogin,
    redirectIfLoggedIn,
    renderTable,
    triggerNotification
  };
})();

// Expose for debugging
window.App = App;
