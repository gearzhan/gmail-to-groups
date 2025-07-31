from flask import Flask, render_template, jsonify, request
import os
import json
from datetime import datetime, timedelta
import re
import subprocess

app = Flask(__name__)

# 配置
LOG_FILE = 'email_migration.log'  # 日志文件路径
CONFIG_FILE = 'config.json'

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE) if os.path.dirname(LOG_FILE) else '.', exist_ok=True)

# 创建默认配置文件
default_config = {
    "service_account_file": "service-account-key.json",
    "group_email": "your-group@yourdomain.com",
    "user_email": "user@yourdomain.com",
    "last_run": "Never"
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)

def read_log_file(lines=50):
    """
    读取日志文件最后几行
    """
    try:
        if not os.path.exists(LOG_FILE):
            return ["日志文件不存在"]
        
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            lines_list = f.readlines()
            return lines_list[-lines:] if len(lines_list) > lines else lines_list
    except Exception as e:
        return [f"读取日志文件错误: {str(e)}"]

def get_migration_stats():
    """
    获取迁移统计信息 - 支持多任务
    """
    try:
        if not os.path.exists(LOG_FILE):
            return {"total_runs": 0, "success_count": 0, "error_count": 0, "last_run": "从未运行", "task_stats": []}
        
        success_count = 0
        error_count = 0
        last_run = "未知"
        total_runs = 0
        task_stats = []
        
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # 查找最新的迁移完成记录
        for line in reversed(lines):
            if "Migration completed" in line:
                if total_runs == 0:  # 只获取最新的一次运行信息
                    last_run = line.split(' - ')[0] if ' - ' in line else line.strip()
                    # 提取成功和错误数量
                    success_match = re.search(r'(\d+) successful', line)
                    error_match = re.search(r'(\d+) errors', line)
                    if success_match:
                        success_count = int(success_match.group(1))
                    if error_match:
                        error_count = int(error_match.group(1))
                total_runs += 1
        
        # 提取任务级别的统计信息
        current_run_lines = []
        found_start = False
        
        for line in reversed(lines):
            if "Migration completed" in line and not found_start:
                found_start = True
                continue
            elif "开始多任务邮件迁移" in line and found_start:
                break
            elif found_start:
                current_run_lines.insert(0, line)
        
        # 解析任务统计
        for line in current_run_lines:
            if "完成!" in line and "成功:" in line:
                # 解析任务完成信息
                task_match = re.search(r'任务 (.+?) 完成! 成功: (\d+), 错误: (\d+)', line)
                if task_match:
                    task_name = task_match.group(1)
                    task_success = int(task_match.group(2))
                    task_errors = int(task_match.group(3))
                    task_stats.append({
                        'name': task_name,
                        'success_count': task_success,
                        'error_count': task_errors
                    })
        
        return {
            "total_runs": total_runs,
            "success_count": success_count,
            "error_count": error_count,
            "last_run": last_run,
            "task_stats": task_stats
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    """
    主页面
    """
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    """
    获取日志API
    """
    lines = request.args.get('lines', 50, type=int)
    logs = read_log_file(lines)
    return jsonify({"logs": logs})

@app.route('/api/stats')
def get_stats():
    """
    获取统计信息API
    """
    stats = get_migration_stats()
    return jsonify(stats)

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """
    配置管理API
    """
    if request.method == 'POST':
        data = request.json
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return jsonify({"status": "success"})
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return jsonify(config_data)

@app.route('/api/tasks')
def get_tasks():
    """
    获取迁移任务列表API
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return jsonify({"tasks": config_data.get('migration_tasks', [])})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    更新迁移任务API
    """
    try:
        data = request.json
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 查找并更新任务
        tasks = config_data.get('migration_tasks', [])
        for task in tasks:
            if task['id'] == task_id:
                task.update(data)
                break
        else:
            return jsonify({"error": "任务未找到"}), 404
        
        # 保存配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """
    添加新迁移任务API
    """
    try:
        data = request.json
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 生成新的任务ID
        existing_ids = [task['id'] for task in config_data.get('migration_tasks', [])]
        new_id = f"task{len(existing_ids) + 1}"
        while new_id in existing_ids:
            new_id = f"task{len(existing_ids) + 1}_{datetime.now().strftime('%H%M%S')}"
        
        # 创建新任务
        new_task = {
            'id': new_id,
            'name': data.get('name', '新任务'),
            'enabled': data.get('enabled', True),
            'source_label': data.get('source_label', ''),
            'target_group': data.get('target_group', ''),
            'description': data.get('description', '')
        }
        
        # 添加到配置
        if 'migration_tasks' not in config_data:
            config_data['migration_tasks'] = []
        config_data['migration_tasks'].append(new_task)
        
        # 保存配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({"status": "success", "task": new_task})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    删除迁移任务API
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 查找并删除任务
        tasks = config_data.get('migration_tasks', [])
        config_data['migration_tasks'] = [task for task in tasks if task['id'] != task_id]
        
        # 保存配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run-migration', methods=['POST'])
def run_migration():
    """
    手动触发迁移API - 支持多任务
    """
    try:
        # 调用迁移脚本
        result = subprocess.run(['python', 'gmail_to_groups.py'], 
                              capture_output=True, text=True, timeout=300,
                              encoding='utf-8', errors='ignore')
        
        # 更新最后运行时间
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config_data['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)