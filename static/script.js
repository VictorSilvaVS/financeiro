const API_URL = "";
let token = localStorage.getItem('finance_token');
let authMode = 'login';

let state = {
    username: "",
    balance: 0,
    income: 0,
    expenses: 0,
    transactions: [],
    caixinhas: []
};

let globalSettings = {
    theme: "dark",
    primaryColor: "#6366f1",
    fontSize: "16px",
    currency: "BRL",
    language: "pt-BR",
    navPos: "row",
    fontFamily: "'Outfit', sans-serif"
};

const translations = {
    "pt-BR": {
        dashboard: "Dashboard",
        transactions: "Transações",
        caixinhas: "Caixinhas",
        tipsLink: "Dicas & Paz",
        settings: "Configurações",
        balance: "Saldo Total",
        income: "Ganhos",
        expenses: "Despesas",
        recentActivities: "Atividade Recente",
        myCaixinhas: "Minhas Caixinhas",
        saveVault: "Sincronizar com o Vault",
        newRecord: "Novo Registro",
        langLabel: "Idioma do Sistema",
        currLabel: "Moeda de Exibição",
        colorLabel: "Cor Principal",
        fontLabel: "Tamanho da Fonte",
        navLabel: "Posição da Barra Lateral",
        fontStyleLabel: "Estilo da Fonte",
        emptyTrans: "Nenhuma transação registrada.",
        emptyCaix: "Sem reservas no momento.",
        logout: "Sair",
        quotes: [
            "Cuidado com as pequenas despesas; um pequeno vazamento afunda um grande navio.",
            "Dinheiro é um mestre terrível, mas um excelente servo.",
            "O hábito de poupar é em si uma educação; ele cultiva todas as virtudes.",
            "Não economize o que resta depois de gastar, gaste o que resta depois de economizar.",
            "A riqueza não consiste em ter grandes posses, mas em ter poucas necessidades."
        ],
        financialTips: [
            { title: "Regra 50-30-20", description: "50% Essenciais, 30% Desejos Pessoais, 20% Dívidas ou Poupança.", icon: "fa-percent" },
            { title: "Reserva de Emergência", description: "Tente juntar de 3 a 6 meses de seus gastos fixos em uma reserva segura.", icon: "fa-shield-heart" },
            { title: "Inflação de Estilo de Vida", description: "Quando ganhar mais, tente não aumentar seus gastos na mesma proporção.", icon: "fa-chart-line" },
            { title: "Compras por Impulso", description: "Espere 24 horas antes de comprar algo não planejado. O desejo pode passar.", icon: "fa-clock" }
        ]
    },
    "en-US": {
        dashboard: "Dashboard",
        transactions: "Transactions",
        caixinhas: "Vaults",
        tipsLink: "Tips & Peace",
        settings: "Settings",
        balance: "Total Balance",
        income: "Income",
        expenses: "Expenses",
        recentActivities: "Recent Activity",
        myCaixinhas: "My Vaults",
        saveVault: "Sync with Vault",
        newRecord: "New Record",
        langLabel: "System Language",
        currLabel: "Display Currency",
        colorLabel: "Primary Color",
        fontLabel: "Font Size",
        navLabel: "Sidebar Position",
        fontStyleLabel: "Font Style",
        emptyTrans: "No transactions recorded.",
        emptyCaix: "No savings at the moment.",
        logout: "Logout",
        quotes: [
            "Beware of little expenses; a small leak will sink a great ship.",
            "Money is a terrible master but an excellent servant.",
            "The habit of saving is itself an education; it fosters every virtue.",
            "Do not save what is left after spending, but spend what is left after saving.",
            "Wealth consists not in having great possessions, but in having few wants."
        ],
        financialTips: [
            { title: "50-30-20 Rule", description: "50% Needs, 30% Wants, 20% Savings or Debt.", icon: "fa-percent" },
            { title: "Emergency Fund", description: "Try to save 3-6 months of essential expenses in a safe place.", icon: "fa-shield-heart" },
            { title: "Lifestyle Inflation", description: "When your income increases, try not to increase spending proportionally.", icon: "fa-chart-line" },
            { title: "Impulse Buying", description: "Wait 24 hours before buying something unplanned. The urge usually fades.", icon: "fa-clock" }
        ]
    },
    "es-ES": {
        dashboard: "Panel",
        transactions: "Transacciones",
        caixinhas: "Ahorros",
        tipsLink: "Consejos y Paz",
        settings: "Ajustes",
        balance: "Saldo Total",
        income: "Ingresos",
        expenses: "Gastos",
        recentActivities: "Actividad Recente",
        myCaixinhas: "Mis Ahorros",
        saveVault: "Sincronizar con la Bóveda",
        newRecord: "Nuevo Registro",
        langLabel: "Idioma del Sistema",
        currLabel: "Moneda de Visualización",
        colorLabel: "Color Principal",
        fontLabel: "Tamaño de Fuente",
        navLabel: "Posición de la Barra Lateral",
        fontStyleLabel: "Estilo de Fuente",
        emptyTrans: "No hay transacciones registradas.",
        emptyCaix: "Sin ahorros por ahora.",
        logout: "Cerrar sesión",
        quotes: [
            "Cuidado con los gastos pequeños; una pequeña fuga halla el hundimiento de un gran barco.",
            "El dinero es un amo terrible, pero un sirviente excelente.",
            "El hábito de ahorrar es en sí mismo una educación; fomenta todas las virtudes.",
            "No ahorres lo que queda después de gastar, sino gasta lo que queda después de ahorrar.",
            "La riqueza no consiste en tener grandes posesiones, sino en tener pocos deseos."
        ],
        financialTips: [
            { title: "Regla 50-30-20", description: "50% Necesidades, 30% Deseos, 20% Ahorro.", icon: "fa-percent" },
            { title: "Fondo de Emergencia", description: "Ahorra de 3 a 6 meses de gastos básicos en un lugar seguro.", icon: "fa-shield-heart" },
            { title: "Inflación del Estilo de Vida", description: "Si ganas más, no gastes proporcionalmente más.", icon: "fa-chart-line" },
            { title: "Compras por Impulso", description: "Espera 24 horas antes de comprar algo no planeado.", icon: "fa-clock" }
        ]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        checkTokenAndLoad();
    }
    updateDate();
    setRandomQuote();
    renderTips();
});

