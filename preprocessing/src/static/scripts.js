document.getElementById('group-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const groupName = document.getElementById('group-name').value;
    const folderPath = document.getElementById('folder-path').value;

    fetch('/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(JSON.stringify({ name: groupName, folder_path: folderPath })),
    }).then(response => response.json())
        .then(data => {
            updateGroupTable(data.groups)
            updateGroupsInPanelForm(data.groups)
        });
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
        body: JSON.stringify(JSON.stringify({
            name: panelName,
            group_names: groupNames,
            experiment_type: experimentType,
            measurement_types: measurementTypes
        }))
    }).then(response => response.json())
        .then(response => {
            console.log(response)
            return response
        })
      .then(data => updatePanelTable(data.panels));
});

document.getElementById('groups').addEventListener('change', function () {
    const selectedGroups = Array.from(this.selectedOptions).map(option => option.text);
    const selectedDisplay = document.getElementById('selected-groups');

    // Clear previous selections
    selectedDisplay.innerHTML = '';

    // Add selected items as badges
    selectedGroups.forEach(group => {
        const span = document.createElement('span');
        span.textContent = group;
        selectedDisplay.appendChild(span);
    });
});

function updateGroupTable(groups) {
    const tableBody = document.getElementById('group-table').querySelector('tbody');
    tableBody.innerHTML = '';
    groups.forEach(item => {
        const row = document.createElement('tr');
        for (const value of Object.values(item)) {
            const cell = document.createElement('td');
            cell.textContent = value;
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    });
}

function updatePanelTable(panels) {
    const tableBody = document.getElementById('panel-table').querySelector('tbody');
    tableBody.innerHTML = '';
    panels.forEach(panel => {
        const row = document.createElement('tr');
        for (const key_name of ['name', 'experiment_type', 'measurement_types', 'group_names']) {
            const cell = document.createElement('td');
            console.log(panel);
            console.log(key_name);
            cell.innerHTML = panel[key_name];
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    });
}

function updateGroupsInPanelForm(groups) {
    const selectElement = document.getElementById('groups');

    // Clear existing options
    selectElement.innerHTML = '';

    // Add new options
    groups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.name;
        option.textContent = group.name;
        selectElement.appendChild(option);
    });
}
