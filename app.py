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
    "sender": ""
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

def check_needs_decision(messages):
    """Check if the current state needs user decision"""
    if not messages:
        return False
    
    # Get the last message
    last_message = messages[-1]
    content = ""
    
    if isinstance(last_message, (HumanMessage, AIMessage)):
        content = last_message.content
    elif isinstance(last_message, dict):
        content = last_message.get('content', '')
    elif isinstance(last_message, str):
        content = last_message
    
    decision_phrases = [
        "Please enter your choice",
        "please enter your choice",
        "Please choose",
        "請選擇",
        "Enter your choice",
        "Choose between",
        "Select an option"
    ]
    
    return any(phrase in content for phrase in decision_phrases)

import traceback # Add traceback import for background error handling

def process_message_background(input_state):
    """Processes the message in a background thread."""
    global current_state, sse_queue, system
    try:
        # Run the system with input (This is the blocking part)
        events = system.workflow_manager.get_graph().stream(
            input_state,
            {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
            stream_mode="values",
            debug=False
        )

        # Update state with results
        temp_state = input_state.copy() # Work on a copy within the thread initially
        for event in events:
            for key in temp_state:
                if key != "messages" and key in event:
                    temp_state[key] = event[key]
            if "messages" in event and event["messages"]:
                # Update messages carefully
                temp_state["messages"] = [
                    msg for msg in event["messages"]
                    if isinstance(msg, (HumanMessage, AIMessage, dict, str))
                ]

            # Check if decision is needed after processing this event's messages
            needs_decision = check_needs_decision(temp_state.get("messages", []))
            if needs_decision:
                temp_state['needs_decision'] = True
                current_state = temp_state # Update global state immediately
                serialized_state = serialize_state(current_state)
                state_json = json.dumps(serialized_state)
                sse_queue.put(state_json)
                print("Decision needed, state pushed to SSE. Ending background thread.")
                return # Exit the background function immediately

        # --- Code after the loop (only runs if no decision was needed during the loop) ---
        # If the loop completes without returning, it means no decision was needed.

        # Safely update the global state
        temp_state['needs_decision'] = False # Explicitly set to false as loop completed
        current_state = temp_state # Update global state

        # Serialize and push final state update via SSE
        serialized_state = serialize_state(current_state)
        state_json = json.dumps(serialized_state)
        sse_queue.put(state_json)
        print("Background processing complete (no decision needed), state pushed to SSE.") # Modified log

    except Exception as e:
        print(f"Error in background processing: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # Optionally push an error state via SSE
        error_state = {**serialize_state(current_state), "error": str(e)}
        sse_queue.put(json.dumps(error_state))


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
    
    try:
        # Create input state
        input_state = current_state.copy()
        
        if message:
            # Add new message to state
            input_state["messages"] = current_state["messages"] + [HumanMessage(content=message)]
        
        # Add process_decision if provided
        if process_decision:
            input_state["process_decision"] = process_decision
            # Add system message to show the decision
            decision_text = "重新生成假設" if process_decision == "1" else "繼續研究"
            input_state["messages"] = input_state["messages"] + [
                HumanMessage(content=f"已選擇: {decision_text}")
            ]
        
        # Create and start the background thread
        thread = threading.Thread(target=process_message_background, args=(input_state.copy(),)) # Pass a copy of input_state
        thread.start()
        print("Started background thread for message processing.") # Add log

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
        # Check if decision is needed based on current messages
        needs_decision = check_needs_decision(current_state.get("messages", []))
        serialized_state = serialize_state(current_state)
        # Combine serialized state with the needs_decision flag
        response_data = {**serialized_state, "needs_decision": needs_decision}
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
    def generate():
        while True:
            try:
                # Block until a message is available
                message = sse_queue.get(timeout=None) # No timeout, wait indefinitely
                # Format as SSE message
                yield f"event: state_update\ndata: {message}\n\n"
                sse_queue.task_done() # Mark message as processed
            except Exception as e:
                print(f"Error in SSE generator: {e}")
                # Optionally break or handle specific errors
                break # Exit loop on error to prevent infinite loops on persistent issues
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001) # Change port to 5001