// Auth Logic
function toggleAuthMode() {
    authMode = authMode === 'login' ? 'signup' : 'login';
    document.getElementById('auth-title').textContent = authMode === 'login' ? 'Bem-vindo' : 'Criar Conta';
    document.getElementById('auth-subtitle').textContent = authMode === 'login' ? 'Entre na sua conta segura' : 'Comece sua jornada financeira';
    document.getElementById('auth-btn').textContent = authMode === 'login' ? 'Entrar' : 'Cadastrar';
    document.getElementById('auth-toggle').textContent = authMode === 'login' ? 'Não tem conta? Crie agora' : 'Já tem conta? Entre aqui';
}

async function handleAuth() {
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;

    if (!username || !password) return alert("Preencha todos os campos");

    const endpoint = authMode === 'login' ? '/token' : '/signup';
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro na autenticação");
        }

        if (authMode === 'signup') {
            alert("Conta criada! Agora faça login.");
            toggleAuthMode();
        } else {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('finance_token', token);
            await checkTokenAndLoad();
        }
    } catch (err) {
        alert(err.message);
    }
}

async function checkTokenAndLoad() {
    try {
        // Fetch Data
        const resData = await fetch(`${API_URL}/api/data`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!resData.ok) {
            logout();
            return;
        }

        const data = await resData.json();
        state.username = data.username;
        state.transactions = data.transactions;
        state.caixinhas = data.caixinhas;

        // Fetch Settings
        const resSettings = await fetch(`${API_URL}/api/settings`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resSettings.ok) {
            globalSettings = await resSettings.json();
            applySettings(false); // Apply without saving back to server
        }

        calculateTotals();
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
        document.querySelectorAll('.username').forEach(el => el.textContent = state.username);
        updateUI();
    } catch (err) {
        console.error(err);
        logout();
    }
}

