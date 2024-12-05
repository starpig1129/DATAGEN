from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from main import MultiAgentSystem
from core.state import State
from langchain_core.messages import HumanMessage, AIMessage

app = Flask(__name__, static_folder='ui')
CORS(app)  # Enable CORS for all routes

# Initialize the multi-agent system
system = MultiAgentSystem()

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
            "type": "human" if isinstance(msg, HumanMessage) else "assistant"
        }
    elif isinstance(msg, dict):
        return msg
    elif isinstance(msg, str):
        return {
            "content": msg,
            "type": "assistant"
        }
    else:
        return {
            "content": str(msg),
            "type": "assistant"
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

@app.route('/')
def index():
    return send_from_directory('ui', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('ui', path)

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
            decision_text = "Regenerate hypothesis" if process_decision == "1" else "Continue research"
            input_state["messages"] = input_state["messages"] + [
                HumanMessage(content=f"Selected option: {decision_text}")
            ]
        
        # Run the system with input
        events = system.workflow_manager.get_graph().stream(
            input_state,
            {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
            stream_mode="values",
            debug=False
        )
        
        # Update state with results
        for event in events:
            # Update non-message state fields
            for key in current_state:
                if key != "messages" and key in event:
                    current_state[key] = event[key]
            
            # Handle messages separately to maintain order
            if "messages" in event and event["messages"]:
                current_state["messages"] = [
                    msg for msg in event["messages"]
                    if isinstance(msg, (HumanMessage, AIMessage, dict, str))
                ]
        
        # Check if we need a process decision
        needs_decision = (
            not process_decision and 
            "Please choose the next step:" in str(current_state.get("messages", []))
        )
        
        # Serialize state for response
        serialized_state = serialize_state(current_state)
        
        return jsonify({
            "status": "success",
            "state": serialized_state,
            "needs_decision": needs_decision
        })
    except Exception as e:
        import traceback
        print("Error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        return jsonify(serialize_state(current_state))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
