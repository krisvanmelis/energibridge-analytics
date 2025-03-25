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
            console.log(data);
            updateGroupTable(data.groups);
            updateGroupsInPanelForm(data.groups);
        });
});

document.getElementById('panel-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const panelName = document.getElementById('panel-name').value;
    const groupNames = Array.from(document.querySelectorAll('.item.selected'))
                                  .map(item => item.textContent);
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

document.addEventListener('DOMContentLoaded', function() {
    fetch('/groups')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateGroupTable(data.groups);
                updateGroupsInPanelForm(data.groups);
            } else {
                console.error('Failed to load groups:', data.message);
            }
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
        const item = document.createElement('div');
        item.className = 'item';
        item.textContent = group.name;
        item.addEventListener('click', () => {
            item.classList.toggle('selected');
        });
        selectElement.appendChild(item);
    });
}