function logout() {
    localStorage.removeItem('finance_token');
    location.reload();
}

function calculateTotals() {
    state.income = state.transactions.filter(t => t.type === 'income').reduce((acc, t) => acc + t.amount, 0);
    state.expenses = state.transactions.filter(t => t.type === 'expense').reduce((acc, t) => acc + t.amount, 0);
    state.balance = state.income - state.expenses;
}

// UI Rendering
function updateUI() {
    document.getElementById('total-balance').textContent = formatCurrency(state.balance);
    document.getElementById('total-income').textContent = formatCurrency(state.income);
    document.getElementById('total-expenses').textContent = formatCurrency(state.expenses);

    const renderList = (list, targetId) => {
        const target = document.getElementById(targetId);
        if (!target) return;

        if (list.length === 0) {
            target.innerHTML = `<p class="empty-state">Nenhuma transação registrada.</p>`;
        } else {
            target.innerHTML = list.slice().reverse().map(t => {
                const badgeClass = t.category === 'fixed' ? 'badge-fixed' : 'badge-variable';
                const categoryLabel = t.category === 'fixed' ? 'Fixa' : 'Variável';
                const installmentLabel = t.installments > 1 ? `<span class="badge badge-installment"><i class="fas fa-layer-group"></i> ${t.current_installment}/${t.installments}</span>` : '';

                return `
                    <div class="transaction-item">
                        <div class="t-main">
                            <div class="t-icon ${t.type}"><i class="fas ${t.type === 'income' ? 'fa-arrow-up' : 'fa-arrow-down'}"></i></div>
                            <div class="t-info">
                                <p>${t.description}</p>
                                <span>
                                    <i class="fas fa-calendar-day"></i> ${t.date}
                                    ${t.type === 'expense' ? `<span class="badge ${badgeClass}">${categoryLabel}</span>` : ''}
                                    ${installmentLabel}
                                </span>
                            </div>
                        </div>
                        <div class="t-amount ${t.type === 'income' ? 'plus' : 'minus'}">
                            ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
                        </div>
                        <div class="t-actions">
                            <button onclick="deleteTransaction(${t.id})" title="Remover"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                `;
            }).join('');
        }
    };

    renderList(state.transactions.slice(-5), 'recent-transactions');
    renderList(state.transactions, 'full-transaction-list');
    renderCaixinhas();
}

// Backend Interactions
async function addTransaction(type, description, amount, category, installments = 1) {
    const totalAmount = parseFloat(amount);
    const instCount = parseInt(installments) || 1;
    const valuePerInst = totalAmount / instCount;

    const tData = {
        type,
        category: type === 'expense' ? category : null,
        description,
        amount: instCount > 1 ? valuePerInst : totalAmount,
        totalAmount: totalAmount,
        installments: instCount,
        currentInstallment: 1,
        date: new Date().toLocaleDateString(globalSettings.language)
    };

    try {
        const res = await fetch(`${API_URL}/api/transactions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tData)
        });
        if (res.ok) await checkTokenAndLoad();
        closeModal();
    } catch (err) {
        alert("Erro ao salvar transação");
    }
}

async function deleteTransaction(id) {
    if (!confirm("Remover esta transação?")) return;
    try {
        const res = await fetch(`${API_URL}/api/transactions/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) await checkTokenAndLoad();
    } catch (err) {
        alert("Erro ao deletar");
    }
}

async function addCaixinha(name, target) {
    try {
        const res = await fetch(`${API_URL}/api/caixinhas`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, target: parseFloat(target) })
        });
        if (res.ok) await checkTokenAndLoad();
        closeModal();
    } catch (err) {
        alert("Erro ao criar caixinha");
    }
}

