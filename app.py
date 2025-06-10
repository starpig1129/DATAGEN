import json # Add json import
from queue import Queue, Empty # Add Queue and Empty import
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
import asyncio
from typing import Dict, Any

app = Flask(__name__, static_folder='ui', static_url_path='') # Serve static files from root URL path
CORS(app)  # Enable CORS for all routes

# Remove SSE blueprint configuration and registration
# app.config["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379")
# app.register_blueprint(sse, url_prefix='/stream')

# Initialize the multi-agent system
system = MultiAgentSystem()

# Create a thread-safe queue for SSE messages and connection tracking
sse_queue = Queue()
active_connections = {}  # Track active SSE connections
connection_counter = 0

# WebSocket 支援 - 導入 WebSocket 管理器
try:
    from websocket_server import ws_manager, broadcast_agent_update, broadcast_data_update, broadcast_file_update
    WEBSOCKET_ENABLED = True
    print("WebSocket 支援已啟用")
except ImportError:
    WEBSOCKET_ENABLED = False
    print("WebSocket 支援未啟用 - websocket_server.py 不可用")
    
    # 創建空的廣播函數作為備用
    def broadcast_agent_update(*args, **kwargs):
        pass
    def broadcast_data_update(*args, **kwargs):
        pass
    def broadcast_file_update(*args, **kwargs):
        pass

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
    "needs_decision": False,
    "user_choice_continue": False,
    "force_process": False,
    "workflow_in_progress": False
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
            # Add debug logging for hypothesis field
            if key == "hypothesis" and value:
                print(f"序列化 hypothesis: 類型=字符串, 內容='{value[:100]}...'")
        elif isinstance(value, (HumanMessage, AIMessage)):
            # Handle AIMessage and HumanMessage objects properly (should be rare now)
            serialized_msg = serialize_message(value)
            serialized[key] = serialized_msg
            print(f"警告: 發現未處理的 AIMessage 對象在 {key}: {type(value).__name__}")
        elif isinstance(value, dict):
            # Recursively serialize nested dictionaries
            serialized[key] = serialize_state(value)
        elif isinstance(value, list):
            # Handle lists that might contain messages or other objects
            serialized[key] = [
                serialize_message(item) if isinstance(item, (HumanMessage, AIMessage))
                else serialize_state(item) if isinstance(item, dict)
                else item if isinstance(item, (str, bool, int, float, type(None)))
                else str(item)
                for item in value
            ]
        else:
            # Fallback to string representation for other types
            serialized[key] = str(value)
            # Add debug logging for unexpected types
            if key == "hypothesis":
                print(f"警告: hypothesis 使用字符串轉換: 類型={type(value).__name__}, 值='{str(value)[:100]}...'")
    return serialized

def check_needs_decision(state):
    """Check if the current state needs user decision based on sender"""
    sender = state.get("sender", "")
    # 檢查是否需要用戶決策 - 移除 hypothesis_agent 的直接檢測，改為依賴工作流中斷檢測
    needs_decision = sender == "human_choice" or sender == "human_review"
    
    # 關鍵修復：增強調試日誌以追蹤事件流
    print(f"=== check_needs_decision 詳細檢查 ===")
    print(f"當前事件發送者: '{sender}'")
    print(f"基於發送者的決策需求: {needs_decision}")
    
    # 添加調試日誌
    if sender == "hypothesis_agent":
        hypothesis = state.get("hypothesis", "")
        print(f"=== hypothesis_agent 特別檢測 ===")
        print(f"hypothesis 是否存在: {bool(hypothesis)}")
        print(f"hypothesis 類型: {type(hypothesis).__name__}")
        print(f"hypothesis 內容預覽: {hypothesis[:100]}..." if hypothesis else "無內容")
        print(f"注意: hypothesis_agent 的決策需求將由工作流中斷檢測處理")
        print("==============================")
    
    # 關鍵修復：添加其他發送者的日誌
    elif sender in ["human_choice", "human_review"]:
        print(f"=== 檢測到需要用戶介入的發送者: {sender} ===")
    elif sender:
        print(f"=== 其他代理發送者: {sender} ===")
    else:
        print(f"=== 無發送者或發送者為空 ===")
    
    print(f"最終決策需求結果: {needs_decision}")
    print("=" * 45)
    
    return needs_decision


