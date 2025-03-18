async function addConfig() {
    const name = document.getElementById('name').value;
    const experiment_type = document.getElementById('experiment_type').value;
    const measurement_types = Array.from(document.querySelectorAll('.measurement-type:checked')).map(cb => cb.value);
    const groups = Array.from(document.querySelectorAll('.group-entry')).map(entry => ({
        name: entry.querySelector('.group-name').value,
        folder_path: entry.querySelector('.group-folder').value
    }));

    const response = await fetch('/add_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, experiment_type, measurement_types, groups })
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
