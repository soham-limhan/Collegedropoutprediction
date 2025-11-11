document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const idx = params.get('index');
    const name = params.get('name');

    const studentsRes = await fetch('/students');
    const students = await studentsRes.json();

    let selected = null;
    if (idx !== null && idx !== '') {
        const i = parseInt(idx, 10);
        if (!Number.isNaN(i) && i >= 0 && i < students.length) {
            selected = students[i];
        }
    } else if (name) {
        selected = students.find(s => String(s.Name || '').toLowerCase() === String(name).toLowerCase());
    }

    const tbody = document.getElementById('rows');
    tbody.innerHTML = '';
    const renderRow = (s) => {
        const tr = document.createElement('tr');
        const risk = String(s.Risk_Category || '').toLowerCase();
        let label = 'Unknown';
        if (risk === 'red') label = 'Red';
        else if (risk === 'yellow') label = 'Yellow';
        else if (risk === 'green') label = 'Green';
        tr.innerHTML = `
          <td class="px-3 py-2">${s.Name ?? ''}</td>
          <td class="px-3 py-2">${s.Gender ?? ''}</td>
          <td class="px-3 py-2">${s.Age ?? ''}</td>
          <td class="px-3 py-2">${s.Number_of_Absences ?? s.Absences ?? ''}</td>
          <td class="px-3 py-2">${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}</td>
          <td class="px-3 py-2">${label}</td>
        `;
        tbody.appendChild(tr);
    };

    if (selected) {
        document.getElementById('summary').textContent = 'Report for: ' + (selected.Name || 'Student');
        renderRow(selected);
    } else {
        // Full report: show totals summary header
        // Fetch risk summary for counts
        try {
            const sres = await fetch('/risk_summary');
            const s = await sres.json();
            document.getElementById('summary').innerHTML = `
                <div>Total students: <b>${s.total}</b> — 
                <span class="text-red-600">Red: <b>${s.red}</b></span>, 
                <span class="text-yellow-600">Yellow: <b>${s.yellow}</b></span>, 
                <span class="text-green-600">Green: <b>${s.green}</b></span></div>`;
        } catch (e) {
            document.getElementById('summary').textContent = 'Full report';
        }
        students.forEach(renderRow);
    }
});
