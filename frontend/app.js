// --- Configuration ---
// The address of your running backend server.
const API_BASE_URL = 'http://127.0.0.1:8000';
// The mock security token for the secure endpoint.
const MOCK_ABHA_TOKEN = 'SIH2025_DUMMY_ABHA_TOKEN';

// --- DOM Element Selection ---
// This section gets all the interactive parts from your HTML page.
const searchInput = document.getElementById('search-input');
const namasteResultsList = document.getElementById('namaste-results');
const icdResultsList = document.getElementById('icd-results'); 
const loader = document.getElementById('loader');

const entryCard = document.getElementById('entry-card');
const selectedEntryContent = document.getElementById('selected-entry-content');
const createBundleBtn = document.getElementById('create-bundle-btn');

const bundleCard = document.getElementById('bundle-card');
const fhirBundleOutput = document.getElementById('fhir-bundle-output');
const submitBundleBtn = document.getElementById('submit-bundle-btn');

const toast = document.getElementById('toast');

// --- State Management ---
// These variables store the user's selections as they use the app.
let selectedNamasteTerm = null;
let generatedBundle = null;
let debounceTimer;

// --- LIVE API FUNCTIONS (These talk to your backend) ---

async function performSearch(query) {
    showLoader(true);
    clearResults();
    try {
        const response = await fetch(`${API_BASE_URL}/api/search?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Network response was not ok.');
        const data = await response.json();
        renderResults(data.namaste_ayush_results, data.icd11_biomedical_results);
    } catch (error) {
        console.error('Search failed:', error);
        showToast('Search failed. Could not connect to the server.', 'error');
    } finally {
        showLoader(false);
    }
}

async function performTranslate(namasteCode) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/translate?code=${encodeURIComponent(namasteCode)}`);
        if (!response.ok) throw new Error('Translation failed.');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Translation failed:', error);
        showToast('Could not translate the selected NAMASTE code.', 'error');
        return null;
    }
}

async function submitBundle(bundle) {
    showToast('Submitting record...', 'info');
    try {
        const response = await fetch(`${API_BASE_URL}/api/bundle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${MOCK_ABHA_TOKEN}`
            },
            body: JSON.stringify(bundle)
        });

        if (response.status === 401) throw new Error('Authorization failed. Check token.');
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Server responded with an error.');
        }

        const result = await response.json();
        showToast(result.message, 'success');
        console.log('Submission successful:', result);
    } catch (error) {
        console.error('Submission failed:', error);
        showToast(error.message, 'error');
    }
}

// --- UI Rendering Functions ---

function clearResults() {
    namasteResultsList.innerHTML = '';
    icdResultsList.innerHTML = '';
}

function renderResults(namasteData, biomedicalData) {
    clearResults();

    if (!namasteData || namasteData.length === 0) {
        namasteResultsList.innerHTML = '<li>No results found.</li>';
    } else {
        namasteData.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="code">${item.code}</span> ${item.display}`;
            // This is the action that runs when a user clicks a result.
            li.addEventListener('click', () => onNamasteTermSelect(item));
            namasteResultsList.appendChild(li);
        });
    }

    if (!biomedicalData || biomedicalData.length === 0) {
        icdResultsList.innerHTML = '<li>No results found.</li>';
    } else {
        biomedicalData.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="code">${item.code}</span> ${item.display}`;
            icdResultsList.appendChild(li);
        });
    }
}
async function onNamasteTermSelect(item) {
    clearTimeout(debounceTimer);
    searchInput.value = '';
    clearResults();

    selectedNamasteTerm = item;

    // ❌ REMOVE these two lines (they cause flicker)
    // hideSection(entryCard);
    // hideSection(bundleCard);

    // Get translation
    const translation = await performTranslate(item.code);
    if (!translation) return;

    selectedNamasteTerm.translation = translation;

    selectedEntryContent.innerHTML = `
        <h4>${item.display}</h4>
        <p><strong>NAMASTE Code:</strong> <span class="code-display">${item.code}</span></p>
        <p><strong>ICD-11 TM2 Code:</strong> <span class="code-display">${translation.target_code} (${translation.target_display})</span></p>
    `;

    // ✅ Show Step 2 properly
    showSection(entryCard);
}


// --- Event Listeners (These connect user actions to our functions) ---

// Listen for typing in the search box.
searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = searchInput.value;
    if (query.length > 2) {
        // Debouncing: waits 500ms after user stops typing before calling the API.
        debounceTimer = setTimeout(() => performSearch(query), 500);
    } else {
        clearResults();
    }
});

// Listen for a click on the "Generate FHIR Record" button.
createBundleBtn.addEventListener('click', (event) => {
     event.preventDefault(); 
    if (!selectedNamasteTerm || !selectedNamasteTerm.translation) {
        showToast('Please select a valid NAMASTE term first.', 'error');
        return;
    }
    generatedBundle = createFhirBundle(selectedNamasteTerm);
    fhirBundleOutput.textContent = JSON.stringify(generatedBundle, null, 2);
    showSection(bundleCard);
    bundleCard.scrollIntoView({ behavior: 'smooth' });
    showToast('FHIR record generated.', 'success');
});

// Listen for a click on the "Submit Record Securely" button.
submitBundleBtn.addEventListener('click', (event) => {
    event.preventDefault(); 
    if (!generatedBundle) {
        showToast('Please generate a bundle first.', 'error');
        return;
    }
    submitBundle(generatedBundle);
});

// --- Utility Functions ---

function showLoader(isLoading) { loader.style.display = isLoading ? 'block' : 'none'; }
function showSection(section) { section.style.display = 'block'; setTimeout(() => { section.style.opacity = 1; }, 10); }
function hideSection(section) { section.style.opacity = 0; setTimeout(() => { section.style.display = 'none'; }, 300); }

function showToast(message, type = 'info') {
    toast.className = ''; // reset old classes
    toast.textContent = message;
    toast.classList.add('show', type);

    setTimeout(() => { toast.className = toast.className.replace('show', ''); }, 3000);
}

/** Creates a complete and valid FHIR Bundle based on the user's selection. */
function createFhirBundle(term) {
    const patientId = `patient-${Math.random().toString(36).substr(2, 9)}`;
    const conditionId = `condition-${Math.random().toString(36).substr(2, 9)}`;

    return {
        "resourceType": "Bundle", "type": "transaction",
        "entry": [{
            "fullUrl": `urn:uuid:${patientId}`,
            "resource": { "resourceType": "Patient", "id": patientId, "name": [{ "use": "official", "family": "Kumar", "given": ["Aditya"] }] },
            "request": { "method": "POST", "url": "Patient" }
        }, {
            "fullUrl": `urn:uuid:${conditionId}`,
            "resource": {
                "resourceType": "Condition",
                "clinicalStatus": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active" }] },
                "code": {
                    "text": `Dual diagnosis: ${term.display} and ${term.translation.target_display}`,
                    "coding": [
                        { "system": "http://sih.gov.in/fhir/namaste-codes", "code": term.code, "display": term.display },
                        { "system": term.translation.target_system, "code": term.translation.target_code, "display": term.translation.target_display }
                    ]
                },
                "subject": { "reference": `urn:uuid:${patientId}` }
            },
            "request": { "method": "POST", "url": "Condition" }
        }]
    };
}

