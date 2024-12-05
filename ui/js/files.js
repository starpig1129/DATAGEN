class FileManager {
    constructor() {
        this.files = [];
        this.filesContent = document.getElementById('filesContent');
        
        // Initial file fetch
        this.fetchFiles();
        
        // Start polling for file updates
        this.startPolling();
    }

    async fetchFiles() {
        try {
            const response = await fetch(`${window.apiConfig.apiBaseUrl}/api/files`);
            const data = await response.json();
            this.updateFiles(data.files);
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    }

    startPolling() {
        // Poll every 5 seconds
        setInterval(() => this.fetchFiles(), 5000);
    }

    updateFiles(newFiles) {
        this.files = newFiles;
        this.render();
    }

    render() {
        this.filesContent.innerHTML = '';

        this.files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.textContent = file;
            this.filesContent.appendChild(fileItem);
        });
    }
}

// Create global file manager instance
const fileManager = new FileManager();
