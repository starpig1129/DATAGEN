import json # Add json import
from queue import Queue # Add Queue import
from flask import Flask, request, jsonify, send_from_directory, Response # Add Response import
from flask_cors import CORS
# from flask_sse import sse # Remove Flask-SSE import
import os
import shutil
import mimetypes
from werkzeug.utils import secure_filename
from datetime import datetime
from main import MultiAgentSystem
from core.state import State
from langchain_core.messages import HumanMessage, AIMessage
import threading # Add threading import

app = Flask(__name__, static_folder='ui', static_url_path='') # Serve static files from root URL path
CORS(app)  # Enable CORS for all routes

# Remove SSE blueprint configuration and registration
# app.config["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379")
# app.register_blueprint(sse, url_prefix='/stream')

# Initialize the multi-agent system
system = MultiAgentSystem()

# Create a thread-safe queue for SSE messages
sse_queue = Queue()

# Initialize state
current_state = {
    "messages": [],
    "hypothesis": "",
    "process": "",
    "process_decision": "",
    "visualization_state": "",
    "searcher_state": "",
    "code_state": "",
    "report_section": "",
    "quality_review": "",
    "needs_revision": False,
    "sender": "",
    "needs_decision": False
}

def serialize_message(msg):
    """Convert message objects to serializable format"""
    if isinstance(msg, (HumanMessage, AIMessage)):
        return {
            "content": msg.content,
            "type": "human" if isinstance(msg, HumanMessage) else "assistant",
            "sender": getattr(msg, 'sender', None) or ('User' if isinstance(msg, HumanMessage) else 'Assistant')
        }
    elif isinstance(msg, dict):
        return msg
    elif isinstance(msg, str):
        return {
            "content": msg,
            "type": "assistant",
            "sender": "Assistant"
        }
    else:
        return {
            "content": str(msg),
            "type": "assistant",
            "sender": "Assistant"
        }

def serialize_state(state):
    """Convert state to JSON serializable format"""
    serialized = {}
    for key, value in state.items():
        if key == "messages":
            serialized[key] = [serialize_message(msg) for msg in value]
        elif isinstance(value, (str, bool, int, float, type(None))):
            serialized[key] = value
        else:
            serialized[key] = str(value)
    return serialized

def check_needs_decision(state):
    """Check if the current state needs user decision based on sender"""
    sender = state.get("sender", "")
    return sender == "human_choice" or sender == "human_review"

import traceback # Add traceback import for background error handling

