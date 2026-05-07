document.addEventListener('DOMContentLoaded', () => {
    const API_URL = "http://127.0.0.1:8000";

    const translations = {
        'en': { 'brand': 'SmartDOX', 'subtitle': '| Government Tender Evaluation', 'step-1': '1. Process New Tender', 'step-2': '2. Evaluate Bidder', 'btn-extract': 'Extract Criteria', 'btn-analyze': 'Analyze Submission', 'output-title': 'Output Report:', 'btn-choose-file': 'Choose File' },
        'hi': { 'brand': 'स्मार्टडॉक्स', 'subtitle': '| सरकारी निविदा मूल्यांकन', 'step-1': '1. नई निविदा संसाधित करें', 'step-2': '2. बोलीदाता का मूल्यांकन करें', 'btn-extract': 'मानदंड निकालें', 'btn-analyze': 'सबमिशन का विश्लेषण करें', 'output-title': 'आउटपुट रिपोर्ट:', 'btn-choose-file': 'फ़ाइल चुनें' },
        'mr': { 'brand': 'स्मार्टडॉक्स', 'subtitle': '| सरकारी निविदा मूल्यांकन', 'step-1': '1. नवीन निविदा प्रक्रिया', 'step-2': '2. बोलीदात्याचे मूल्यांकन करा', 'btn-extract': 'निकष काढा', 'btn-analyze': 'विश्लेषण करा', 'output-title': 'आउटपुट रिपोर्ट:', 'btn-choose-file': 'फाईल निवडा' },
        'bn': { 'brand': 'স্মার্টডক্স', 'subtitle': '| সরকারি টেন্ডার মূল্যায়ন', 'step-1': '1. নতুন টেন্ডার প্রসেস করুন', 'step-2': '2. বিডার মূল্যায়ন করুন', 'btn-extract': 'মানদণ্ড বের করুন', 'btn-analyze': 'সাবমিশন বিশ্লেষণ করুন', 'output-title': 'আউটপুট রিপোর্ট:', 'btn-choose-file': 'ফাইল নির্বাচন করুন' },
        'ta': { 'brand': 'ஸ்மார்ட் டாக்ஸ்', 'subtitle': '| அரசு டெண்டர் மதிப்பீடு', 'step-1': '1. புதிய டெண்டர் செயலாக்கம்', 'step-2': '2. ஏலதாரரை மதிப்பிடுங்கள்', 'btn-extract': 'நிபந்தனைகளை பிரித்தெடுக்கவும்', 'btn-analyze': 'বিশ্লেஷிக்கவும்', 'output-title': 'வெளியீட்டு அறிக்கை:', 'btn-choose-file': 'கோப்பைத் தேர்ந்தெடுக்கவும்' }
    };

    // --- DOM ELEMENTS ---
    const tenderInput = document.getElementById('tenderFile');
    const bidderInput = document.getElementById('bidderFile');
    const langSelector = document.getElementById('langSelector');
    const chatBox = document.getElementById('chatBox');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');

    // --- FILE INPUT HANDLERS ---
    if(tenderInput) {
        tenderInput.addEventListener('change', (e) => {
            const span = document.getElementById('tenderFileName');
            if(span) span.textContent = e.target.files[0] ? e.target.files[0].name : "No file chosen";
        });
    }

    if(bidderInput) {
        bidderInput.addEventListener('change', (e) => {
            const span = document.getElementById('bidderFileName');
            if(span) span.textContent = e.target.files[0] ? e.target.files[0].name : "No file chosen";
        });
    }

    // --- UI HELPERS ---
    function updateUI(lang) {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                el.innerText = translations[lang][key];
            }
        });
    }

    if(langSelector) {
        langSelector.addEventListener('change', (e) => {
            updateUI(e.target.value);
        });
    }

    // --- API CALLS (Exposed to Window for HTML onclick) ---
