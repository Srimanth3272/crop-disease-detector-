// Global state
let selectedFile = null;
let currentLanguage = 'en';
let currentResults = null;

// Translations mock database (could be expanded)
const translations = {
    'en': {
        'appTitle': 'Smart Paddy Detector',
        'uploadInstruction': 'Upload Paddy Leaf Image',
        'uploadSubtext': 'Take a clear picture of the infected leaf for accurate diagnosis.',
        'dragDrop': 'Tap here to choose or capture image',
        'analyzeBtn': 'Analyze Image',
        'analyzing': 'AI is analyzing the leaf...',
        'resultTitle': 'Diagnosis Result',
        'confidence': 'Confidence Score',
        'severity': 'Severity Level',
        'guideCause': 'Cause',
        'guidePrecautions': 'Precautions',
        'guideFertilizers': 'Recommended Fertilizers',
        'guideOrganic': 'Organic Treatment',
        'guidePesticides': 'Pesticides',
        'resetBtn': 'Analyze Another Image',
        'voiceIntro': 'Disease detected is',
        'errorLoad': 'Error processing image. Please try again.'
    },
    'te': { // Telugu
        'appTitle': 'స్మార్ట్ ప్యాడీ డిటెక్టర్',
        'uploadInstruction': 'వరి ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి',
        'uploadSubtext': 'ఖచ్చితమైన రోగ నిర్ధారణ కోసం వ్యాధి సోకిన ఆకు చిత్రాన్ని తీయండి.',
        'dragDrop': 'చిత్రాన్ని ఎంచుకోవడానికి ఇక్కడ నొక్కండి',
        'analyzeBtn': 'చిత్రాన్ని విశ్లేషించండి',
        'analyzing': 'AI ఆకును విశ్లేషిస్తోంది...',
        'resultTitle': 'రోగనిర్ధారణ ఫలితం',
        'confidence': 'గుర్తింపు శాతం',
        'severity': 'తీవ్రత స్థాయి',
        'guideCause': 'కారణం',
        'guidePrecautions': 'తీసుకోవాల్సిన జాగ్రత్తలు',
        'guideFertilizers': 'సిఫార్సు చేసిన ఎరువులు',
        'guideOrganic': 'సేంద్రీయ చికిత్స',
        'guidePesticides': 'పురుగుమందులు',
        'resetBtn': 'మరొక చిత్రాన్ని విశ్లేషించండి',
        'voiceIntro': 'గుర్తించబడిన వ్యాధి',
        'errorLoad': 'లోపం. దయచేసి మళ్ళీ ప్రయత్నించండి.'
    },
    'hi': { // Hindi
        'appTitle': 'स्मार्ट पैडी डिटेक्टर',
        'uploadInstruction': 'धान के पत्ते की छवि अपलोड करें',
        'uploadSubtext': 'सटीक निदान के लिए संक्रमित पत्ते की एक स्पष्ट तस्वीर लें।',
        'dragDrop': 'छवि चुनने के लिए यहां टैप करें',
        'analyzeBtn': 'छवि का विश्लेषण करें',
        'analyzing': 'AI पत्ते का विश्लेषण कर रहा है...',
        'resultTitle': 'निदान परिणाम',
        'confidence': 'आत्मविश्वास स्कोर',
        'severity': 'गंभीरता स्तर',
        'guideCause': 'कारण',
        'guidePrecautions': 'एहतियात',
        'guideFertilizers': 'अनुशंसित उर्वरक',
        'guideOrganic': 'जैविक उपचार',
        'guidePesticides': 'कीटनाशक',
        'resetBtn': 'एक और छवि का विश्लेषण करें',
        'voiceIntro': 'मर्ज पाया गया है',
        'errorLoad': 'त्रुटि। कृपया पुनः प्रयास करें।'
    },
    'ta': { // Tamil
        'appTitle': 'ஸ்மார்ட் நெல் கண்டுபிடிப்பான்',
        'uploadInstruction': 'நெல் இலை படத்தை பதிவேற்றவும்',
        'uploadSubtext': 'துல்லியமான கண்டறிதலுக்கு பாதிக்கப்பட்ட இலையின் தெளிவான படத்தை எடுக்கவும்.',
        'dragDrop': 'படத்தை தட்டவும்',
        'analyzeBtn': 'அனலைஸ் செய்',
        'analyzing': 'AI ஆராய்கிறது...',
        'resultTitle': 'முடிவு',
        'confidence': 'உறுதித்தன்மை',
        'severity': 'தீவிரம்',
        'guideCause': 'காரணம்',
        'guidePrecautions': 'முன்னெச்சரிக்கைகள்',
        'guideFertilizers': 'உரங்கள்',
        'guideOrganic': 'இயற்கை சிகிச்சை',
        'guidePesticides': 'பூச்சிக்கொல்லிகள்',
        'resetBtn': 'மீண்டும் செய்',
        'voiceIntro': 'கண்டுபிடிக்கப்பட்ட நோய்',
        'errorLoad': 'பிழை. மீண்டும் முயற்சிக்கவும்.'
    }
};

