// 全局变量
let autoRefresh = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载数据
    loadStats();
    loadLogs();
    loadConfig();
    loadTasks();
    
    // 绑定事件
    const refreshStatsBtn = document.getElementById('refresh-stats');
    if (refreshStatsBtn) refreshStatsBtn.addEventListener('click', loadStats);
    
    const refreshLogsBtn = document.getElementById('refresh-logs');
    if (refreshLogsBtn) refreshLogsBtn.addEventListener('click', loadLogs);
    
    const runBtn = document.getElementById('run-migration');
    if (runBtn) runBtn.addEventListener('click', runMigration);
    
    const logLinesSelect = document.getElementById('log-lines');
    if (logLinesSelect) logLinesSelect.addEventListener('change', loadLogs);
    
    const configForm = document.getElementById('config-form');
    if (configForm) configForm.addEventListener('submit', saveConfig);
    
    // 设置定时刷新
    setInterval(loadStats, 30000); // 30秒刷新统计
    setInterval(loadLogs, 10000);  // 10秒刷新日志
    setInterval(loadTasks, 60000); // 60秒刷新任务列表
});

/**
 * 加载统计信息
 */
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('success-count').textContent = data.success_count || 0;
            document.getElementById('error-count').textContent = data.error_count || 0;
            document.getElementById('total-runs').textContent = data.total_runs || 0;
            document.getElementById('last-run').textContent = data.last_run || '从未运行';
        })
        .catch(error => {
            console.error('加载统计信息失败:', error);
            showStatus('加载统计信息失败', 'error');
        });
}

/**
 * 加载日志
 */
function loadLogs() {
    const lines = document.getElementById('log-lines').value;
    fetch(`/api/logs?lines=${lines}`)
        .then(response => response.json())
        .then(data => {
            const logContent = document.getElementById('log-content');
            logContent.textContent = data.logs.join('');
            // 滚动到底部
            logContent.scrollTop = logContent.scrollHeight;
        })
        .catch(error => {
            console.error('加载日志失败:', error);
            showStatus('加载日志失败', 'error');
        });
}

/**
 * 手动运行迁移
 */
function runMigration() {
    const button = document.getElementById('run-migration');
    const originalText = button.innerHTML;
    
    // 显示加载状态
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 运行中...';
    button.disabled = true;
    showStatus('开始运行迁移...', 'info');
    
    fetch('/api/run-migration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showStatus('迁移完成!', 'success');
            loadStats();
            loadLogs();
        } else {
            showStatus('迁移失败: ' + (data.message || data.error), 'error');
        }
    })
    .catch(error => {
        showStatus('请求失败: ' + error.message, 'error');
    })
    .finally(() => {
        // 恢复按钮状态
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

/**
 * 加载配置
 */
function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            document.getElementById('group_email').value = data.group_email || '';
            document.getElementById('user_email').value = data.user_email || '';
            document.getElementById('service_account_file').value = data.service_account_file || '';
        })
        .catch(error => {
            console.error('加载配置失败:', error);
            showStatus('加载配置失败', 'error');
        });
}

/**
 * 保存配置
 */
function saveConfig(event) {
    event.preventDefault();
    
    const config = {
        group_email: document.getElementById('group_email').value,
        user_email: document.getElementById('user_email').value,
        service_account_file: document.getElementById('service_account_file').value
    };
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        showStatus('配置保存成功!', 'success');
    })
    .catch(error => {
        showStatus('保存配置失败: ' + error.message, 'error');
    });
}

/**
 * 显示状态消息
 */
function showStatus(message, type) {
    const statusElement = document.getElementById('status-message');
    statusElement.textContent = message;
    
    // 清除之前的类
    statusElement.className = '';
    
    // 根据类型设置样式
    switch(type) {
        case 'success':
            statusElement.classList.add('text-success');
            break;
        case 'error':
            statusElement.classList.add('text-danger');
            break;
        case 'info':
            statusElement.classList.add('text-info');
            break;
        default:
            statusElement.classList.add('text-muted');
    }
    
    // 3秒后清除消息
    setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = '';
    }, 3000);
}

/**
 * 格式化日志显示
 */
