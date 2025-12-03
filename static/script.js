document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("scoutForm");
    const clubSelect = document.getElementById("clubSelect");
    const resultsArea = document.getElementById("resultsArea");
    const welcomeScreen = document.getElementById("welcome");
    const loading = document.getElementById("loading");
    const errorMsg = document.getElementById("errorMsg");
    const tableHead = document.getElementById("tableHeadRow");
    const tableBody = document.getElementById("tableBody");

    // Load Clubs
    fetch('/api/clubs')
        .then(res => res.json())
        .then(clubs => {
            clubSelect.innerHTML = '<option value="" disabled selected>Select Club...</option>';
            clubs.forEach(c => {
                let opt = document.createElement('option');
                opt.value = c; opt.textContent = c;
                clubSelect.appendChild(opt);
            });
        });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        // Transition UI
        welcomeScreen.classList.add("hidden");
        resultsArea.classList.add("hidden");
        errorMsg.classList.add("hidden");
        loading.classList.remove("hidden");

        const formData = new FormData(form);
        const payload = {
            club_name: formData.get("club_name"),
            subrole: formData.get("subrole"),
            top_k: formData.get("top_k")
        };

        fetch('/api/recommend', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            loading.classList.add("hidden");
            if (data.error) {
                errorMsg.textContent = data.error;
                errorMsg.classList.remove("hidden");
                return;
            }

            // Update Header Info
            document.getElementById("resClub").textContent = data.club;
            document.getElementById("resRole").textContent = data.role;

            // 1. BUILD TABLE HEADERS DYNAMICALLY
            // We want: Rank | Player Info | Match % | Key Feature | ...Dynamic Stats...
            let headersHtml = `
                <th>Rank</th>
                <th>Player Profile</th>
                <th>Squad</th>
                <th>Similarity</th>
                <th>Key Stat</th>
            `;

            // Add the dynamic columns returned by backend
            data.display_columns.forEach(col => {
                headersHtml += `<th>${col}</th>`;
            });

            tableHead.innerHTML = headersHtml;

            // 2. BUILD TABLE ROWS
            tableBody.innerHTML = "";
            data.results.forEach(p => {
                let matchClass = p.fit_cosine > 90 ? "match-high" : "match-mid";
                
                // Build dynamic stat cells
                let statsHtml = "";
                data.display_columns.forEach( key => {
                    statsHtml += `<td><span class="attr-val">${p.display_stats[key] || '-'}</span></td>`;
                });

                let row = `
                    <tr>
                        <td class="rank-cell">#${p.rank}</td>
                        <td>
                            <span class="player-name">${p.player}</span>
                            <div class="player-meta">
                                ${p.age} yo • ${p.nation}
                            </div>
                        </td>
                        <td>${p.club}</td>
                        <td><span class="match-pill ${matchClass}">${p.fit_cosine}%</span></td>
                        <td>
                            <div style="color:var(--primary); font-weight:bold;">${p.key_feature_value}</div>
                            <div style="font-size:0.75rem; color:var(--text-muted);">${p.key_feature}</div>
                        </td>
                        ${statsHtml}
                    </tr>
                `;
                tableBody.innerHTML += row;
            });

            resultsArea.classList.remove("hidden");
        })
        .catch(err => {
            loading.classList.add("hidden");
            errorMsg.textContent = "Error fetching data.";
            errorMsg.classList.remove("hidden");
            console.error(err);
        });
    });
});