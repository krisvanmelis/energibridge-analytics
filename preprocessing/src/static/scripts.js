document.getElementById('group-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const groupName = document.getElementById('group-name').value;
    const folderPath = document.getElementById('folder-path').value;

    await addGroup(groupName, folderPath);
    await syncGroups();
});

document.getElementById('panel-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const panelName = document.getElementById('panel-name').value;
    const groupNames = Array.from(document.querySelectorAll('.item.selected'))
                                  .map(item => item.textContent);
    const experimentType = document.getElementById('experiment-type').value;
    const measurementTypes = Array.from(document.querySelectorAll('input[name="measurement_types"]:checked'))
                                 .map(cb => cb.value);

    await addPanel(panelName, groupNames, experimentType, measurementTypes);
    await syncPanels();
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

document.addEventListener('DOMContentLoaded', async () => {
    const folderPathSelect = document.getElementById('folder-path');
    try {
        const response = await fetch('/csv-data/input/');
        const data = await response.json(); // Assuming the endpoint returns a JSON array of folder names

        data.folders.forEach(folder => {
            const option = document.createElement('option');
            option.value = folder;
            option.textContent = folder;
            folderPathSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching folder paths:', error);
    }
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
        const deleteButton = document.createElement('button');
        const groupName = Object.values(item)[0];
        deleteButton.innerText = 'Delete Group';
        deleteButton.onclick = async () => {
            await deleteGroup(groupName);
            await syncGroups();
        }
        const deleteCell = document.createElement('td');
        deleteCell.appendChild(deleteButton);
        row.appendChild(deleteCell)
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
        const deleteButton = document.createElement('button');
        const panelName = Object.values(panel)[0];
        deleteButton.innerText = 'Delete Panel';
        deleteButton.onclick = async () => {
            await deletePanel(panelName);
            await syncPanels();
        }
        const deleteCell = document.createElement('td');
        deleteCell.appendChild(deleteButton);
        row.appendChild(deleteCell)
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

async function fetchGroups() {
    return await fetch('/groups')
        .then(response => response.json())
}

async function addGroup(name, folder_path) {
    return await fetch('/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(JSON.stringify({ name, folder_path })),
    })
        .then(response => response.json())
}

async function deleteGroup(name) {
    return await fetch('/groups', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    })
        .then(response => response.json())
}

async function syncGroups() {
    const response = await fetchGroups();

    updateGroupTable(response.groups);
    updateGroupsInPanelForm(response.groups);
}

async function fetchPanels() {
    return await fetch('/panels')
        .then(response => response.json())
}

async function addPanel(name, group_names, experiment_type, measurement_types) {
    return await fetch('/panels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(JSON.stringify({
            name,
            group_names,
            experiment_type,
            measurement_types,
        }))
    })
        .then(response => response.json())
}

async function deletePanel(name) {
    return await fetch('/panels', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    })
        .then(response => response.json())
}

async function syncPanels() {
    const response = await fetchPanels();

    updatePanelTable(response.panels);
}