def check_workflow_interrupt(graph, thread_config, current_state, thread_id):
    """
    統一的工作流中斷檢測函數
    整合三層重複檢測邏輯為單一、原子性的檢測
    
    Args:
        graph: 工作流圖實例
        thread_config: 線程配置
        current_state: 當前狀態字典
        thread_id: 線程識別符
        
    Returns:
        dict: {
            'needs_interrupt': bool,          # 是否需要中斷
            'interrupt_type': str,           # 中斷類型
            'updated_state': dict,           # 更新後的狀態
            'reason': str                    # 中斷原因
        }
    """
    print(f"=== 統一中斷檢測開始 [線程ID: {thread_id}] ===")
    
    # 獲取當前檢查點狀態
    try:
        checkpoint = graph.get_state(thread_config)
    except Exception as e:
        print(f"⚠️  無法獲取檢查點狀態: {e}")
        return {
            'needs_interrupt': False,
            'interrupt_type': 'none',
            'updated_state': current_state,
            'reason': '無法獲取檢查點狀態'
        }
    
    # 創建狀態副本用於修改
    updated_state = current_state.copy()
    
    # 檢查工作流階段和決策狀態
    is_workflow_start = not updated_state.get("workflow_in_progress", False)
    has_recent_decision = (
        updated_state.get("user_choice_continue", False) or
        updated_state.get("force_process", False)
    )
    # 修復：與 core/router.py 中的 hypothesis_router 邏輯保持一致
    # 檢查所有可能的決策標誌
    process_decision = updated_state.get("process_decision", "").strip()
    has_process_decision = process_decision in ["1", "2"]  # 任何有效決策都算作已決策
    
    # 用戶已決策的條件：不是工作流開始 且 (有最近決策 或 有處理決策)
    user_already_decided = (
        not is_workflow_start and (has_recent_decision or has_process_decision)
    )
    
    print(f"中斷檢測狀態分析:")
    print(f"  - 工作流開始階段: {is_workflow_start}")
    print(f"  - 有最近決策: {has_recent_decision}")
    print(f"  - process_decision 值: '{process_decision}'")
    print(f"  - 有處理決策(=2): {has_process_decision}")
    print(f"  - 用戶已決策: {user_already_decided}")
    
    # 檢查檢查點狀態
    if not checkpoint:
        print("📋 沒有檢查點狀態，工作流正常結束")
        return {
            'needs_interrupt': False,
            'interrupt_type': 'workflow_complete',
            'updated_state': updated_state,
            'reason': '工作流正常完成'
        }
    
    next_steps = checkpoint.next if checkpoint.next else []
    print(f"檢查點下一步: {next_steps}")
    
    # 新增：檢查 sender 是否為 human_choice（直接來自節點的信號）
    if updated_state.get("sender") == "human_choice" and not user_already_decided:
        print("🔍 檢測到 human_choice sender，直接觸發決策狀態")
        
        # 使用原子性狀態更新函數
        updated_state = update_decision_state(
            updated_state,
            True,
            'human_choice 節點直接要求用戶決策',
            thread_id
        )
        
        return {
            'needs_interrupt': True,
            'interrupt_type': 'human_choice_sender',
            'updated_state': updated_state,
            'reason': 'human_choice 節點直接要求用戶決策'
        }
    
    # 核心中斷檢測邏輯
    elif "HumanChoice" in next_steps and not user_already_decided:
        print("🔍 檢測到需要用戶決策的中斷點")
        
        # 使用原子性狀態更新函數
        updated_state = update_decision_state(
            updated_state,
            True,
            '工作流在 HumanChoice 節點需要用戶決策',
            thread_id
        )
        
        # 清除過期的決策標誌
        if not has_recent_decision:
            updated_state["process_decision"] = ""
        
        return {
            'needs_interrupt': True,
            'interrupt_type': 'human_choice_required',
            'updated_state': updated_state,
            'reason': '工作流在 HumanChoice 節點需要用戶決策'
        }
    
    elif "HumanChoice" in next_steps and user_already_decided:
        print(f"⏭️  用戶已做決策，跳過中斷檢測")
        
        # 關鍵修復：用戶已決策時，立即清除需要決策的狀態
        updated_state["needs_decision"] = False
        
        # 清除一次性決策標誌，但保持 workflow_in_progress
        if has_recent_decision:
            updated_state["user_choice_continue"] = False
            updated_state["force_process"] = False
            print("已清除一次性決策標誌")
        
        # 如果有有效的處理決策，也要清除
        if has_process_decision:
            updated_state["process_decision"] = ""
            print("已清除 process_decision")
        
        print("已清除 needs_decision 狀態")
        
        return {
            'needs_interrupt': False,
            'interrupt_type': 'decision_completed',
            'updated_state': updated_state,
            'reason': '用戶已完成決策，繼續工作流'
        }
    
    # 檢查是否有其他等待中的節點
    elif next_steps:
        print(f"📋 檢測到其他等待節點: {next_steps}")
        return {
            'needs_interrupt': False,
            'interrupt_type': 'other_nodes_pending',
            'updated_state': updated_state,
            'reason': f'等待其他節點處理: {next_steps}'
        }
    
    # 工作流正常完成
    else:
        print("✅ 工作流正常完成，無需中斷")
        
        # 使用原子性狀態更新函數
        updated_state = update_decision_state(
            updated_state,
            False,
            '工作流正常完成',
            thread_id
        )
        
        return {
            'needs_interrupt': False,
            'interrupt_type': 'workflow_complete',
            'updated_state': updated_state,
            'reason': '工作流正常完成'
        }