function formatLogLine(line) {
    if (line.includes('ERROR') || line.includes('失败')) {
        return `<span class="log-error">${line}</span>`;
    } else if (line.includes('WARNING') || line.includes('警告')) {
        return `<span class="log-warning">${line}</span>`;
    } else if (line.includes('SUCCESS') || line.includes('成功')) {
        return `<span class="log-success">${line}</span>`;
    }
    return line;
}

/**
 * 页面卸载时清理定时器
 */// 任务管理功能
function loadTasks() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            if (data.tasks) {
                displayTasks(data.tasks);
            }
        })
        .catch(error => {
            console.error('加载任务失败:', error);
            showMessage('加载任务失败', 'error');
        });
}

function displayTasks(tasks) {
    const container = document.getElementById('tasksContainer');
    
    if (tasks.length === 0) {
        container.innerHTML = '<div class="text-muted text-center py-3">暂无迁移任务，点击上方按钮添加新任务</div>';
        return;
    }
    
    let html = '<div class="row">';
    tasks.forEach(task => {
        const statusBadge = task.enabled ? 
            '<span class="badge bg-success">启用</span>' : 
            '<span class="badge bg-secondary">禁用</span>';
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${task.name}</h6>
                            ${statusBadge}
                        </div>
                        <p class="card-text small text-muted mb-2">
                            <strong>标签:</strong> ${task.source_label || '全部'}<br>
                            <strong>目标:</strong> ${task.target_group}
                        </p>
                        ${task.description ? `<p class="card-text small">${task.description}</p>` : ''}
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-outline-primary" onclick="editTask('${task.id}')">
                                <i class="fas fa-edit"></i> 编辑
                            </button>
                            <button class="btn btn-outline-${task.enabled ? 'warning' : 'success'}" 
                                    onclick="toggleTask('${task.id}', ${!task.enabled})">
                                <i class="fas fa-${task.enabled ? 'pause' : 'play'}"></i> 
                                ${task.enabled ? '禁用' : '启用'}
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteTask('${task.id}')">
                                <i class="fas fa-trash"></i> 删除
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function showAddTaskModal() {
    document.getElementById('taskModalTitle').textContent = '添加任务';
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
    document.getElementById('taskEnabled').checked = true;
    
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

function editTask(taskId) {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            const task = data.tasks.find(t => t.id === taskId);
            if (task) {
                document.getElementById('taskModalTitle').textContent = '编辑任务';
                document.getElementById('taskId').value = task.id;
                document.getElementById('taskName').value = task.name;
                document.getElementById('sourceLabel').value = task.source_label;
                document.getElementById('targetGroup').value = task.target_group;
                document.getElementById('taskDescription').value = task.description || '';
                document.getElementById('taskEnabled').checked = task.enabled;
                
                const modal = new bootstrap.Modal(document.getElementById('taskModal'));
                modal.show();
            }
        })
        .catch(error => {
            console.error('加载任务详情失败:', error);
            showMessage('加载任务详情失败', 'error');
        });
}

function saveTask() {
    const taskId = document.getElementById('taskId').value;
    const taskData = {
        name: document.getElementById('taskName').value,
        source_label: document.getElementById('sourceLabel').value,
        target_group: document.getElementById('targetGroup').value,
        description: document.getElementById('taskDescription').value,
        enabled: document.getElementById('taskEnabled').checked
    };
    
    const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
    const method = taskId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' || data.task) {
            showMessage(taskId ? '任务更新成功' : '任务添加成功', 'success');
            loadTasks();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
            modal.hide();
        } else {
            showMessage(data.error || '保存任务失败', 'error');
        }
    })
    .catch(error => {
        console.error('保存任务失败:', error);
        showMessage('保存任务失败', 'error');
    });
}

function toggleTask(taskId, enabled) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled: enabled })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage(`任务已${enabled ? '启用' : '禁用'}`, 'success');
            loadTasks();
        } else {
            showMessage(data.error || '更新任务状态失败', 'error');
        }
    })
    .catch(error => {
        console.error('更新任务状态失败:', error);
        showMessage('更新任务状态失败', 'error');
    });
}

function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？此操作不可撤销。')) {
        return;
    }
    
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage('任务删除成功', 'success');
            loadTasks();
        } else {
            showMessage(data.error || '删除任务失败', 'error');
        }
    })
    .catch(error => {
        console.error('删除任务失败:', error);
        showMessage('删除任务失败', 'error');
    });
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    // 清理定时器等资源
});