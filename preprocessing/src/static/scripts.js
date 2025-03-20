document.getElementById('group-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const groupName = document.getElementById('group-name').value;
    const folderPath = document.getElementById('folder-path').value;

    fetch('/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: groupName, folder_path: folderPath })
    }).then(response => response.json())
      .then(data => updateTable('group-table', data.groups));
});

document.getElementById('panel-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const panelName = document.getElementById('panel-name').value;
    const groupNames = Array.from(document.getElementById('groups').selectedOptions)
                           .map(option => option.value);
    const experimentType = document.getElementById('experiment-type').value;
    const measurementTypes = Array.from(document.querySelectorAll('input[name="measurement_types"]:checked'))
                                 .map(cb => cb.value);

    fetch('/panels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: panelName,
            group_names: groupNames,
            experiment_type: experimentType,
            measurement_types: measurementTypes
        })
    }).then(response => response.json())
      .then(data => updateTable('panel-table', data.panels));
});

document.getElementById('generate-visualizations').addEventListener('click', function() {
    fetch('/visualizations/generate', { method: 'POST' })
        .then(response => window.location.href = response.url);
});

function updateTable(tableId, data) {
    const tableBody = document.getElementById(tableId).querySelector('tbody');
    tableBody.innerHTML = '';
    data.forEach(item => {
        const row = document.createElement('tr');
        for (const value of Object.values(item)) {
            const cell = document.createElement('td');
            cell.textContent = value;
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    });
}
