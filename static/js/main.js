document.addEventListener('DOMContentLoaded', function() {
    // Setup buttons for viewing file details
    setupDetailsButtons();
    
    // Setup refresh button
    document.getElementById('refresh-logs').addEventListener('click', function() {
        refreshLogs();
    });
    
    // Auto-refresh logs if monitoring is active
    if (document.querySelector('.monitoring-status')) {
        setInterval(refreshLogs, 10000); // Refresh every 10 seconds
    }
});

function setupDetailsButtons() {
    document.querySelectorAll('.view-details').forEach(button => {
        button.addEventListener('click', function() {
            const logIndex = this.getAttribute('data-log');
            showFileDetails(logIndex);
        });
    });
}

function refreshLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            // Update the global variable
            window.processedFiles = data;
            
            // Update the file count
            document.getElementById('file-count').textContent = `${data.length} Files`;
            
            // Update the table
            const tbody = document.querySelector('#logs-table tbody');
            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">No files processed yet</td>
                    </tr>
                `;
                return;
            }
            
            // Build the new table contents
            let html = '';
            data.slice().reverse().forEach((log, index) => {
                const fileName = log.original_path.split('/').pop();
                const statusClass = log.status === 'success' ? 'table-success' : 
                                   (log.status === 'skipped' ? 'table-warning' : 'table-danger');
                const statusBadge = log.status === 'success' ? 'bg-success' : 
                                   (log.status === 'skipped' ? 'bg-warning' : 'bg-danger');
                const statusText = log.status.charAt(0).toUpperCase() + log.status.slice(1);
                
                html += `
                    <tr class="${statusClass}">
                        <td>${log.timestamp}</td>
                        <td class="text-truncate" style="max-width: 200px;">${fileName}</td>
                        <td><span class="badge ${statusBadge}">${statusText}</span></td>
                        <td>
                            <button class="btn btn-sm btn-info view-details" 
                                    data-bs-toggle="modal" 
                                    data-bs-target="#detailsModal"
                                    data-log="${index}">
                                <i class="fas fa-info-circle"></i> Details
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
            
            // Re-attach event listeners
            setupDetailsButtons();
        })
        .catch(error => console.error('Error fetching logs:', error));
}

function showFileDetails(index) {
    const log = window.processedFiles.slice().reverse()[index];
    const modalContent = document.getElementById('modal-content');
    
    // Format the details based on status
    let detailsHtml = '';
    
    if (log.status === 'success') {
        const originalFileName = log.original_path.split('/').pop();
        const newFileName = log.new_path.split('/').pop();
        
        detailsHtml = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i> File renamed successfully
            </div>
            
            <div class="card mb-3">
                <div class="card-header">File Information</div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Original Filename:</div>
                        <div class="col-8">${originalFileName}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">New Filename:</div>
                        <div class="col-8">${newFileName}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Path:</div>
                        <div class="col-8 text-truncate">${log.original_path.substring(0, log.original_path.lastIndexOf('/'))}</div>
                    </div>
                    <div class="row">
                        <div class="col-4 fw-bold">Processing Time:</div>
                        <div class="col-8">${log.processing_time} seconds</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Extracted Metadata</div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Author:</div>
                        <div class="col-8">${log.metadata.author || 'Unknown'}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Title:</div>
                        <div class="col-8">${log.metadata.title || 'Unknown'}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Journal:</div>
                        <div class="col-8">${log.metadata.journal || 'Unknown'}</div>
                    </div>
                    <div class="row">
                        <div class="col-4 fw-bold">Year:</div>
                        <div class="col-8">${log.metadata.year || 'Unknown'}</div>
                    </div>
                </div>
            </div>
        `;
    } else if (log.status === 'skipped') {
        detailsHtml = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i> File skipped
            </div>
            
            <div class="card mb-3">
                <div class="card-header">Reason</div>
                <div class="card-body">
                    ${log.reason}
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header">File Information</div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Filename:</div>
                        <div class="col-8">${log.original_path.split('/').pop()}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Path:</div>
                        <div class="col-8 text-truncate">${log.original_path.substring(0, log.original_path.lastIndexOf('/'))}</div>
                    </div>
                    <div class="row">
                        <div class="col-4 fw-bold">Processing Time:</div>
                        <div class="col-8">${log.processing_time} seconds</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Extracted Metadata</div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Author:</div>
                        <div class="col-8">${log.metadata.author || 'Unknown'}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Title:</div>
                        <div class="col-8">${log.metadata.title || 'Unknown'}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Journal:</div>
                        <div class="col-8">${log.metadata.journal || 'Unknown'}</div>
                    </div>
                    <div class="row">
                        <div class="col-4 fw-bold">Year:</div>
                        <div class="col-8">${log.metadata.year || 'Unknown'}</div>
                    </div>
                </div>
            </div>
        `;
    } else {
        detailsHtml = `
            <div class="alert alert-danger">
                <i class="fas fa-times-circle me-2"></i> Error processing file
            </div>
            
            <div class="card mb-3">
                <div class="card-header">Error Details</div>
                <div class="card-body">
                    ${log.error}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">File Information</div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Filename:</div>
                        <div class="col-8">${log.original_path.split('/').pop()}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Path:</div>
                        <div class="col-8 text-truncate">${log.original_path.substring(0, log.original_path.lastIndexOf('/'))}</div>
                    </div>
                    <div class="row">
                        <div class="col-4 fw-bold">Processing Time:</div>
                        <div class="col-8">${log.processing_time} seconds</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    modalContent.innerHTML = detailsHtml;
}
