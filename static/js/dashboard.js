// --- JAVASCRIPT FOR INTERACTION ---

document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
    initStudentsDropdown();
    document.getElementById('predictionForm').addEventListener('submit', handlePrediction);
});

async function handlePrediction(event) {
    event.preventDefault();
    const form = event.target;
    const resultDiv = document.getElementById('predictionResult');
    const riskText = document.getElementById('riskText');
    const probabilityValue = document.getElementById('probabilityValue');

    const data = {
        age: form.age.value,
        gpa: form.gpa.value,
        absences: form.absences.value,
        study_hours: form.study_hours.value,
        gender: form.gender.value,
        financial_aid: form.financial_aid.value,
    };

    riskText.textContent = 'Calculating...';
    resultDiv.classList.remove('hidden');
    resultDiv.className = 'mt-6 p-4 border-2 rounded-lg text-center'; // Reset classes

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Server returned an error for prediction.');
        }

        const result = await response.json();
        
        riskText.textContent = result.prediction_text;
        probabilityValue.textContent = result.probability;
        
        // Styling based on risk level
        if (result.probability > 50) {
            resultDiv.classList.add('border-red-500', 'bg-red-50');
            riskText.classList.add('text-red-600');
            riskText.classList.remove('text-green-600');
        } else {
            resultDiv.classList.add('border-green-500', 'bg-green-50');
            riskText.classList.add('text-green-600');
            riskText.classList.remove('text-red-600');
        }

    } catch (error) {
        console.error('Prediction failed:', error);
        riskText.textContent = 'Error';
        probabilityValue.textContent = 'N/A';
        resultDiv.classList.add('border-yellow-500', 'bg-yellow-50');
    }
}

let genderChartInstance = null;
let absencesChartInstance = null;

async function fetchDashboardData() {
    try {
        const response = await fetch('/dashboard_data');
        if (!response.ok) throw new Error('Failed to fetch dashboard data');
        const data = await response.json();
        
        renderGenderChart(data.gender_data);
        renderAbsencesChart(data.absences_data);

    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function initStudentsDropdown() {
    try {
        const res = await fetch('/students');
        if (!res.ok) throw new Error('Failed to load students');
        const students = await res.json();
        const select = document.getElementById('studentSelect');
        select.innerHTML = '';
        students.forEach((s, idx) => {
            const option = document.createElement('option');
            option.value = idx;
            option.textContent = `${s.Name || ('Student ' + (idx+1))}`;
            select.appendChild(option);
        });
        select.addEventListener('change', () => renderSelectedStudent(students[select.value]));
        if (students.length > 0) {
            select.value = 0;
            renderSelectedStudent(students[0]);
        }
    } catch (e) {
        console.error('initStudentsDropdown error', e);
    }
}

function renderSelectedStudent(s) {
    const container = document.getElementById('selectedStudent');
    const nameEl = document.getElementById('studentName');
    const nameBtn = document.getElementById('studentNameBtn');
    const metaEl = document.getElementById('studentMeta');
    const badge = document.getElementById('riskBadge');
    const details = document.getElementById('studentDetails');
    const setText = (id, val) => document.getElementById(id).textContent = (val ?? 'N/A');
    if (!s) { container.classList.add('hidden'); return; }
    nameEl.textContent = s.Name || 'Student';
    const gender = s.Gender === 'M' ? 'Male' : (s.Gender === 'F' ? 'Female' : String(s.Gender));
    const age = s.Age ?? 'N/A';
    const abs = s.Number_of_Absences ?? s.Absences ?? 'N/A';
    metaEl.textContent = `Gender: ${gender} • Age: ${age} • Absences: ${abs}`;
    const risk = String(s.Risk_Category || '').toLowerCase();
    badge.textContent = (s.Risk_Category || 'Unknown');
    badge.className = 'px-3 py-1 rounded-full text-white text-sm font-semibold';
    if (risk === 'red') {
        badge.classList.add('bg-red-600');
    } else if (risk === 'yellow') {
        badge.classList.add('bg-yellow-500');
    } else if (risk === 'green') {
        badge.classList.add('bg-green-600');
    } else {
        badge.classList.add('bg-gray-500');
    }
    container.classList.remove('hidden');

    // Populate details
    setText('dSchool', s.School);
    setText('dAddress', s.Address);
    setText('dFamilySize', s.Family_Size);
    setText('dParental', s.Parental_Status);
    setText('dMEdu', s.Mother_Education);
    setText('dFEdu', s.Father_Education);
    setText('dTravel', s.Travel_Time);
    setText('dStudy', s.Study_Time);
    setText('dFails', s.Number_of_Failures);
    setText('dInternet', s.Internet_Access);
    setText('dHealth', s.Health_Status);
    setText('dAbsences', s.Number_of_Absences ?? s.Absences);
    setText('dGrades', `${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}`);
    setText('dRiskDesc', s.Risk_Description || '');

    // Toggle details on name click
    const expanded = details.classList.contains('hidden') ? 'false' : 'true';
    nameBtn.setAttribute('aria-expanded', expanded);
    nameBtn.onclick = () => {
        details.classList.toggle('hidden');
        nameBtn.setAttribute('aria-expanded', details.classList.contains('hidden') ? 'false' : 'true');
    };
}

function renderGenderChart(data) {
    if (genderChartInstance) genderChartInstance.destroy();

    const ctx = document.getElementById('genderChart').getContext('2d');
    genderChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.Gender === 'M' ? 'Male' : 'Female'),
            datasets: [{
                label: 'Dropout Rate (%)',
                data: data.map(d => d.Dropout_Rate),
                backgroundColor: ['#3b82f6', '#ef4444'], // Blue and Red
                borderColor: ['#2563eb', '#dc2626'],
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Dropout Rate (%)' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + '%';
                        }
                    }
                }
            }
        }
    });
}

function renderAbsencesChart(data) {
    if (absencesChartInstance) absencesChartInstance.destroy();

    const ctx = document.getElementById('absencesChart').getContext('2d');
    absencesChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.Absence_Level),
            datasets: [{
                label: 'Dropout Rate (%)',
                data: data.map(d => d.Dropout_Rate),
                borderColor: '#10b981', // Emerald Green
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                tension: 0.4,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Dropout Rate (%)' }
                },
                x: {
                    title: { display: true, text: 'Absence Level' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + '%';
                        }
                    }
                }
            }
        }
    });
}
