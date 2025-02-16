// State management
class State {
    constructor() {
        this.data = {
            messages: [],
            hypothesis: "",
            process: "",
            process_decision: "",
            visualization_state: "",
            searcher_state: "",
            code_state: "",
            report_section: "",
            quality_review: "",
            needs_revision: false,
            sender: ""
        };
        
        // Start polling for state updates
        this.startPolling();
    }

    async fetchState() {
        try {
            const response = await fetch(`${window.apiConfig.apiBaseUrl}/api/state`);
            const newState = await response.json();
            
            // Check if messages have changed
            const hasNewMessages = JSON.stringify(this.data.messages) !== JSON.stringify(newState.messages);
            
            // Update state
            this.update(newState);
            
            // If there are new messages, update chat
            if (hasNewMessages && window.chatManager) {
                window.chatManager.updateFromState(newState.messages);
            }
        } catch (error) {
            console.error('Error fetching state:', error);
        }
    }

    startPolling() {
        // Poll every 2 seconds
        setInterval(() => this.fetchState(), 2000);
    }

    update(newState) {
        // Deep copy the new state
        this.data = JSON.parse(JSON.stringify(newState));
        this.render();
    }

    render() {
        const stateContent = document.getElementById('stateContent');
        if (!stateContent) return;
        
        stateContent.innerHTML = '';

        // 首先顯示當前代理
        if (this.data.sender) {
            const activeAgentItem = document.createElement('div');
            activeAgentItem.className = 'state-item active-agent';
            
            const agentLabel = document.createElement('div');
            agentLabel.className = 'state-label';
            agentLabel.textContent = 'ACTIVE AGENT';
            
            const agentValue = document.createElement('div');
            agentValue.className = 'state-value';
            agentValue.textContent = this.data.sender;
            
            activeAgentItem.appendChild(agentLabel);
            activeAgentItem.appendChild(agentValue);
            stateContent.appendChild(activeAgentItem);
        }

        // 然後顯示其他狀態
        Object.entries(this.data).forEach(([key, value]) => {
            if (key !== 'messages' && key !== 'sender') {  // Skip messages as they're shown in chat
                const stateItem = document.createElement('div');
                stateItem.className = 'state-item';
                
                const label = document.createElement('div');
                label.className = 'state-label';
                label.textContent = key.replace(/_/g, ' ').toUpperCase();
                
                const valueDiv = document.createElement('div');
                valueDiv.className = 'state-value';
                valueDiv.textContent = value || 'Not set';
                
                stateItem.appendChild(label);
                stateItem.appendChild(valueDiv);
                stateContent.appendChild(stateItem);
            }
        });
    }
}

// Create global state instance
const state = new State();

// Expose state globally for other components
window.state = state;