def process_message_background(input_state):
    """Processes the message in a background thread."""
    global current_state, sse_queue, system
    thread_id = threading.get_ident()
    print(f"後台處理開始 [線程ID: {thread_id}]")
    try:
        # Run the system with input (This is the blocking part)
        print(f"啟動代理工作流 [線程ID: {thread_id}]")
        print(f"輸入狀態: sender={input_state.get('sender', 'None')}, process_decision={input_state.get('process_decision', 'None')}")
        
        # Use persistent thread ID for checkpoint continuity
        thread_config = {"configurable": {"thread_id": "persistent_chat_session"}, "recursion_limit": 3000}
        
        # If this is a decision, we're continuing from an interrupt
        if input_state.get("process_decision"):
            print(f"恢復工作流從決策點，process_decision={input_state.get('process_decision')}")
            # First update the checkpoint state with the decision
            graph = system.workflow_manager.get_graph()
            current_checkpoint = graph.get_state(thread_config)
            if current_checkpoint:
                # Update the state with the decision using update_state
                update_data = {
                    "process_decision": input_state["process_decision"]
                }
                # Add the decision message to the state
                if "messages" in input_state:
                    update_data["messages"] = input_state["messages"]
                
                print(f"更新checkpoint狀態，process_decision={update_data.get('process_decision')}")
                graph.update_state(thread_config, update_data)
                
                # Continue from the interrupt point (resume)
                print("從中斷點恢復工作流執行")
                events = graph.stream(
                    None,  # No input needed when resuming from interrupt
                    thread_config,
                    stream_mode="values",
                    debug=False
                )
            else:
                print("警告：沒有找到checkpoint，啟動新工作流")
                events = graph.stream(
                    input_state,
                    thread_config,
                    stream_mode="values",
                    debug=False
                )
        else:
            print(f"啟動新的工作流實例")
            events = system.workflow_manager.get_graph().stream(
                input_state,
                thread_config,
                stream_mode="values",
                debug=False
            )
        print(f"工作流流已創建 [線程ID: {thread_id}]")

        # Update state with results
        temp_state = input_state.copy() # Work on a copy within the thread initially
        event_count = 0
        for event in events:
            event_count += 1
            print(f"處理事件 #{event_count} [線程ID: {thread_id}]")
            print(f"事件發送者: {event.get('sender', 'None')}")
            
            for key in temp_state:
                if key != "messages" and key in event:
                    temp_state[key] = event[key]
            if "messages" in event and event["messages"]:
                # Update messages carefully
                temp_state["messages"] = [
                    msg for msg in event["messages"]
                    if isinstance(msg, (HumanMessage, AIMessage, dict, str))
                ]
                print(f"更新消息列表，當前消息數: {len(temp_state['messages'])}")

            # --- Start of modified SSE push logic ---
            # Check if decision is needed based on the sender in the current event state
            needs_decision = check_needs_decision(event) # Pass the event directly
            print(f"檢查是否需要決策: {needs_decision}, 發送者: {event.get('sender', 'None')}")
            
            if needs_decision:
                temp_state['needs_decision'] = True
                temp_state['process_decision'] = "" # Clear process decision
                print(f"需要用戶決策，設置needs_decision=True，已清除process_decision")
            else:
                temp_state['needs_decision'] = False
                print(f"不需要決策，設置needs_decision=False")

            # Serialize and push the current temp_state after processing each event
            # This ensures intermediate updates are sent to the frontend
            current_snapshot_state = temp_state.copy() # Take a snapshot for this push
            # Ensure needs_decision reflects the check result for this specific snapshot
            current_snapshot_state['needs_decision'] = needs_decision
            serialized_state = serialize_state(current_snapshot_state)
            state_json = json.dumps(serialized_state)
            print(f"將狀態推送到SSE隊列 [線程ID: {thread_id}, 事件 #{event_count}]")
            sse_queue.put(state_json)
            print(f"狀態已推送 (needs_decision={needs_decision}, 隊列大小: {sse_queue.qsize()})")

            # If decision is needed, update global state and exit thread *after* pushing
            if needs_decision:
                current_state = temp_state # Update global state immediately
                print(f"需要決策，已更新全局狀態並結束線程 [線程ID: {thread_id}]")
                return # Exit the background function immediately
            # --- End of modified SSE push logic ---

        # --- Code after the loop (only runs if no decision was needed during the loop) ---
        # If the loop completes without returning, check if it's due to an interrupt
        print(f"工作流完成，處理了 {event_count} 個事件 [線程ID: {thread_id}]")
        
        # Check if the workflow was interrupted (paused for user decision)
        graph = system.workflow_manager.get_graph()
        thread_config = {"configurable": {"thread_id": "persistent_chat_session"}}
        current_checkpoint = graph.get_state(thread_config)
        
        if current_checkpoint and current_checkpoint.next:
            # Workflow was interrupted, check if next step is HumanChoice
            next_steps = current_checkpoint.next
            print(f"工作流被中斷，下一步: {next_steps}")
            if "HumanChoice" in next_steps:
                print("檢測到需要決策 - 工作流在Hypothesis後暫停")
                temp_state['needs_decision'] = True
                temp_state['sender'] = "human_choice"
                current_state = temp_state
                print(f"已設置needs_decision=True，等待用戶決策 [線程ID: {thread_id}]")
                
                # Push interrupt state to SSE
                serialized_state = serialize_state(current_state)
                print(f"=== 中斷狀態序列化調試 ===")
                print(f"原始狀態 sender: {current_state.get('sender', 'None')}")
                print(f"原始狀態 needs_decision: {current_state.get('needs_decision', 'None')}")
                print(f"序列化後狀態 sender: {serialized_state.get('sender', 'None')}")
                print(f"序列化後狀態 needs_decision: {serialized_state.get('needs_decision', 'None')}")
                state_json = json.dumps(serialized_state)
                print(f"最終JSON字符串: {state_json}")
                sse_queue.put(state_json)
                print(f"中斷狀態已推送到SSE隊列 [線程ID: {thread_id}, 隊列大小: {sse_queue.qsize()}]")
                return
        
        # Normal completion - no decision needed
        temp_state['needs_decision'] = False
        current_state = temp_state
        print(f"已更新全局狀態，不需要決策 [線程ID: {thread_id}]")

        # Serialize and push the final state update via SSE
        serialized_state = serialize_state(current_state)
        state_json = json.dumps(serialized_state)
        sse_queue.put(state_json)
        print(f"最終狀態已推送到SSE隊列 [線程ID: {thread_id}, 隊列大小: {sse_queue.qsize()}]")

    except Exception as e:
        print(f"後台處理錯誤 [線程ID: {thread_id}]: {str(e)}")
        print(f"錯誤追踪: {traceback.format_exc()}")
        # Optionally push an error state via SSE
        error_state = {**serialize_state(current_state), "error": str(e)}
        sse_queue.put(json.dumps(error_state))
        print(f"錯誤狀態已推送到SSE隊列 [線程ID: {thread_id}]")


