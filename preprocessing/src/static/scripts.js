// Adding a group
document.getElementById('group-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const groupName = document.getElementById('group-name').value;
    const folderPath = document.getElementById('folder-path').value;

    await addGroup(groupName, folderPath).then(async () =>
        await syncGroups()
    );
});

// Adding a panel
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

// Refreshing the page
document.addEventListener('DOMContentLoaded', async function() {
    await syncGroups();
    await syncPanels()
});

/**
 * Update the groups in the groups table.
 *
 * @param groups - The groups to use to fill the table.
 */
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

/**
 * Update list of panels in panel table.
 *
 * @param panels - Panels to use to fill the table
 */
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
        const values = Object.values(panel);
        const panelName = values[values.length - 1];  // For some reason the panel name is the last value instead of the first
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

/**
 * Update the groups to choose from in the panel form.
 *
 * @param groups - Groups to use as data
 */
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

/**
 * Fetch all groups.
 *
 * @returns Response containing list of all groups or null
 */
async function fetchGroups() {
    return await executeRequest('groups', {
        method: 'GET',
    });
}

/**
 * Add a group.
 *
 * @param name - Name of the group
 * @param folder_path - Path to folder containing data for experiment groups (csv files)
 * @returns Response containing list of new groups or null
 */
async function addGroup(name, folder_path) {
    return await executeRequest('/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, folder_path }),
    });
}

/**
 * Delete a group by name.
 *
 * @param name - Group name
 * @returns Response containing list of new groups or null
 */
async function deleteGroup(name) {
    return await executeRequest('/groups', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    });
}

/**
 * Sync all groups on screen with BE.
 */
async function syncGroups() {
    await fetchGroups().then(response => {
        if (response) {
            updateGroupTable(response.groups);
            updateGroupsInPanelForm(response.groups);
        }
    });
}

/**
 * Fetch all current panels.
 *
 * @returns Response containing list of all panels or null.
 */
async function fetchPanels() {
    return await executeRequest('/panels', {
        method: 'GET',
    });
}

/**
 * Add a panel.
 *
 * @param name - Name of the panel
 * @param group_names - Experiment group names
 * @param experiment_type - Experiment type TODO remove
 * @param measurement_types - Measurement types
 * @returns Response containing new panels or null
 */
async function addPanel(name, group_names, experiment_type, measurement_types) {
    return await executeRequest('/panels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(JSON.stringify({
            name,
            group_names,
            experiment_type,
            measurement_types,
        }))
    });
}

/**
 * Delete a panel by name.
 *
 * @param name - Name of the panel
 * @returns Response containing new panels or null
 */
async function deletePanel(name) {
    return await executeRequest('/panels', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    });
}

/**
 * Sync panels on screen with BE.
 */
async function syncPanels() {
    const response = await fetchPanels();
    if (response) {
        updatePanelTable(response.panels);
    }
}

/**
 * Execute an HTTP request and display error if it fails.
 *
 * @param url - URL to make request to
 * @param config - Request configuration (same as fetch api)
 * @returns Response or null on error
 */
async function executeRequest(url, config) {
    return await fetch(url, config).then(async (response) => {
        const json = await response.json();

        // Alert on screen if request fails
        if (json.status !== 'success') {
            alert(json.message);
            return null;
        }
        return json;
    })
}