def update_decision_state(state, needs_decision, reason="", thread_id=None):
    """
    原子性更新決策狀態函數
    確保決策狀態設定的一致性和可靠性
    
    Args:
        state: 當前狀態字典
        needs_decision: 是否需要決策
        reason: 更新原因
        thread_id: 線程識別符（用於日誌）
    
    Returns:
        dict: 更新後的狀態
    """
    updated_state = state.copy()
    
    if needs_decision:
        # 設置需要決策的狀態
        updated_state["needs_decision"] = True
        updated_state["workflow_in_progress"] = True
        updated_state["sender"] = "human_choice"
        
        # 清除過期的決策標誌（如果沒有最近決策）
        if not updated_state.get("user_choice_continue", False) and not updated_state.get("force_process", False):
            updated_state["process_decision"] = ""
        
        log_msg = f"✅ 設置決策狀態: needs_decision=True"
    else:
        # 關鍵修復：徹底清除決策需求狀態
        updated_state["needs_decision"] = False
        
        # 檢查是否是決策處理完成的情況
        process_decision = updated_state.get("process_decision", "").strip()
        user_choice_continue = updated_state.get("user_choice_continue", False)
        
        # 如果用戶剛完成決策（process_decision存在且有效），清除相關標誌
        if process_decision in ["1", "2"] or user_choice_continue:
            updated_state["user_choice_continue"] = False
            updated_state["force_process"] = False
            # 只有在決策處理完成後才清除 process_decision
            if process_decision in ["1", "2"]:
                updated_state["process_decision"] = ""
            log_msg = f"✅ 決策處理完成: needs_decision=False, 已清除決策標誌"
        else:
            # 只在工作流完全結束時清除 workflow_in_progress
            if not user_choice_continue and not updated_state.get("force_process", False):
                updated_state["workflow_in_progress"] = False
            log_msg = f"✅ 清除決策狀態: needs_decision=False"
    
    # 記錄狀態更新
    if thread_id:
        print(f"{log_msg} [線程ID: {thread_id}]")
        if reason:
            print(f"更新原因: {reason}")
    else:
        print(log_msg)
        if reason:
            print(f"更新原因: {reason}")
    
    return updated_state


