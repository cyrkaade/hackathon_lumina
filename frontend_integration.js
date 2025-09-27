/**
 * Frontend Integration Example for Call Center Assessment API
 * Use this code in your frontend to connect to your backend
 */

class CallCenterAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * Upload audio file for assessment
     * @param {File} audioFile - Audio file to upload
     * @param {string} language - Language code (ru/kk)
     * @returns {Promise<Object>} Upload response with assessment
     */
    async uploadCall(audioFile, language = 'ru') {
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('language', language);

        try {
            const response = await fetch(`${this.baseURL}/api/upload-call`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * Get the latest assessment result
     * @returns {Promise<Object>} Latest assessment results
     */
    async getLatestAssessment() {
        try {
            const response = await fetch(`${this.baseURL}/api/latest-assessment`);

            if (!response.ok) {
                throw new Error(`Assessment fetch failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Assessment error:', error);
            throw error;
        }
    }

    /**
     * Get assessment results for a specific call
     * @param {string} callId - Call ID
     * @returns {Promise<Object>} Assessment results
     */
    async getAssessment(callId) {
        try {
            const response = await fetch(`${this.baseURL}/api/assessment/${callId}`);

            if (!response.ok) {
                throw new Error(`Assessment fetch failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Assessment error:', error);
            throw error;
        }
    }

    /**
     * Trigger assessment for a call
     * @param {string} callId - Call ID
     * @param {string} language - Language code
     * @returns {Promise<Object>} Assessment response
     */
    async assessCall(callId, language = 'ru') {
        try {
            const response = await fetch(`${this.baseURL}/api/assess-call/${callId}?language=${language}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Assessment failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Assessment error:', error);
            throw error;
        }
    }

    /**
     * Get worker performance data
     * @param {number} workerId - Worker ID
     * @param {number} days - Number of days to look back
     * @returns {Promise<Object>} Worker performance data
     */
    async getWorkerPerformance(workerId, days = 30) {
        try {
            const response = await fetch(`${this.baseURL}/api/worker/${workerId}/performance?days=${days}`);

            if (!response.ok) {
                throw new Error(`Performance fetch failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Performance error:', error);
            throw error;
        }
    }

    /**
     * Get worker rankings
     * @param {string} department - Department filter (optional)
     * @param {number} limit - Number of results to return
     * @returns {Promise<Object>} Worker rankings
     */
    async getWorkerRankings(department = null, limit = 10) {
        try {
            let url = `${this.baseURL}/api/workers/rankings?limit=${limit}`;
            if (department) {
                url += `&department=${department}`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Rankings fetch failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Rankings error:', error);
            throw error;
        }
    }
}

// React Component Example
const CallAssessmentComponent = () => {
    const [api] = useState(new CallCenterAPI('http://localhost:8000'));
    const [uploading, setUploading] = useState(false);
    const [assessment, setAssessment] = useState(null);
    const [error, setError] = useState(null);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setUploading(true);
        setError(null);

        try {
            // Upload the file and get assessment immediately
            const uploadResult = await api.uploadCall(file, 'ru');
            console.log('Upload successful:', uploadResult);

            if (uploadResult.status === 'success' && uploadResult.assessment) {
                setAssessment(uploadResult.assessment);
            } else {
                setError(uploadResult.message || 'Assessment failed');
            }
            
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <h2>Call Center Assessment</h2>
            
            <input 
                type="file" 
                accept=".wav,.mp3,.m4a" 
                onChange={handleFileUpload}
                disabled={uploading}
            />
            
            {uploading && <p>Processing audio...</p>}
            
            {error && <p style={{color: 'red'}}>Error: {error}</p>}
            
            {assessment && (
                <div>
                    <h3>Assessment Results</h3>
                    <p>Total Score: {assessment.total_score}</p>
                    <p>Emotion Score: {assessment.emotion_score}</p>
                    <p>Resolution Score: {assessment.resolution_score}</p>
                    <p>Communication Score: {assessment.communication_score}</p>
                    <p>Professionalism Score: {assessment.professionalism_score}</p>
                </div>
            )}
        </div>
    );
};

// Vue.js Component Example
const CallAssessmentVue = {
    data() {
        return {
            api: new CallCenterAPI('http://localhost:8000'),
            uploading: false,
            assessment: null,
            error: null
        };
    },
    methods: {
        async handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            this.uploading = true;
            this.error = null;

            try {
                const uploadResult = await this.api.uploadCall(file, 'ru');
                console.log('Upload successful:', uploadResult);

                if (uploadResult.status === 'success' && uploadResult.assessment) {
                    this.assessment = uploadResult.assessment;
                } else {
                    this.error = uploadResult.message || 'Assessment failed';
                }
                
            } catch (err) {
                this.error = err.message;
            } finally {
                this.uploading = false;
            }
        }
    },
    template: `
        <div>
            <h2>Call Center Assessment</h2>
            <input 
                type="file" 
                accept=".wav,.mp3,.m4a" 
                @change="handleFileUpload"
                :disabled="uploading"
            />
            <p v-if="uploading">Processing audio...</p>
            <p v-if="error" style="color: red">Error: {{ error }}</p>
            <div v-if="assessment">
                <h3>Assessment Results</h3>
                <p>Total Score: {{ assessment.total_score }}</p>
                <p>Emotion Score: {{ assessment.emotion_score }}</p>
                <p>Resolution Score: {{ assessment.resolution_score }}</p>
                <p>Communication Score: {{ assessment.communication_score }}</p>
                <p>Professionalism Score: {{ assessment.professionalism_score }}</p>
            </div>
        </div>
    `
};

// Vanilla JavaScript Example
document.addEventListener('DOMContentLoaded', () => {
    const api = new CallCenterAPI('http://localhost:8000');
    const fileInput = document.getElementById('audioFile');
    const resultsDiv = document.getElementById('results');

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        try {
            resultsDiv.innerHTML = 'Uploading and processing...';
            
            const uploadResult = await api.uploadCall(file, 'ru');
            console.log('Upload successful:', uploadResult);

            if (uploadResult.status === 'success' && uploadResult.assessment) {
                const assessment = uploadResult.assessment;
                resultsDiv.innerHTML = `
                    <h3>Assessment Results</h3>
                    <p>Total Score: ${assessment.total_score}</p>
                    <p>Emotion Score: ${assessment.emotion_score}</p>
                    <p>Resolution Score: ${assessment.resolution_score}</p>
                    <p>Communication Score: ${assessment.communication_score}</p>
                    <p>Professionalism Score: ${assessment.professionalism_score}</p>
                `;
            } else {
                resultsDiv.innerHTML = `<p style="color: red">Error: ${uploadResult.message || 'Assessment failed'}</p>`;
            }
            
        } catch (error) {
            resultsDiv.innerHTML = `<p style="color: red">Error: ${error.message}</p>`;
        }
    });
});

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CallCenterAPI;
}
