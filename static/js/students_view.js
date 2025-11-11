document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/students');
        const students = await res.json();
        const tbody = document.getElementById('rows');
        const params = new URLSearchParams(window.location.search);
        const initialSearch = params.get('search') || '';
        const highlight = (params.get('highlight') || '').toLowerCase();
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const clearBtn = document.getElementById('clearBtn');
        searchInput.value = initialSearch;

        function render(list) {
            tbody.innerHTML = '';
            list.forEach((s, i) => {
            const tr = document.createElement('tr');
            const risk = String(s.Risk_Category || '').toLowerCase();
            let badge = '<span class="px-2 py-0.5 rounded-full text-white text-xs bg-gray-500">Unknown</span>';
            if (risk === 'red') badge = '<span class="px-2 py-0.5 rounded-full text-white text-xs bg-red-600">Red</span>';
            else if (risk === 'yellow') badge = '<span class="px-2 py-0.5 rounded-full text-white text-xs bg-yellow-500">Yellow</span>';
            else if (risk === 'green') badge = '<span class="px-2 py-0.5 rounded-full text-white text-xs bg-green-600">Green</span>';
            tr.innerHTML = `
              <td class="px-3 py-2 text-gray-500">${i}</td>
              <td class="px-3 py-2 font-medium">${s.Name ?? 'Student'}</td>
              <td class="px-3 py-2">${s.Gender ?? ''}</td>
              <td class="px-3 py-2">${s.Age ?? ''}</td>
              <td class="px-3 py-2">${s.Number_of_Absences ?? s.Absences ?? ''}</td>
              <td class="px-3 py-2">${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}</td>
              <td class="px-3 py-2">${badge}</td>
              <td class="px-3 py-2">${s.Risk_Description ?? ''}</td>
              <td class="px-3 py-2"><a class="text-blue-600 hover:underline" href="/edit_student?gindex=${encodeURIComponent(String(s._idx))}">Edit</a></td>
            `;
              if (highlight && String(s.Name || '').toLowerCase() === highlight) {
                tr.classList.add('bg-yellow-50');
              }
            tbody.appendChild(tr);
            });
        }

        function sortByRisk(list) {
            const rank = (rc) => {
              const v = String(rc || '').toLowerCase();
              if (v === 'red') return 0;
              if (v === 'yellow') return 1;
              if (v === 'green') return 2;
              return 3;
            };
            return [...list].sort((a,b) => rank(a.Risk_Category) - rank(b.Risk_Category));
        }

        function filterList() {
            const q = searchInput.value.trim().toLowerCase();
            if (!q) { render(sortByRisk(students)); return; }
            const filtered = students.filter(s => String(s.Name || '').toLowerCase().includes(q));
            render(sortByRisk(filtered));
        }

        render(sortByRisk(students));
        if (initialSearch) filterList();
        searchBtn.addEventListener('click', filterList);
        clearBtn.addEventListener('click', () => { searchInput.value = ''; render(students); });
    } catch (e) { console.error(e); }
});
