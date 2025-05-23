import json # Add json import
from queue import Queue # Add Queue import
from flask import Flask, request, jsonify, send_from_directory, Response # Add Response import
from flask_cors import CORS
# from flask_sse import sse # Remove Flask-SSE import
import os
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
        
        events = system.workflow_manager.get_graph().stream(
            input_state,
            {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
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
                print(f"需要用戶決策，已清除process_decision")

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
        # If the loop completes without returning, it means no decision was needed throughout the stream.
        print(f"工作流完成，處理了 {event_count} 個事件 [線程ID: {thread_id}]")

        # Safely update the global state with the final accumulated state
        temp_state['needs_decision'] = False # Explicitly set to false as loop completed without needing decision
        current_state = temp_state # Update global state
        print(f"已更新全局狀態，不需要決策 [線程ID: {thread_id}]")

        # Serialize and push the final state update via SSE
        # This ensures the final state with needs_decision=False is sent.
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

@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        # List files in data_storage directory
        if os.path.exists('data_storage'):
            files = os.listdir('data_storage')
            return jsonify({"files": files})
        else:
            return jsonify({"files": []})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001) # Change port to 5001
