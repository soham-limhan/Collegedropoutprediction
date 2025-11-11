document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('addStudentForm').addEventListener('submit', handleAddStudent);
    document.getElementById('quickPredictForm').addEventListener('submit', handleQuickPredict);
    initMenu();
    fetchRiskSummary();
});

function initMenu() {
    const toggle = document.getElementById('menuToggle');
    const panel = document.getElementById('menuPanel');
    const btnList = document.getElementById('btnListStudents');
    const btnAdd = document.getElementById('btnAddStudent');
    const btnDel = document.getElementById('btnDeleteStudent');
    const btnPrint = document.getElementById('btnPrintReport');
    const delCtrls = document.getElementById('deleteControls');
    const confirmDel = document.getElementById('confirmDelete');
    const delResult = document.getElementById('deleteResult');

    toggle.addEventListener('click', () => panel.classList.toggle('hidden'));
    btnList.addEventListener('click', () => { window.location.href = '/students_view'; });
    btnAdd.addEventListener('click', () => { document.getElementById('addStudentForm').scrollIntoView({behavior: 'smooth'}); });
    btnDel.addEventListener('click', () => { delCtrls.classList.toggle('hidden'); });
    btnPrint.addEventListener('click', () => {
        const full = confirm('Click OK for full report, or Cancel to print a single student.');
        if (full) {
            window.open('/print_report', '_blank');
            return;
        }
        const idx = prompt('Enter student index (0-based), or leave blank to search by name:');
        if (idx && idx.trim() !== '') {
            window.open('/print_report?index=' + encodeURIComponent(idx.trim()), '_blank');
            return;
        }
        const name = prompt('Enter full name to print report for:');
        if (name && name.trim() !== '') {
            window.open('/print_report?name=' + encodeURIComponent(name.trim()), '_blank');
        } else {
            alert('No student specified.');
        }
    });

    confirmDel.addEventListener('click', async () => {
        delResult.textContent = 'Deleting...';
        try {
            const payload = { index: document.getElementById('delIndex').value, name: document.getElementById('delName').value };
            const res = await fetch('/delete_student', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Delete failed');
            delResult.className = 'mt-2 text-sm text-green-700';
            delResult.textContent = `Deleted: ${data.deleted}`;
            fetchRiskSummary();
        } catch (e) {
            delResult.className = 'mt-2 text-sm text-red-700';
            delResult.textContent = 'Error: ' + e.message;
        }
    });
}

async function fetchRiskSummary() {
    try {
        const res = await fetch('/risk_summary');
        if (!res.ok) throw new Error('Failed to load risk summary');
        const s = await res.json();
        document.getElementById('totalStudents').textContent = s.total;
        document.getElementById('countRed').textContent = s.red;
        document.getElementById('countYellow').textContent = s.yellow;
        document.getElementById('countGreen').textContent = s.green;
        renderRiskChart(s);
    } catch (e) {
        console.error('risk summary error', e);
    }
}

let riskChartInstance = null;
function renderRiskChart(s) {
    if (riskChartInstance) riskChartInstance.destroy();
    const ctx = document.getElementById('riskChart').getContext('2d');
    riskChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Red', 'Yellow', 'Green'],
            datasets: [{
                label: 'Students',
                data: [s.red, s.yellow, s.green],
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                borderColor: ['#dc2626', '#d97706', '#059669'],
                borderWidth: 1,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            plugins: { legend: { display: false } }
        }
    });
}

async function handleAddStudent(e) {
    e.preventDefault();
    const form = e.target;
    const payload = Object.fromEntries(new FormData(form).entries());
    // Basic validation: enforce desired risk zone if provided
    if (payload.desired_risk_zone && !['Red','Yellow','Green'].includes(payload.desired_risk_zone)) {
        alert('Invalid desired risk zone.');
        return;
    }
    const resBox = document.getElementById('addStudentResult');
    resBox.textContent = 'Adding student...';
    try {
        const res = await fetch('/add_student', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Unknown error');
        resBox.textContent = `Added ${payload.name}. Risk: ${data.risk_category} (${data.probability}%)`;
        alert(`Student "${payload.name}" added successfully in category: ${data.risk_category}.`);
        // Refresh risk summary and students dropdown
        fetchRiskSummary();
        if (typeof initStudentsDropdown === 'function') {
            initStudentsDropdown();
        }
        // Navigate to list and highlight new student; list sorted by Red, Yellow, Green
        if (payload.name) {
            const q = new URLSearchParams({ search: payload.name, highlight: payload.name }).toString();
            window.location.href = '/students_view?' + q;
        }
    } catch (err) {
        resBox.textContent = 'Failed to add: ' + err.message;
    }
}

async function handleQuickPredict(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
        age: form.age.value,
        gpa: form.gpa.value,
        absences: form.absences.value,
        study_hours: form.study_hours.value,
        gender: form.gender.value,
        financial_aid: form.financial_aid.value,
    };
    const box = document.getElementById('quickPredictResult');
    box.className = 'mt-4 p-4 border rounded-lg';
    box.textContent = 'Predicting...';
    try {
        const res = await fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Unknown error');
        box.classList.remove('hidden');
        box.textContent = `${data.prediction_text} (${data.probability}%)`;
    } catch (err) {
        box.textContent = 'Prediction failed: ' + err.message;
    }
}