// DOM Elements
const elements = {
    dropZone: document.getElementById('dropZone'),
    imageInput: document.getElementById('imageInput'),
    imagePreview: document.getElementById('imagePreview'),
    uploadPlaceholder: document.getElementById('uploadPlaceholder'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    resultsSection: document.getElementById('resultsSection'),
    languageSelect: document.getElementById('languageSelect'),
    resetBtn: document.getElementById('resetBtn'),
    voiceBtn: document.getElementById('voiceBtn'),
    // Result Outputs
    diseaseName: document.getElementById('diseaseName'),
    confidenceVal: document.getElementById('confidenceVal'),
    severityVal: document.getElementById('severityVal'),
    guideCauseText: document.getElementById('guideCauseText'),
    guidePrecautionsText: document.getElementById('guidePrecautionsText'),
    guideFertilizersText: document.getElementById('guideFertilizersText'),
    guideOrganicText: document.getElementById('guideOrganicText'),
    guidePesticidesText: document.getElementById('guidePesticidesText')
};

// --- Initialization & Flow ---

document.addEventListener('DOMContentLoaded', () => {
    updateLanguage();
});

// The input covers the whole dropZone invisibly, so no JS bridging needed for click
elements.imageInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

elements.dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.dropZone.classList.add('dragover');
});

elements.dropZone.addEventListener('dragleave', () => elements.dropZone.classList.remove('dragover'));

elements.dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

function handleFileSelect(file) {
    // Alert nicely if file is not an image
    if (!file.type.startsWith('image/')) {
        alert("Please upload a valid image file!");
        return;
    }
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.imagePreview.src = e.target.result;
        elements.imagePreview.classList.remove('hidden');
        elements.uploadPlaceholder.classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

// Reset Flow
elements.resetBtn.addEventListener('click', () => {
    selectedFile = null;
    currentResults = null;
    elements.imageInput.value = '';
    elements.imagePreview.classList.add('hidden');
    elements.uploadPlaceholder.classList.remove('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.analyzeBtn.classList.remove('hidden');
    
    // Stop speaking if active
    if('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
});

// --- API Interaction ---

elements.analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert("Please upload a leaf image first before clicking Analyze!");
        return;
    }
    
    // Show loading
    elements.analyzeBtn.classList.add('hidden');
    elements.loadingIndicator.classList.remove('hidden');
    elements.resultsSection.classList.add('hidden');
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('lang', currentLanguage); // Send current UI language

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });
        
        if(!response.ok) throw new Error("Server error - Make sure your Python Flask backend is running!");
        
        currentResults = await response.json();
        displayResults(currentResults);
        
    } catch (err) {
        console.error(err);
        alert("Could not connect to backend! Are you sure your Python Flask server (app.py) is running? Error: " + err.message);
        elements.analyzeBtn.classList.remove('hidden');
    } finally {
        elements.loadingIndicator.classList.add('hidden');
    }
});

function displayResults(data) {
    elements.diseaseName.textContent = data.disease;
    elements.confidenceVal.textContent = Math.round(data.confidence * 100) + '%';
    
    elements.severityVal.textContent = data.severity;
    elements.severityVal.className = 'metric-val severity-' + data.severity;
    
    elements.guideCauseText.textContent = data.cause;
    elements.guidePrecautionsText.textContent = data.precautions;
    elements.guideFertilizersText.textContent = data.fertilizers;
    elements.guideOrganicText.textContent = data.organic;
    elements.guidePesticidesText.textContent = data.pesticides;
    
    elements.resultsSection.classList.remove('hidden');
}

// --- Voice Assistance ---

elements.voiceBtn.addEventListener('click', () => {
    if (!currentResults || !('speechSynthesis' in window)) {
        alert("Your browser does not support the Voice Assistant feature.");
        return;
    }
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    const dict = translations[currentLanguage];
    const intro = dict['voiceIntro'];
    const disease = currentResults.disease;
    
    // We compose a simple text to read entirely localized
    const textToRead = `${intro} ${disease}. 
        ${dict['confidence']}: ${Math.round(currentResults.confidence * 100)} percent.
        ${dict['severity']}: ${currentResults.severity}.
        ${dict['guidePrecautions']}: ${currentResults.precautions}
    `;

    const utterance = new SpeechSynthesisUtterance(textToRead);
    
    // Set matching language voice
    if(currentLanguage === 'hi') utterance.lang = 'hi-IN';
    else if(currentLanguage === 'te') utterance.lang = 'te-IN';
    else if(currentLanguage === 'ta') utterance.lang = 'ta-IN';
    else utterance.lang = 'en-US';
    
    utterance.rate = 0.9;
    
    // Helpful error catching if the computer lacks the voice pack
    utterance.onerror = (event) => {
        console.error('SpeechSynthesisUtterance.onerror', event);
        alert(`An error occurred while trying to speak. Your device might not have the ${utterance.lang} language voice pack installed in your OS settings!`);
    };

    window.speechSynthesis.speak(utterance);
});

// --- Multilingual Support ---

elements.languageSelect.addEventListener('change', (e) => {
    currentLanguage = e.target.value;
    updateLanguage();
});

function updateLanguage() {
    const dict = translations[currentLanguage] || translations['en'];
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });
}