@app.route('/')
def index():
    return send_from_directory('ui', 'index.html')

# Flask will automatically handle static files based on static_folder and static_url_path

@app.route('/api/send_message', methods=['POST'])
def send_message():
    global current_state
    data = request.json
    message = data.get('message', '')
    process_decision = data.get('process_decision', '')
    
    print(f"收到API請求 - /api/send_message: message={message}, process_decision={process_decision}")
    
    try:
        # Create input state
        input_state = current_state.copy()
        
        if message:
            # Add new message to state
            print(f"添加用戶消息到狀態: '{message}'")
            input_state["messages"] = current_state["messages"] + [HumanMessage(content=message)]
        
        # Add process_decision if provided
        if process_decision:
            print(f"添加決策到狀態: process_decision={process_decision}")
            input_state["process_decision"] = process_decision
            # Add system message to show the decision
            decision_text = "重新生成假設" if process_decision == "1" else "繼續研究"
            input_state["messages"] = input_state["messages"] + [
                HumanMessage(content=f"已選擇: {decision_text}")
            ]
        
        # Create and start the background thread
        print("創建後台線程處理消息...")
        thread = threading.Thread(target=process_message_background, args=(input_state.copy(),)) # Pass a copy of input_state
        thread.start()
        print(f"後台線程已啟動 - 線程ID: {thread.ident}")

        # Immediately return a response indicating processing has started
        return jsonify({
            "status": "processing",
            "message": "訊息已收到，正在處理中..."
        })
    except Exception as e:
        import traceback
        print("Error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        # Check if decision is needed based on current sender
        needs_decision = check_needs_decision(current_state) # Pass the whole state
        print(f"API - /api/state: 計算的needs_decision={needs_decision}, 發送者={current_state.get('sender', 'None')}")
        
        serialized_state = serialize_state(current_state)
        
        # 檢查當前狀態中是否已有needs_decision字段
        state_needs_decision = current_state.get('needs_decision')
        print(f"API - /api/state: 當前狀態中的needs_decision={state_needs_decision}")
        
        # Combine serialized state with the needs_decision flag
        # Ensure needs_decision from the state itself is used if available, otherwise calculate
        response_data = {**serialized_state, "needs_decision": current_state.get('needs_decision', needs_decision)}
        print(f"API - /api/state: 最終返回的needs_decision={response_data['needs_decision']}")
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        print("Error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# 文件管理API端點
UPLOAD_FOLDER = 'data_storage'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'md', 'py', 'js', 'html', 'css'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(filepath):
    """獲取文件詳細信息"""
    try:
        stat = os.stat(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        return {
            'name': filename,
            'size': stat.st_size,
            'extension': ext.lstrip('.'),
            'mimeType': mimetypes.guess_type(filepath)[0] or 'application/octet-stream',
            'createdAt': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'updatedAt': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'type': get_file_type(ext.lstrip('.'))
        }
    except Exception as e:
        print(f"Error getting file info for {filepath}: {e}")
        return None

def get_file_type(extension):
    """根據副檔名判斷文件類型"""
    extension = extension.lower()
    
    if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
        return 'image'
    elif extension in ['pdf']:
        return 'document'
    elif extension in ['txt', 'md', 'json', 'csv', 'py', 'js', 'html', 'css']:
        return 'text'
    elif extension in ['mp4', 'avi', 'mov', 'webm']:
        return 'video'
    elif extension in ['mp3', 'wav', 'ogg']:
        return 'audio'
    elif extension in ['zip', 'rar', '7z', 'tar', 'gz']:
        return 'archive'
    else:
        return 'other'

@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        # 確保data_storage目錄存在
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            return jsonify({"files": []})
        
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                file_info = get_file_info(filepath)
                if file_info:
                    file_info['id'] = f"file_{len(files)}"
                    file_info['path'] = f"/{UPLOAD_FOLDER}/{filename}"
                    files.append(file_info)
        
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
def upload_files():
    try:
        # 確保data_storage目錄存在
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "沒有文件被上傳"}), 400
        
        uploaded_files = []
        files = request.files.getlist('file')
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                return jsonify({
                    "status": "error",
                    "message": f"不支援的文件格式: {file.filename}"
                }), 400
            
            # 檢查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({
                    "status": "error",
                    "message": f"文件 {file.filename} 超過大小限制"
                }), 400
            
            # 安全的文件名
            filename = secure_filename(file.filename)
            
            # 處理文件名衝突
            counter = 1
            original_filename = filename
            while os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            uploaded_files.append(filename)
        
        return jsonify({
            "status": "success",
            "message": f"成功上傳 {len(uploaded_files)} 個文件",
            "files": uploaded_files
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        os.remove(filepath)
        return jsonify({"status": "success", "message": f"文件 {filename} 已刪除"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/<filename>/rename', methods=['PUT'])
def rename_file(filename):
    try:
        data = request.get_json()
        new_name = data.get('newName')
        
        if not new_name:
            return jsonify({"status": "error", "message": "新文件名不能為空"}), 400
        
        # 安全的文件名
        new_name = secure_filename(new_name)
        
        old_path = os.path.join(UPLOAD_FOLDER, filename)
        new_path = os.path.join(UPLOAD_FOLDER, new_name)
        
        if not os.path.exists(old_path):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        if os.path.exists(new_path):
            return jsonify({"status": "error", "message": "目標文件名已存在"}), 400
        
        os.rename(old_path, new_path)
        return jsonify({"status": "success", "message": f"文件已重命名為 {new_name}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/preview/<filename>', methods=['GET'])
def preview_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        # 獲取文件類型
        _, ext = os.path.splitext(filename)
        file_type = get_file_type(ext.lstrip('.'))
        
        if file_type == 'image':
            return send_from_directory(UPLOAD_FOLDER, filename)
        else:
            return jsonify({"status": "error", "message": "不支援預覽此文件類型"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/content/<filename>', methods=['GET'])
def get_file_content(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "文件不存在"}), 404
        
        # 獲取文件類型
        _, ext = os.path.splitext(filename)
        file_type = get_file_type(ext.lstrip('.'))
        
        if file_type == 'text':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(content, mimetype='text/plain')
        else:
            return jsonify({"status": "error", "message": "不支援讀取此文件類型"}), 400
    except UnicodeDecodeError:
        try:
            # 嘗試其他編碼
            with open(filepath, 'r', encoding='gbk') as f:
                content = f.read()
            return Response(content, mimetype='text/plain')
        except:
            return jsonify({"status": "error", "message": "無法讀取文件內容"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# New SSE endpoint using in-memory queue
@app.route('/stream')
def event_stream():
    print("SSE連接已建立 - 客戶端已連接到/stream端點")
    def generate():
        connection_id = f"conn_{id(generate)}"
        print(f"SSE生成器已啟動 [ID: {connection_id}]")
        try:
            # 發送初始連接確認
            initial_message = json.dumps({"status": "connected", "connection_id": connection_id})
            yield f"event: connection_established\ndata: {initial_message}\n\n"
            print(f"已發送SSE連接確認 [ID: {connection_id}]")
            
            while True:
                try:
                    # Block until a message is available
                    print(f"等待消息... [ID: {connection_id}]")
                    message = sse_queue.get(timeout=None) # No timeout, wait indefinitely
                    # Format as SSE message
                    print(f"從隊列獲取到消息，準備發送 [ID: {connection_id}]")
                    sse_data = f"event: state_update\ndata: {message}\n\n"
                    yield sse_data
                    print(f"已發送SSE消息 [ID: {connection_id}]")
                    sse_queue.task_done() # Mark message as processed
                except Exception as e:
                    print(f"SSE生成器錯誤 [ID: {connection_id}]: {e}")
                    # Optionally break or handle specific errors
                    break # Exit loop on error to prevent infinite loops on persistent issues
        except GeneratorExit:
            print(f"SSE連接已關閉 [ID: {connection_id}]")
            
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    print("SSE響應已創建並返回")
    return response

# 設定管理API端點
SETTINGS_FILE = 'data_storage/settings.json'

def load_settings():
    """載入系統設定"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"載入設定失敗: {e}")
        return None

def save_settings(settings):
    """保存系統設定"""
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存設定失敗: {e}")
        return False

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """獲取系統設定"""
    try:
        settings = load_settings()
        if settings:
            return jsonify(settings)
        else:
            # 返回預設設定
            default_settings = {
                "api": {
                    "token": "",
                    "baseUrl": "http://localhost:5001",
                    "timeout": 30000,
                    "retryAttempts": 3,
                    "enableLogging": True,
                    # 新增的API Keys
                    "openaiApiKey": "",
                    "firecrawlApiKey": "",
                    "langchainApiKey": "",
                    # 系統路徑配置
                    "workingDirectory": "./data_storage/",
                    "condaPath": "/home/user/anaconda3",
                    "condaEnv": "data_assistant",
                    "chromedriverPath": "./chromedriver-linux64/chromedriver"
                },
                "user": {
                    "language": "zh-TW",
                    "theme": "auto",
                    "timezone": "Asia/Taipei",
                    "dateFormat": "YYYY-MM-DD",
                    "notifications": {
                        "enabled": True,
                        "types": {
                            "email": True,
                            "browser": True,
                            "system": True,
                            "chat": True,
                            "agent": True
                        },
                        "sound": True,
                        "vibration": False,
                        "desktop": True,
                        "quietHours": {
                            "enabled": False,
                            "startTime": "22:00",
                            "endTime": "08:00"
                        }
                    },
                    "interface": {
                        "sidebarCollapsed": False,
                        "compactMode": False,
                        "showToolbar": True,
                        "animationsEnabled": True,
                        "fontSize": "medium",
                        "density": "comfortable"
                    }
                },
                "agent": {
                    "workflow": {
                        "autoStart": False,
                        "parallelExecution": True,
                        "maxConcurrentAgents": 3,
                        "retryFailedTasks": True,
                        "saveIntermediateResults": True
                    },
                    "priorities": {
                        "searchAgent": 1,
                        "analysisAgent": 2,
                        "visualizationAgent": 3,
                        "reportAgent": 4,
                        "qualityReviewAgent": 5
                    },
                    "timeout": {
                        "agentResponse": 60000,
                        "fileUpload": 300000,
                        "apiRequest": 30000,
                        "websocketConnection": 10000
                    },
                    "debugging": {
                        "enabled": False,
                        "logLevel": "info",
                        "saveLogsToFile": False,
                        "showAgentSteps": False,
                        "verboseOutput": False
                    }
                },
                "data": {
                    "upload": {
                        "maxFileSize": 100,
                        "allowedTypes": [".csv", ".xlsx", ".json", ".txt", ".pdf"],
                        "maxFilesPerUpload": 10,
                        "autoScan": True,
                        "compressImages": True
                    },
                    "retention": {
                        "chatHistory": 30,
                        "uploadedFiles": 90,
                        "analysisResults": 180,
                        "logs": 7,
                        "autoDelete": False
                    },
                    "cache": {
                        "enabled": True,
                        "maxSize": 500,
                        "ttl": 3600,
                        "preloadData": False,
                        "compressData": True
                    },
                    "cleanup": {
                        "autoCleanup": True,
                        "cleanupInterval": 24,
                        "keepRecent": 7,
                        "cleanupLogs": True,
                        "cleanupCache": True
                    }
                },
                "version": "1.0.0",
                "lastModified": datetime.now().isoformat()
            }
            return jsonify(default_settings)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """更新系統設定"""
    try:
        # 驗證請求數據
        if not request.json:
            return jsonify({"status": "error", "message": "無效的請求數據"}), 400
        
        settings = request.json
        
        # 添加最後修改時間
        settings['lastModified'] = datetime.now().isoformat()
        
        # 保存設定
        if save_settings(settings):
            return jsonify({"status": "success", "message": "設定已保存"})
        else:
            return jsonify({"status": "error", "message": "保存設定失敗"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """驗證API Token"""
    try:
        data = request.json
        token = data.get('token') if data else None
        
        if not token:
            # 檢查Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({"status": "error", "message": "Token為空"}), 400
        
        # 這裡可以實現實際的Token驗證邏輯
        # 目前簡單檢查Token格式和長度
        if len(token) >= 32 and token.replace('-', '').replace('_', '').isalnum():
            return jsonify({
                "status": "success",
                "valid": True,
                "message": "Token驗證成功"
            })
        else:
            return jsonify({
                "status": "error",
                "valid": False,
                "message": "Token格式無效"
            }), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """獲取系統狀態"""
    try:
        # 檢查系統各組件狀態
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "multiAgentSystem": {
                    "status": "running" if system else "stopped",
                    "description": "多代理分析系統"
                },
                "fileStorage": {
                    "status": "available" if os.path.exists(UPLOAD_FOLDER) else "unavailable",
                    "description": "文件存儲系統",
                    "path": UPLOAD_FOLDER
                },
                "settingsStorage": {
                    "status": "available" if os.path.exists(os.path.dirname(SETTINGS_FILE)) else "unavailable",
                    "description": "設定存儲系統",
                    "path": SETTINGS_FILE
                }
            },
            "metrics": {
                "uptime": "運行中",
                "memoryUsage": "正常",
                "diskSpace": "充足"
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001) # Change port to 5001
