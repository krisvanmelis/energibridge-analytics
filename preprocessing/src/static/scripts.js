$(document).ready(function() {
    // Initialize the page
    syncGroups();
    syncExperiments();
    loadMeasurementTypes();

    // Set up error card close button
    $('#close-error').click(function() {
        $('#error-card').fadeOut();
    });

    // Fetch folder paths for the dropdown
    $.ajax({
        url: '/csv-data/input/',
        method: 'GET',
        success: function(data) {
            const folderPathSelect = $('#folder-path');
            data.folders.forEach(folder => {
                folderPathSelect.append(
                    $('<option>').val(folder).text(folder)
                );
            });
        },
        error: function(error) {
            console.error('Error fetching folder paths:', error);
        }
    });

    // Adding a group
    $('#group-form').submit(function(e) {
        e.preventDefault();
        const groupName = $('#group-name').val();
        const folderPath = $('#folder-path').val();
        
        if (!groupName || !folderPath) {
            showError('Validation Error', 'Please enter a group name and select a data folder.');
            return;
        }
        
        // Show loading state
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.text();
        submitBtn.html('<span class="loading-spinner"></span> Adding...');
        submitBtn.prop('disabled', true);
        
        addGroup(groupName, folderPath)
            .then(() => {
                syncGroups();
                // Reset form
                $('#group-name').val('');
                $('#folder-path').val('');
                showError('Success', `Group "${groupName}" added successfully.`, null, 'success');
            })
            .finally(() => {
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            });
    });

    // Adding an experiment
    $('#panel-form').submit(function(e) {
        e.preventDefault();
        const experimentName = $('#panel-name').val();
        const groupNames = $('.item.selected').map(function() {
            return $(this).text();
        }).get();
        const experimentType = $('#experiment-type').val();
        const measurementTypes = $('input[name="measurement_types"]:checked').map(function() {
            return $(this).val();
        }).get();
        
        if (groupNames.length === 0) {
            showError('Validation Error', 'Please select at least one group.');
            return;
        }
        
        if (measurementTypes.length === 0) {
            showError('Validation Error', 'Please select at least one measurement type.');
            return;
        }

        addExperiment(experimentName, groupNames, experimentType, measurementTypes)
            .then(() => syncExperiments());
    });

    // Generate visualizations button
    $('#generate-visualizations').click(function() {
        $.ajax({
            url: '/visualizations/generate',
            method: 'GET',
            success: function(response) {
                if (response.status === 'success') {
                    showError('Success', 'Visualizations generated successfully!', null, 'success');
                    // Open Grafana dashboard in new tab
                    window.open('http://localhost:3000', '_blank');
                } else {
                    showError('Error', 'Error generating visualizations: ' + response.message);
                }
            },
            error: function(error, textStatus, errorThrown) {
                console.error('Error generating visualizations:', error);
                showError(
                    'Visualization Generation Failed', 
                    'Could not generate visualizations.',
                    `Status: ${textStatus}\nError: ${errorThrown}\nResponse: ${JSON.stringify(error.responseJSON || {}, null, 2)}`
                );
            }
        });
    });
});

/**
 * Display an error message in the error card.
 * 
 * @param {string} title - The error title
 * @param {string} message - The error message
 * @param {string|null} details - Technical details (stack trace, etc.), can be null
 * @param {string} type - Type of message ('error' or 'success')
 */
function showError(title, message, details = null, type = 'error') {
    const errorCard = $('#error-card');
    
    // Set content
    $('.error-header h3').text(title);
    $('#error-message').text(message);
    
    // Handle technical details
    if (details) {
        $('#error-details').text(details);
        $('details').show();
    } else {
        $('details').hide();
    }
    
    // Set color based on type
    if (type === 'success') {
        errorCard.css('border-left-color', '#4CAF50');
        $('.error-header h3').css('color', '#4CAF50');
    } else {
        errorCard.css('border-left-color', '#f44336');
        $('.error-header h3').css('color', '#f44336');
    }
    
    // Show the card with animation
    errorCard.fadeIn();
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            errorCard.fadeOut();
        }, 5000);
    }
}

/**
 * Update list of experiments in experiment table.
 *
 * @param experiments - Experiments to use to fill the table
 */
function updateExperimentTable(experiments) {
    const tableBody = $('#panel-table tbody');
    tableBody.empty();
    
    experiments.forEach(experiment => {
        const row = $('<tr>');
        
        ['name', 'experiment_type', 'measurement_types', 'group_names'].forEach(key => {
            $('<td>').html(experiment[key]).appendTo(row);
        });
        
        const deleteButton = $('<button>')
            .text('Delete Experiment')
            .click(function() {
                deleteExperiment(experiment.name)
                    .then(() => syncExperiments());
            });
            
        $('<td>').append(deleteButton).appendTo(row);
        tableBody.append(row);
    });
}

/**
 * Update the groups to choose from in the experiment form.
 *
 * @param groups - Groups to use as data
 */
function updateGroupsInExperimentForm(groups) {
    const selectElement = $('#groups');
    selectElement.empty();

    groups.forEach(group => {
        $('<div>')
            .addClass('item')
            .text(group.name)
            .click(function() {
                $(this).toggleClass('selected');
            })
            .appendTo(selectElement);
    });
}

