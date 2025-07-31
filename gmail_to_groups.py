import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 配置文件路径
CONFIG_FILE = 'config.json'

def load_config():
    """
    加载配置文件
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        raise

def create_services(config):
    """
    创建Google API服务
    """
    service_account_file = config['service_account_file']
    user_email = config['user_email']
    
    # 检查服务账户文件是否存在
    if not os.path.exists(service_account_file):
        raise FileNotFoundError(f"服务账户文件不存在: {service_account_file}")
    
    # 认证
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=[
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/apps.groups.migration'
        ]
    ).with_subject(user_email)
    
    # 创建服务
    gmail_service = build('gmail', 'v1', credentials=credentials)
    groups_service = build('groupsmigration', 'v1', credentials=credentials)
    
    return gmail_service, groups_service

def migrate_task_emails(task, gmail_service, groups_service):
    """
    迁移单个任务的邮件
    """
    task_id = task['id']
    task_name = task['name']
    source_label = task['source_label']
    target_group = task['target_group']
    
    logging.info(f"开始处理任务: {task_name} (ID: {task_id})")
    
    try:
        # 获取昨天的邮件，按标签过滤
        yesterday = datetime.now() - timedelta(days=1)
        query = f'after:{yesterday.strftime("%Y/%m/%d")} label:{source_label}'
        
        logging.info(f"任务 {task_name} 搜索条件: {query}")
        
        # 搜索邮件
        results = gmail_service.users().messages().list(
            userId='me',
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        logging.info(f"任务 {task_name} 找到 {len(messages)} 封邮件")
        
        successful_count = 0
        error_count = 0
        
        # 迁移每封邮件
        for i, message in enumerate(messages, 1):
            try:
                logging.info(f"任务 {task_name} 正在处理邮件 {i}/{len(messages)}: {message['id']}")
                
                # 获取邮件内容
                msg = gmail_service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='raw'
                ).execute()
                
                # 迁移到群组
                groups_service.archive().insert(
                    groupId=target_group,
                    body={},
                    media_body=msg['raw']
                ).execute()
                
                successful_count += 1
                logging.info(f"任务 {task_name} 成功迁移邮件 ID: {message['id']}")
                
                # 添加小延迟避免API限制
                time.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logging.error(f"任务 {task_name} 迁移邮件 {message['id']} 失败: {str(e)}")
        
        logging.info(f"任务 {task_name} 完成! 成功: {successful_count}, 错误: {error_count}")
        return {
            'task_id': task_id,
            'task_name': task_name,
            'successful_count': successful_count,
            'error_count': error_count,
            'total_messages': len(messages)
        }
        
    except Exception as e:
        logging.error(f"任务 {task_name} 执行失败: {str(e)}")
        return {
            'task_id': task_id,
            'task_name': task_name,
            'successful_count': 0,
            'error_count': 1,
            'total_messages': 0,
            'error': str(e)
        }

def migrate_daily_emails():
    """
    迁移每日邮件到Google Groups - 支持多任务
    """
    try:
        logging.info("开始多任务邮件迁移")
        
        # 加载配置
        config = load_config()
        
        # 创建服务
        gmail_service, groups_service = create_services(config)
        
        # 获取启用的迁移任务
        migration_tasks = [task for task in config.get('migration_tasks', []) if task.get('enabled', True)]
        
        if not migration_tasks:
            logging.warning("没有找到启用的迁移任务")
            return
        
        logging.info(f"找到 {len(migration_tasks)} 个启用的迁移任务")
        
        # 并行处理多个任务
        total_successful = 0
        total_errors = 0
        task_results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(migrate_task_emails, task, gmail_service, groups_service): task
                for task in migration_tasks
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    task_results.append(result)
                    total_successful += result['successful_count']
                    total_errors += result['error_count']
                except Exception as e:
                    logging.error(f"任务 {task['name']} 执行异常: {str(e)}")
                    total_errors += 1
        
        # 输出总结
        logging.info("=" * 50)
        logging.info("迁移任务总结:")
        for result in task_results:
            logging.info(f"  {result['task_name']}: {result['successful_count']} 成功, {result['error_count']} 错误")
        
        logging.info(f"总计: {total_successful} 成功, {total_errors} 错误")
        logging.info(f"Migration completed - {total_successful} successful, {total_errors} errors")
        logging.info("=" * 50)
        
    except Exception as error:
        logging.error(f'多任务迁移执行错误: {error}')
        raise

if __name__ == '__main__':
    migrate_daily_emails()