async function depositCaixinha(id, val) {
    const amount = parseFloat(val);
    if (state.balance < amount) return alert("Saldo insuficiente");

    try {
        const res = await fetch(`${API_URL}/api/caixinhas/${id}/deposit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount })
        });
        if (res.ok) await checkTokenAndLoad();
        closeModal();
    } catch (err) {
        alert("Erro no depósito");
    }
}

// Settings Logic
function applySettings(updateInputs = true) {
    if (updateInputs) {
        globalSettings.language = document.getElementById('set-lang').value;
        globalSettings.currency = document.getElementById('set-currency').value;
        globalSettings.primaryColor = document.getElementById('set-color').value;
        globalSettings.fontSize = document.getElementById('set-font').value;
        globalSettings.navPos = document.getElementById('set-nav-pos').value;
        globalSettings.fontFamily = document.getElementById('set-font-family').value;
    } else {
        if (document.getElementById('set-lang')) document.getElementById('set-lang').value = globalSettings.language;
        if (document.getElementById('set-currency')) document.getElementById('set-currency').value = globalSettings.currency;
        if (document.getElementById('set-color')) document.getElementById('set-color').value = globalSettings.primaryColor;
        if (document.getElementById('set-font')) document.getElementById('set-font').value = globalSettings.fontSize;
        if (document.getElementById('set-nav-pos')) document.getElementById('set-nav-pos').value = globalSettings.navPos || "row";
        if (document.getElementById('set-font-family')) document.getElementById('set-font-family').value = globalSettings.fontFamily || "'Outfit', sans-serif";
    }

    document.documentElement.style.setProperty('--primary', globalSettings.primaryColor);
    document.documentElement.style.fontSize = globalSettings.fontSize;
    document.documentElement.style.setProperty('--font-family', globalSettings.fontFamily);
    document.documentElement.style.setProperty('--nav-pos', globalSettings.navPos);

    if (globalSettings.navPos === 'row-reverse') {
        document.documentElement.style.setProperty('--sidebar-border-right', 'none');
        document.documentElement.style.setProperty('--sidebar-border-left', '1px solid var(--glass-border)');
    } else {
        document.documentElement.style.setProperty('--sidebar-border-right', '1px solid var(--glass-border)');
        document.documentElement.style.setProperty('--sidebar-border-left', 'none');
    }

    translateUI();
    updateUI();
    updateDate();
}

function translateUI() {
    const t = translations[globalSettings.language] || translations["pt-BR"];

    // Sidebar & Nav
    const navLinks = document.querySelectorAll('nav a');
    if (navLinks.length >= 5) {
        navLinks[0].innerHTML = `<i class="fas fa-chart-line"></i> ${t.dashboard}`;
        navLinks[1].innerHTML = `<i class="fas fa-exchange-alt"></i> ${t.transactions}`;
        navLinks[2].innerHTML = `<i class="fas fa-piggy-bank"></i> ${t.caixinhas}`;
        navLinks[3].innerHTML = `<i class="fas fa-lightbulb"></i> ${t.tipsLink}`;
        navLinks[4].innerHTML = `<i class="fas fa-cog"></i> ${t.settings}`;
    }

    const logoutBtn = document.querySelector('.sidebar-footer .text-btn');
    if (logoutBtn) logoutBtn.innerHTML = `<i class="fas fa-sign-out-alt"></i> ${t.logout}`;

    // Dashboard Titles
    const h3s = document.querySelectorAll('.stat-info h3');
    if (h3s.length >= 3) {
        h3s[0].textContent = t.balance;
        h3s[1].textContent = t.income;
        h3s[2].textContent = t.expenses;
    }

    // Card Headers
    document.querySelectorAll('.card-header h3').forEach(h => {
        if (h.innerText.includes("Atividade") || h.innerText.includes("Activity") || h.innerText.includes("Actividad")) h.textContent = t.recentActivities;
        if (h.innerText.includes("Caixinhas") || h.innerText.includes("Vaults") || h.innerText.includes("Ahorros")) h.textContent = t.myCaixinhas;
    });

    // Settings Labels
    const labels = document.querySelectorAll('.settings-card label');
    if (labels.length >= 6) {
        labels[0].textContent = t.colorLabel;
        labels[1].textContent = t.fontLabel;
        labels[2].textContent = t.fontStyleLabel;
        labels[3].textContent = t.navLabel;
        labels[4].textContent = t.langLabel;
        labels[5].textContent = t.currLabel;
    }

    const saveBtn = document.querySelector('.settings-actions button');
    if (saveBtn) saveBtn.innerHTML = `<i class="fas fa-cloud-upload-alt"></i> ${t.saveVault}`;

    const newRecBtn = document.querySelector('header .btn-primary');
    if (newRecBtn) newRecBtn.innerHTML = `<i class="fas fa-plus"></i> ${t.newRecord}`;

    setRandomQuote();
    renderTips();
}

async function saveSettingsToServer() {
    const status = document.getElementById('settings-status');
    status.textContent = "Salvando...";
    try {
        const res = await fetch(`${API_URL}/api/settings`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(globalSettings)
        });
        if (res.ok) {
            status.textContent = "Configurações salvas e criptografadas na nuvem! ✨";
            setTimeout(() => status.textContent = "", 3000);
        }
    } catch (err) {
        status.textContent = "Erro ao sincronizar.";
        status.style.color = "var(--danger)";
    }
}

// Helper Functions
// Helper Functions
function formatCurrency(val) {
    const localeMap = {
        'BRL': 'pt-BR',
        'USD': 'en-US',
        'EUR': 'de-DE',
        'GBP': 'en-GB',
        'JPY': 'ja-JP'
    };
    const locale = localeMap[globalSettings.currency] || globalSettings.language;
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: globalSettings.currency
    }).format(val);
}

function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const el = document.getElementById('current-date');
    if (el) el.textContent = now.toLocaleDateString(globalSettings.language, options);
}

function setRandomQuote() {
    const t = translations[globalSettings.language] || translations["pt-BR"];
    const quote = t.quotes[Math.floor(Math.random() * t.quotes.length)];
    const el = document.getElementById('motivational-quote');
    if (el) el.textContent = `"${quote}"`;
}

function renderTips() {
    const container = document.getElementById('tips-grid-content');
    if (!container) return;
    const t = translations[globalSettings.language] || translations["pt-BR"];
    container.innerHTML = t.financialTips.map(tip => `
        <div class="tip-card">
            <i class="fas ${tip.icon}"></i>
            <h3>${tip.title}</h3>
            <p>${tip.description}</p>
        </div>
    `).join('');
}

function renderCaixinhas() {
    const fullContainer = document.getElementById('full-caixinhas-list');
    const miniContainer = document.getElementById('caixinhas-mini-list');
    if (!fullContainer || !miniContainer) return;

    const html = state.caixinhas.map(c => {
        const percent = Math.min((c.current / c.target) * 100, 100).toFixed(0);
        return `
            <div class="caixinha-card">
                <div class="card-header">
                    <h3>${c.name}</h3>
                    <i class="fas fa-piggy-bank"></i>
                </div>
                <p>${formatCurrency(c.current)} / ${formatCurrency(c.target)}</p>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${percent}%"></div>
                    </div>
                    <span>${percent}% alcançado</span>
                </div>
                <button class="btn-primary" style="width:100%; margin-top:1rem" onclick="openDepositModal(${c.id})">Investir</button>
            </div>
        `;
    }).join('');

    fullContainer.innerHTML = html || `<p class="empty-state">Sem reservas no momento.</p>`;

    miniContainer.innerHTML = state.caixinhas.slice(0, 2).map(c => {
        const percent = Math.min((c.current / c.target) * 100, 100).toFixed(0);
        return `
            <div style="margin-bottom:1rem">
                <small>${c.name}</small>
                <div class="progress-bar" style="height:6px"><div class="progress-fill" style="width: ${percent}%"></div></div>
            </div>
        `;
    }).join('') || `<p class="empty-state">Nenhuma caixinha.</p>`;
}

// Navigation
function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
    const section = document.getElementById(sectionId);
    if (section) section.classList.remove('hidden');

    document.querySelectorAll('nav a').forEach(a => {
        a.classList.remove('active');
        if (a.getAttribute('onclick') && a.getAttribute('onclick').includes(sectionId)) a.classList.add('active');
    });
}

// Modal management
function openModal(type) {
    const modalContent = document.getElementById('modal-content');
    let inner = '';

    if (type === 'add-transaction') {
        inner = `
            <div class="modal-header"><h2>Novo Registro</h2></div>
            <div class="form-group"><label>Tipo</label>
                <select id="t-type" onchange="toggleCategoryField()">
                    <option value="income">💰 Ganhos</option><option value="expense">💸 Despesa</option>
                </select>
            </div>
            <div id="category-group" class="form-group hidden"><label>Categoria</label>
                <select id="t-category" onchange="toggleInstallmentsField()">
                    <option value="variable">🛒 Variável</option><option value="fixed">🏠 Fixa</option>
                </select>
            </div>
            <div id="installments-group" class="form-group hidden"><label>Parcelas</label>
                <input type="number" id="t-installments" value="1" min="1">
            </div>
            <div class="form-group"><label>Descrição</label><input type="text" id="t-desc"></div>
            <div class="form-group"><label>Valor Total</label><input type="number" id="t-amount" step="0.01"></div>
            <div style="display:flex; gap:1rem; margin-top:1rem">
                <button class="btn-primary" style="flex:1" onclick="submitTransaction()">Salvar</button>
                <button class="text-btn" onclick="closeModal()">Cancelar</button>
            </div>
        `;
    } else if (type === 'add-caixinha') {
        inner = `
            <h2>Nova Caixinha</h2>
            <div class="form-group"><label>Nome</label><input type="text" id="c-name"></div>
            <div class="form-group"><label>Meta</label><input type="number" id="c-target"></div>
            <div style="display:flex; gap:1rem">
                <button class="btn-primary" onclick="submitCaixinha()">Criar</button>
                <button class="text-btn" onclick="closeModal()">Cancelar</button>
            </div>
        `;
    }
    modalContent.innerHTML = inner;
    document.getElementById('modal-container').classList.remove('hidden');
    if (type === 'add-transaction') toggleCategoryField();
}

function openDepositModal(id) {
    const c = state.caixinhas.find(x => x.id === id);
    const modalContent = document.getElementById('modal-content');
    modalContent.innerHTML = `
        <h2>Investir: ${c.name}</h2>
        <div class="form-group"><label>Valor</label><input type="number" id="d-amount" step="0.01"></div>
        <div style="display:flex; gap:1rem">
            <button class="btn-primary" onclick="submitDeposit(${id})">Depositar</button>
            <button class="text-btn" onclick="closeModal()">Cancelar</button>
        </div>
    `;
    document.getElementById('modal-container').classList.remove('hidden');
}

function toggleCategoryField() {
    const type = document.getElementById('t-type').value;
    const catGroup = document.getElementById('category-group');
    if (type === 'expense') {
        catGroup.classList.remove('hidden');
        toggleInstallmentsField();
    } else {
        catGroup.classList.add('hidden');
        const instGroup = document.getElementById('installments-group');
        if (instGroup) instGroup.classList.add('hidden');
    }
}

function toggleInstallmentsField() {
    const category = document.getElementById('t-category').value;
    const instGroup = document.getElementById('installments-group');
    if (category === 'variable') instGroup.classList.remove('hidden');
    else instGroup.classList.add('hidden');
}

function submitTransaction() {
    const type = document.getElementById('t-type').value;
    const desc = document.getElementById('t-desc').value;
    const amount = document.getElementById('t-amount').value;
    const category = document.getElementById('t-category').value;
    const inst = document.getElementById('t-installments').value;
    if (desc && amount) addTransaction(type, desc, amount, category, inst);
}

function submitCaixinha() {
    const name = document.getElementById('c-name').value;
    const target = document.getElementById('c-target').value;
    if (name && target) addCaixinha(name, target);
}

function submitDeposit(id) {
    const amount = document.getElementById('d-amount').value;
    if (amount) depositCaixinha(id, amount);
}

function closeModal() {
    document.getElementById('modal-container').classList.add('hidden');
}