import traceback # Add traceback import for background error handling

def process_message_background(input_state):
    """Processes the message in a background thread."""
    global current_state, sse_queue, system
    thread_id = threading.get_ident()
    print(f"後台處理開始 [線程ID: {thread_id}]")
    
    # 廣播代理開始處理
    broadcast_agent_update("workflow_manager", "processing", 0, "開始處理用戶請求")
    
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
            
            # --- 統一啟動前中斷檢測 ---
            graph = system.workflow_manager.get_graph()
            
            print(f"=== 工作流啟動前狀態檢查 ===")
            startup_interrupt_result = check_workflow_interrupt(graph, thread_config, input_state, thread_id)
            
            if startup_interrupt_result['needs_interrupt']:
                print("🔍 檢測到現有中斷狀態，直接處理決策需求")
                
                # 應用中斷檢測結果並推送狀態
                temp_state = startup_interrupt_result['updated_state']
                serialized_state = serialize_state(temp_state)
                state_json = json.dumps(serialized_state)
                broadcast_to_sse_connections(state_json)
                print(f"⚡ 直接廣播中斷狀態到SSE連接 [線程ID: {thread_id}]")
                
                # 更新全局狀態並退出
                current_state = temp_state
                print(f"✅ 直接中斷處理完成，已更新全局狀態並結束線程 [線程ID: {thread_id}]")
                return
            else:
                print(f"啟動前檢測結果: {startup_interrupt_result['reason']}")
            
            events = graph.stream(
                input_state,
                thread_config,
                stream_mode="values",
                debug=False
            )
        print(f"工作流流已創建 [線程ID: {thread_id}]")

        # 關鍵修復：確保在事件處理前獲取正確的 graph 引用（避免重複獲取）
        if 'graph' not in locals():
            graph = system.workflow_manager.get_graph()
        if 'thread_config' not in locals():
            thread_config = {"configurable": {"thread_id": "persistent_chat_session"}}

        # Update state with results
        temp_state = input_state.copy() # Work on a copy within the thread initially
        event_count = 0
        
        # 關鍵修復：創建事件列表以檢查事件流完整性
        events_list = []
        events_iterator = iter(events)
        
        # 關鍵修復：先收集所有事件，以便分析事件流
        try:
            for event in events_iterator:
                events_list.append(event)
                print(f"📦 收集事件 #{len(events_list)}: sender={event.get('sender', 'None')}")
        except Exception as e:
            print(f"⚠️  事件收集過程中出現錯誤: {e}")
        
        print(f"🔍 總共收集到 {len(events_list)} 個事件")
        
        # 處理收集到的事件
        for event in events_list:
            event_count += 1
            print(f"=== 處理事件 #{event_count} [線程ID: {thread_id}] ===")
            print(f"事件發送者: {event.get('sender', 'None')}")
            print(f"事件完整內容: {event}")
            
            # 關鍵修復：檢查事件流的完整性
            current_graph_state = graph.get_state(thread_config)
            if current_graph_state:
                print(f"當前圖狀態 - 下一步: {current_graph_state.next}")
                print(f"當前圖狀態 - 配置: {getattr(current_graph_state, 'config', {})}")
            else:
                print("⚠️  無法獲取當前圖狀態")
            print("=" * 50)
            
            # 廣播代理狀態更新
            sender = event.get('sender', 'unknown')
            if sender and sender != 'None':
                progress = min(int((event_count / 10) * 100), 100)  # 估算進度
                current_task = f"執行 {sender} 代理任務"
                broadcast_agent_update(sender, "processing", progress, current_task)
            
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
                
                # 廣播數據更新
                broadcast_data_update("chat_state", {
                    "messages": len(temp_state["messages"]),
                    "sender": sender,
                    "timestamp": datetime.now().isoformat()
                })

            # --- 統一中斷檢測邏輯 (第一層：事件循環內檢測) ---
            # 使用統一的中斷檢測函數替代重複邏輯
            interrupt_result = check_workflow_interrupt(graph, thread_config, temp_state, thread_id)
            
            # 應用中斷檢測結果
            temp_state = interrupt_result['updated_state']
            needs_decision = interrupt_result['needs_interrupt']
            
            print(f"統一中斷檢測結果: {interrupt_result['interrupt_type']} - {interrupt_result['reason']}")
            print(f"需要決策: {needs_decision}, 發送者: {event.get('sender', 'None')}")

            # 廣播當前狀態到前端
            current_snapshot_state = temp_state.copy()
            serialized_state = serialize_state(current_snapshot_state)
            state_json = json.dumps(serialized_state)
            print(f"將狀態廣播到SSE連接 [線程ID: {thread_id}, 事件 #{event_count}]")
            broadcast_to_sse_connections(state_json)
            print(f"狀態已廣播 (needs_decision={needs_decision}, 活躍連接數: {len(active_connections)})")

            # 如果檢測到中斷需求，標記但繼續處理剩餘事件
            if needs_decision:
                print(f"檢測到決策需求，標記狀態但繼續處理剩餘事件 [線程ID: {thread_id}]")
                temp_state['decision_pending'] = True
            # --- 統一中斷檢測邏輯結束 ---

        # --- 統一後處理邏輯 ---
        print(f"事件循環完成，處理了 {event_count} 個事件 [線程ID: {thread_id}]")
        
        # 檢查事件循環中是否標記了決策需求
        decision_pending = temp_state.get('decision_pending', False)
        if decision_pending:
            print(f"🔥 檢測到待處理的決策需求，執行最終決策處理")
            
            # 清除內部標記並推送最終決策狀態
            temp_state.pop('decision_pending', None)
            
            serialized_final_state = serialize_state(temp_state)
            final_json = json.dumps(serialized_final_state)
            broadcast_to_sse_connections(final_json)
            print(f"💥 最終決策狀態已廣播到SSE連接 [線程ID: {thread_id}, 活躍連接數: {len(active_connections)}]")
            
            # 更新全局狀態並退出
            current_state = temp_state
            print(f"⚡ 最終決策處理完成，已更新全局狀態並結束線程 [線程ID: {thread_id}]")
            return
        
        # --- 最終統一中斷檢測 (替代第二層和第三層檢測) ---
        print(f"=== 最終工作流狀態檢查 ===")
        final_interrupt_result = check_workflow_interrupt(graph, thread_config, temp_state, thread_id)
        
        # 應用最終檢測結果
        temp_state = final_interrupt_result['updated_state']
        final_needs_interrupt = final_interrupt_result['needs_interrupt']
        
        print(f"最終中斷檢測結果: {final_interrupt_result['interrupt_type']} - {final_interrupt_result['reason']}")
        
        if final_needs_interrupt:
            print(f"🔄 檢測到最終中斷需求，推送中斷狀態")
            
            # 推送中斷狀態更新
            serialized_interrupt_state = serialize_state(temp_state)
            interrupt_json = json.dumps(serialized_interrupt_state)
            broadcast_to_sse_connections(interrupt_json)
            print(f"🔄 最終中斷狀態已廣播到SSE連接 [線程ID: {thread_id}, 活躍連接數: {len(active_connections)}]")
            
            # 更新全局狀態並退出
            current_state = temp_state
            print(f"✅ 最終中斷處理完成，已更新全局狀態並結束線程 [線程ID: {thread_id}]")
            return
        
        # 工作流正常完成
        print(f"工作流正常完成，無需中斷處理 [線程ID: {thread_id}]")
        current_state = temp_state

        # 推送最終狀態更新
        serialized_state = serialize_state(current_state)
        state_json = json.dumps(serialized_state)
        broadcast_to_sse_connections(state_json)
        print(f"最終狀態已廣播到SSE連接 [線程ID: {thread_id}, 活躍連接數: {len(active_connections)}]")

    except Exception as e:
        print(f"後台處理錯誤 [線程ID: {thread_id}]: {str(e)}")
        print(f"錯誤追踪: {traceback.format_exc()}")
        # Optionally push an error state via SSE
        error_state = {**serialize_state(current_state), "error": str(e)}
        broadcast_to_sse_connections(json.dumps(error_state))
        print(f"錯誤狀態已廣播到SSE連接 [線程ID: {thread_id}]")


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
            # 關鍵修復：新用戶輸入時清除所有決策相關標誌
            print(f"添加用戶消息到狀態: '{message}' - 清除決策標誌")
            input_state["messages"] = current_state["messages"] + [HumanMessage(content=message)]
            # 清除所有決策相關的狀態標誌，確保新工作流能正常中斷
            input_state["user_choice_continue"] = False
            input_state["force_process"] = False
            input_state["process_decision"] = ""
            input_state["workflow_in_progress"] = False
            input_state["needs_decision"] = False
            print("新用戶輸入，已清除所有決策標誌，允許正常中斷檢測")
        
        # Add process_decision if provided
        if process_decision:
            print(f"添加決策到狀態: process_decision={process_decision}")
            input_state["process_decision"] = process_decision
            # 設置決策標誌，表示用戶已做出決策
            input_state["user_choice_continue"] = True
            input_state["workflow_in_progress"] = True
            # Add system message to show the decision
            decision_text = "重新生成假設" if process_decision == "1" else "繼續研究"
            input_state["messages"] = input_state["messages"] + [
                HumanMessage(content=f"已選擇: {decision_text}")
            ]
            print(f"設置決策標誌：user_choice_continue=True, workflow_in_progress=True")
        
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
            
            # 廣播文件上傳狀態
            file_info = get_file_info(filepath)
            if file_info:
                file_info['id'] = f"file_{len(uploaded_files)}"
                broadcast_file_update({
                    "type": "file_uploaded",
                    "file": file_info,
                    "timestamp": datetime.now().isoformat()
                })
        
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