/**
 * Fetch all groups.
 *
 * @returns Promise resolving to response or null
 */
function fetchGroups() {
    return executeRequest('groups', { method: 'GET' });
}

/**
 * Add a group.
 *
 * @param name - Name of the group
 * @param folder_path - Path to folder containing data for experiment groups (csv files)
 * @returns Promise resolving to response or null
 */
function addGroup(name, folder_path) {
    return executeRequest('/groups', {
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ name, folder_path })
    });
}

/**
 * Delete a group by name.
 *
 * @param name - Group name
 * @returns Promise resolving to response or null
 */
function deleteGroup(name) {
    return executeRequest('/groups', {
        method: 'DELETE',
        contentType: 'application/json',
        data: JSON.stringify({ name })
    });
}

/**
 * Sync all groups on screen with BE.
 */
function syncGroups() {
    fetchGroups().then(response => {
        if (response) {
            updateGroupsInExperimentForm(response.groups);
        }
    });
}

/**
 * Fetch all current experiments.
 *
 * @returns Promise resolving to response or null
 */
function fetchExperiments() {
    return executeRequest('/experiments', { method: 'GET' });
}

/**
 * Add an experiment.
 *
 * @param name - Name of the experiment
 * @param group_names - Group names to include in the experiment
 * @param experiment_type - Experiment type
 * @param measurement_types - Measurement types to analyze
 * @returns Promise resolving to response or null
 */
function addExperiment(name, group_names, experiment_type, measurement_types) {
    return executeRequest('/experiments', {
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(JSON.stringify({
            name,
            group_names,
            experiment_type,
            measurement_types
        }))
    });
}

/**
 * Delete an experiment by name.
 *
 * @param name - Name of the experiment
 * @returns Promise resolving to response or null
 */
function deleteExperiment(name) {
    return executeRequest('/experiments', {
        method: 'DELETE',
        contentType: 'application/json',
        data: JSON.stringify({ name })
    });
}

/**
 * Sync experiments on screen with BE.
 */
function syncExperiments() {
    fetchExperiments().then(response => {
        if (response) {
            updateExperimentTable(response.experiments);
        }
    });
}

/**
 * Load measurement types from backend and generate checkboxes
 */
function loadMeasurementTypes() {
    $.ajax({
        url: '/measurement-types',
        method: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                const container = $('#measurement-types-container');
                container.empty();
                
                // Create two columns for better UI organization
                const leftColumn = $('<div class="checkbox-column"></div>');
                const rightColumn = $('<div class="checkbox-column"></div>');
                container.append(leftColumn, rightColumn);
                
                // Split measurement types into two columns
                const types = response.measurement_types;
                const midpoint = Math.ceil(types.length / 2);
                
                // Debug: Log measurement types
                console.log('Available measurement types:', types);
                
                types.forEach((type, index) => {
                    const checkboxId = `measurement-${type.id}`;
                    const checkboxItem = $('<div class="checkbox-item"></div>');
                    
                    const checkbox = $('<input>')
                        .attr('type', 'checkbox')
                        .attr('id', checkboxId)
                        .attr('name', 'measurement_types')
                        .val(type.id);  // Make sure to use the correct ID from the backend
                        
                    const label = $('<label>')
                        .attr('for', checkboxId)
                        .text(type.name.replace(/_/g, ' '));
                        
                    checkboxItem.append(checkbox, label);
                    
                    // Add to appropriate column
                    if (index < midpoint) {
                        leftColumn.append(checkboxItem);
                    } else {
                        rightColumn.append(checkboxItem);
                    }
                });
            } else {
                showError('Error', 'Failed to load measurement types: ' + response.message);
            }
        },
        error: function(error) {
            console.error('Error fetching measurement types:', error);
            showError('Error', 'Failed to load measurement types.');
        }
    });
}

/**
 * Execute an HTTP request and handle errors.
 *
 * @param url - URL to make request to
 * @param options - jQuery ajax options
 * @returns Promise resolving to response or null on error
 */
function executeRequest(url, options) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            ...options,
            success: function(response) {
                if (response.status !== 'success') {
                    showError('Request Error', response.message);
                    resolve(null);
                } else {
                    resolve(response);
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error('Request failed:', xhr);
                let detailsText = '';
                
                try {
                    // Try to extract any additional info from the response
                    if (xhr.responseJSON) {
                        detailsText = `Response: ${JSON.stringify(xhr.responseJSON, null, 2)}\n`;
                    } else if (xhr.responseText) {
                        detailsText = `Response: ${xhr.responseText}\n`;
                    }
                    
                    detailsText += `Status: ${textStatus}\nError: ${errorThrown}\nEndpoint: ${url}\n`;
                    
                    if (xhr.status) {
                        detailsText += `Status Code: ${xhr.status}`;
                    }
                } catch (e) {
                    detailsText = 'Error details could not be parsed.';
                }
                
                showError(
                    'Request Failed', 
                    `Error making request to ${url.split('/').pop()}`, 
                    detailsText
                );
                resolve(null);
            }
        });
    });
}