window.uploadTender = async function() {
    const tenderInput = document.getElementById('tenderFile'); 
    const userId = localStorage.getItem('user_id'); 

    if (!tenderInput.files[0]) return alert("Please select a file");
    
    // Check agar userId null toh nahi
    if (!userId || userId === "null") {
        return alert("User ID not found! Please login again.");
    }

    const formData = new FormData();
    formData.append("file", tenderInput.files[0]);

    showLoader("Extracting Criteria...");

    try {
        // DHAYAN SE: URL ke peeche ?user_id=${userId} hona compulsory hai
        const response = await fetch(`${API_URL}/upload-tender?user_id=${userId}`, { 
            method: 'POST', 
            body: formData 
        });

        const data = await response.json();
        
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            displayResult(data);
            alert("Tender processed and saved to your history!");
            // Optional: History refresh karne ke liye agar usi page par ho
            if (typeof loadHistory === "function") loadHistory();
        }
    } catch (e) { 
        console.error("Fetch error:", e);
        alert("Error connecting to backend"); 
    }
};

    window.evaluateBidder = async function() {
        if (!bidderInput.files[0]) return alert("Please select a file");
        const lang = langSelector ? langSelector.value : 'en';
        const formData = new FormData();
        formData.append("file", bidderInput.files[0]);
        showLoader(`Analyzing... (${lang.toUpperCase()})`);
        try {
            const response = await fetch(`${API_URL}/evaluate-bidder?lang=${lang}`, { method: 'POST', body: formData });
            displayResult(await response.json());
        } catch (e) { alert("Error connecting to backend"); }
    };

    // --- CHATBOT LOGIC ---
    window.toggleChat = function() {
        if(chatBox) chatBox.classList.toggle('hidden');
    };

    window.sendMessage = async function() {
        const msg = userInput.value.trim();
        if (!msg) return;

        // Add User Message UI
        const userDiv = document.createElement('div');
        userDiv.className = 'p-2 rounded-lg max-w-[80%] bg-blue-700 ml-auto text-white shadow-sm';
        userDiv.textContent = msg;
        chatMessages.appendChild(userDiv);
        userInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await response.json();
            
            // Add Bot Response UI
            const botDiv = document.createElement('div');
            botDiv.className = 'p-2 rounded-lg max-w-[80%] bg-gray-800 mr-auto text-white shadow-sm border border-gray-700';
            botDiv.textContent = data.reply;
            chatMessages.appendChild(botDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (e) {
            alert("Chatbot backend not connected!");
        }
    };

    // --- HISTORY LOGIC ---
    window.showHistory = async function() {
        const modal = document.getElementById('historyModal');
        const content = document.getElementById('historyContent');
        
        if(!modal || !content) return;

        modal.classList.remove('hidden'); 
        content.innerHTML = '<div class="text-center py-10"><p class="text-blue-400 animate-pulse">Loading history from database...</p></div>';

        try {
            const response = await fetch(`${API_URL}/chat/history`);
            const data = await response.json();

            if (!data || data.length === 0) {
                content.innerHTML = '<p class="text-gray-500 text-center py-10">No history found yet. Start a conversation!</p>';
                return;
            }

            content.innerHTML = ''; 
            data.forEach(item => {
                const time = new Date(item.timestamp).toLocaleString();
                content.innerHTML += `
                    <div class="border-l-4 border-blue-600 pl-4 py-3 bg-gray-800 rounded-r-lg mb-4 shadow-md">
                        <p class="text-[10px] text-gray-500 font-bold uppercase mb-1">${time}</p>
                        <p class="text-blue-300 font-medium text-sm"><span class="text-white opacity-40">Q:</span> ${item.user_message}</p>
                        <hr class="border-gray-700 my-2">
                        <p class="text-green-400 text-sm"><span class="text-white opacity-40">A:</span> ${item.bot_response}</p>
                    </div>
                `;
            });
        } catch (error) {
            content.innerHTML = `<p class="text-red-500 text-center py-10 font-bold">Error: Could not connect to backend.</p>`;
        }
    };

    window.closeHistory = function() {
        const modal = document.getElementById('historyModal');
        if(modal) modal.classList.add('hidden');
    };
});

// --- GLOBAL UI HELPERS ---
function showLoader(msg) {
    const resultBox = document.getElementById('resultBox');
    const output = document.getElementById('outputData');
    if(resultBox) resultBox.classList.remove('hidden');
    if(output) output.innerText = msg;
}

function displayResult(data) {
    const resultBox = document.getElementById('resultBox');
    const output = document.getElementById('outputData');
    if(resultBox) resultBox.classList.remove('hidden');
    if(output) output.innerText = JSON.stringify(data, null, 4);
}