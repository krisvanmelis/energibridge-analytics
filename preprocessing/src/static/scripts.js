async function fetchConfigs() {
    const response = await fetch('/get_configs');
    const configs = await response.json();

    const tableBody = document.querySelector('table tbody');
    tableBody.innerHTML = `
        <tr>
            <th>Name</th>
            <th>Groups</th>
            <th>Actions</th>
        </tr>
    `; // Clear existing content

    configs.forEach(config => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${config.name}</td>
            <td>
                <ul>
                    ${config.groups.map(group => `<li>${group.name}</li>`).join('')}
                </ul>
            </td>
            <td><button onclick="deleteConfig('${config.name}')">Delete</button></td>
        `;
        tableBody.appendChild(row);
    });
}

async function addConfig() {
    const name = document.getElementById('name').value;
    const experiment_type = document.getElementById('experiment_type').value;
    const measurement_types = Array.from(document.querySelectorAll('.measurement-type:checked')).map(cb => cb.value);
    const groups = Array.from(document.querySelectorAll('.group-entry')).map(entry => ({
        name: entry.querySelector('.group-name').value,
        folder_path: entry.querySelector('.group-folder').value
    }));
    const body = JSON.stringify({ name, experiment_type, measurement_types, groups });
    const response = await fetch('/add_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    location.reload();
}

function addGroupField() {
    const groupContainer = document.getElementById('groups-container');
    const groupEntry = document.createElement('div');
    groupEntry.className = 'group-entry';
    groupEntry.innerHTML = `
        <label>Group Name: <input type="text" class="group-name" required></label>
        <label>Folder Path: <input type="text" class="group-folder" required></label>
        <button type="button" onclick="removeGroupField(this)">Remove Group</button>
    `;
    groupContainer.appendChild(groupEntry);
}

function removeGroupField(button) {
    button.parentElement.remove();
}

async function deleteConfig(name) {
    await fetch('/delete_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ name })
    });
    location.reload();
}

window.onload = async () => {
    await fetchConfigs();
};