# New SSE endpoint with improved connection management and broadcasting
@app.route('/stream')
def event_stream():
    print("SSE連接已建立 - 客戶端已連接到/stream端點")
    
    def generate():
        global connection_counter
        connection_counter += 1
        connection_id = f"conn_{connection_counter}"
        
        # Create a dedicated queue for this connection
        connection_queue = Queue()
        active_connections[connection_id] = connection_queue
        
        print(f"SSE生成器已啟動 [ID: {connection_id}, 活躍連接數: {len(active_connections)}]")
        
        try:
            # 發送初始連接確認
            initial_message = json.dumps({"status": "connected", "connection_id": connection_id})
            yield f"event: connection_established\ndata: {initial_message}\n\n"
            print(f"已發送SSE連接確認 [ID: {connection_id}]")
            
            # 發送心跳以保持連接活躍
            heartbeat_count = 0
            
            while True:
                try:
                    # 使用超時機制避免無限阻塞
                    print(f"等待消息... [ID: {connection_id}, 隊列大小: {connection_queue.qsize()}]")
                    
                    try:
                        message = connection_queue.get(timeout=30)  # 30秒超時
                        print(f"從隊列獲取到消息，準備發送 [ID: {connection_id}]")
                        sse_data = f"event: state_update\ndata: {message}\n\n"
                        yield sse_data
                        print(f"✅ 成功發送SSE消息 [ID: {connection_id}]")
                        
                    except Empty:
                        # 超時時發送心跳保持連接
                        heartbeat_count += 1
                        heartbeat_message = json.dumps({
                            "type": "heartbeat",
                            "timestamp": datetime.now().isoformat(),
                            "connection_id": connection_id,
                            "heartbeat_count": heartbeat_count
                        })
                        yield f"event: heartbeat\ndata: {heartbeat_message}\n\n"
                        print(f"💓 發送心跳 [ID: {connection_id}, 心跳 #{heartbeat_count}]")
                        continue
                        
                except GeneratorExit:
                    print(f"SSE連接正常關閉 [ID: {connection_id}]")
                    break
                except Exception as e:
                    print(f"❌ SSE生成器錯誤 [ID: {connection_id}]: {e}")
                    # 記錄錯誤但繼續嘗試，避免因小錯誤中斷整個連接
                    error_message = json.dumps({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    try:
                        yield f"event: error\ndata: {error_message}\n\n"
                    except:
                        break  # 如果連接真的斷了，退出循環
                        
        except Exception as e:
            print(f"❌ SSE連接異常 [ID: {connection_id}]: {e}")
        finally:
            # 清理連接
            if connection_id in active_connections:
                del active_connections[connection_id]
            print(f"🧹 SSE連接已清理 [ID: {connection_id}, 剩餘活躍連接數: {len(active_connections)}]")
            
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    print("SSE響應已創建並返回")
    return response

# 廣播函數：將消息發送到所有活躍的SSE連接
def broadcast_to_sse_connections(message):
    """將消息廣播到所有活躍的SSE連接 - 修復版本，改善超時和重試機制"""
    if not active_connections:
        print("⚠️ 沒有活躍的SSE連接，跳過廣播")
        return
        
    print(f"📡 開始廣播到 {len(active_connections)} 個活躍連接")
    broadcasted_count = 0
    failed_connections = []
    retry_connections = []
    
    # 第一輪嘗試：使用較長的超時時間
    for connection_id, connection_queue in active_connections.items():
        try:
            connection_queue.put(message, timeout=5)  # 增加到5秒超時
            broadcasted_count += 1
            print(f"✅ 消息已發送到連接 [ID: {connection_id}]")
        except queue.Full:
            print(f"⚠️ 連接隊列已滿，準備重試 [ID: {connection_id}]")
            retry_connections.append((connection_id, connection_queue))
        except Exception as e:
            print(f"❌ 發送到連接失敗 [ID: {connection_id}]: {e}")
            failed_connections.append(connection_id)
    
    # 第二輪重試：對隊列滿的連接進行重試
    if retry_connections:
        print(f"🔄 對 {len(retry_connections)} 個連接進行重試")
        import time
        time.sleep(0.1)  # 短暫等待，讓隊列可能有空間
        
        for connection_id, connection_queue in retry_connections:
            try:
                connection_queue.put(message, timeout=2)  # 重試時使用較短超時
                broadcasted_count += 1
                print(f"✅ 重試成功，消息已發送到連接 [ID: {connection_id}]")
            except queue.Full:
                print(f"❌ 重試失敗，隊列仍滿 [ID: {connection_id}]")
                failed_connections.append(connection_id)
            except Exception as e:
                print(f"❌ 重試發送失敗 [ID: {connection_id}]: {e}")
                failed_connections.append(connection_id)
    
    # 清理失敗的連接
    for connection_id in failed_connections:
        if connection_id in active_connections:
            del active_connections[connection_id]
            print(f"🧹 清理失敗連接 [ID: {connection_id}]")
    
    print(f"📡 廣播完成：成功 {broadcasted_count}，失敗 {len(failed_connections)}，剩餘活躍連接 {len(active_connections)}")
    
    # 關鍵修復：驗證廣播完整性
    if broadcasted_count > 0:
        print(f"✅ SSE 廣播完整性檢查：{broadcasted_count}/{len(active_connections) + len(failed_connections)} 連接成功")
    else:
        print(f"⚠️ SSE 廣播完整性警告：沒有任何連接成功接收消息")

# 設定管理API端點
SETTINGS_FILE = './settings.json'

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
        print(f"🔍 開始保存設定到檔案...")
        print(f"- 目標檔案路徑: {SETTINGS_FILE}")
        print(f"- 目標目錄: {os.path.dirname(SETTINGS_FILE)}")
        print(f"- 設定數據大小: {len(str(settings))} 字符")
        
        # 確保目錄存在
        target_dir = os.path.dirname(SETTINGS_FILE)
        if not os.path.exists(target_dir):
            print(f"📁 創建目錄: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
        else:
            print(f"✅ 目錄已存在: {target_dir}")
        
        # 檢查目錄權限
        if not os.access(target_dir, os.W_OK):
            raise PermissionError(f"沒有寫入權限: {target_dir}")
        print(f"✅ 目錄寫入權限檢查通過")
        
        # 創建備份（如果檔案已存在）
        if os.path.exists(SETTINGS_FILE):
            backup_file = f"{SETTINGS_FILE}.backup"
            import shutil
            shutil.copy2(SETTINGS_FILE, backup_file)
            print(f"💾 已創建備份檔案: {backup_file}")
        
        print(f"💾 開始寫入設定檔案...")
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        # 驗證檔案是否成功創建
        if os.path.exists(SETTINGS_FILE):
            file_size = os.path.getsize(SETTINGS_FILE)
            print(f"✅ 設定檔案創建成功!")
            print(f"- 檔案路徑: {os.path.abspath(SETTINGS_FILE)}")
            print(f"- 檔案大小: {file_size} bytes")
            
            # 驗證檔案內容是否可讀
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                print(f"✅ 檔案內容驗證成功，包含 {len(test_data)} 個頂級鍵")
            except Exception as verify_error:
                print(f"⚠️ 檔案內容驗證失敗: {verify_error}")
        else:
            raise FileNotFoundError("檔案創建後仍不存在")
            
        return True
    except Exception as e:
        print(f"❌ 保存設定失敗: {e}")
        print(f"- 錯誤類型: {type(e).__name__}")
        print(f"- 工作目錄: {os.getcwd()}")
        print(f"- 檔案路徑: {os.path.abspath(SETTINGS_FILE)}")
        import traceback
        print(f"- 錯誤堆疊: {traceback.format_exc()}")
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
        print(f"📥 收到設定更新請求")
        print(f"- 請求方法: {request.method}")
        print(f"- 內容類型: {request.content_type}")
        print(f"- 請求數據大小: {len(request.get_data())} bytes")
        
        # 驗證請求數據
        if not request.json:
            error_msg = "無效的請求數據"
            print(f"❌ {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 400
        
        settings = request.json
        print(f"📋 收到設定數據，包含鍵: {list(settings.keys())}")
        
        # 添加最後修改時間
        settings['lastModified'] = datetime.now().isoformat()
        print(f"⏰ 已添加最後修改時間: {settings['lastModified']}")
        
        # 保存設定
        print(f"💾 開始保存設定...")
        if save_settings(settings):
            success_msg = "設定已保存"
            print(f"✅ {success_msg}")
            
            # 再次檢查檔案是否存在
            if os.path.exists(SETTINGS_FILE):
                file_info = os.stat(SETTINGS_FILE)
                print(f"📁 檔案確認存在: {os.path.abspath(SETTINGS_FILE)}")
                print(f"- 檔案大小: {file_info.st_size} bytes")
                print(f"- 修改時間: {datetime.fromtimestamp(file_info.st_mtime)}")
            else:
                print(f"⚠️ 警告: 保存函數返回成功但檔案不存在")
            
            return jsonify({"status": "success", "message": success_msg})
        else:
            error_msg = "保存設定失敗"
            print(f"❌ {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 500
            
    except Exception as e:
        error_msg = f"處理設定更新時發生錯誤: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"- 錯誤堆疊: {traceback.format_exc()}")
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
