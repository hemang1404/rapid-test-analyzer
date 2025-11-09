(function(){
const raw = sessionStorage.getItem('rta_last_result');
const container = document.getElementById('resultCard');
if(!raw){
container.innerHTML = `
<div class="p-8 text-center">
    <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
    </div>
    <h2 class="text-2xl font-semibold mb-2 text-gray-800">No Result Found</h2>
    <p class="text-gray-600">No analysis result was found. Please analyze a test first.</p>
</div>
`;
return;
}

const data = JSON.parse(raw);

// Normalize fields
const testName = data.test || 'Test';
const testDisplay = testName === 'ph' ? 'pH Strip Analysis' : 
                   testName === 'fob' ? 'Fecal Occult Blood Test' : 
                   testName === 'urinalysis' ? 'Urinalysis Strip Test' : 
                   testName.charAt(0).toUpperCase() + testName.slice(1) + ' Test';
const resultText = data.result || JSON.stringify(data.raw || '');
const diagnosis = data.diagnosis || '';

// Check if this is urinalysis test
const isUrinalysis = testName === 'urinalysis';
const urinalysisResults = isUrinalysis ? (data.raw?.results || {}) : null;

// Generate report ID
const reportId = 'RTA-' + Date.now().toString().slice(-6);
const analysisDate = new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
});

// Determine result status and styling
let resultStatus = 'Normal';
let statusColor = 'text-green-600';
let statusBg = 'bg-green-50';
let statusIcon = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
</svg>`;

if (resultText.toLowerCase().includes('positive') || resultText.toLowerCase().includes('abnormal')) {
    resultStatus = 'Abnormal';
    statusColor = 'text-red-600';
    statusBg = 'bg-red-50';
    statusIcon = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
    </svg>`;
}

container.innerHTML = `
<!-- Medical Report Header -->
<div class="medical-header p-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold mb-1">MEDICAL ANALYSIS REPORT</h1>
            <p class="text-green-100">Rapid Test Analyzer System</p>
        </div>
        <div class="text-right">
            <div class="text-lg font-semibold">Report ID: ${reportId}</div>
            <div class="text-green-100">${analysisDate}</div>
        </div>
    </div>
</div>

<!-- Patient/Test Information -->
<div class="p-6 border-b border-gray-200">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Test Information
            </h3>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between"><span class="text-gray-600">Test Type:</span><span class="font-medium">${testDisplay}</span></div>
                <div class="flex justify-between"><span class="text-gray-600">Method:</span><span class="font-medium">AI Computer Vision Analysis</span></div>
                <div class="flex justify-between"><span class="text-gray-600">Analysis Date:</span><span class="font-medium">${new Date().toLocaleDateString()}</span></div>
            </div>
        </div>
        <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                Analysis Status
            </h3>
            <div class="flex items-center ${statusBg} p-3 rounded-lg">
                <div class="${statusColor} mr-3">${statusIcon}</div>
                <div>
                    <div class="font-semibold ${statusColor}">${resultStatus}</div>
                    <div class="text-xs text-gray-600">Analysis completed successfully</div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Test Results -->
<div class="p-6 border-b border-gray-200">
    <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
        Test Results
    </h3>
    <div class="bg-gray-50 rounded-lg p-4">
        ${isUrinalysis && urinalysisResults && Object.keys(urinalysisResults).length > 0 ? `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-100">
                        <tr>
                            <th scope="col" class="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Test Parameter</th>
                            <th scope="col" class="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Result</th>
                            <th scope="col" class="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Confidence</th>
                            <th scope="col" class="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${Object.entries(urinalysisResults).map(([testCode, testData]) => {
                            const testName = testData.test_name || testCode;
                            const result = testData.result || 'N/A';
                            const confidence = testData.confidence ? (testData.confidence * 100).toFixed(1) + '%' : 'N/A';
                            
                            // Determine if result is abnormal
                            const isAbnormal = ['BLO', 'GLU', 'PRO', 'KET', 'NIT', 'LEU'].includes(testCode) && 
                                             !['Neg', 'NEG', 'negative'].includes(result);
                            
                            const statusColor = isAbnormal ? 'text-red-600 bg-red-50' : 'text-green-600 bg-green-50';
                            const statusText = isAbnormal ? 'Abnormal' : 'Normal';
                            
                            return `
                                <tr class="hover:bg-gray-50 transition-colors">
                                    <td class="py-3 px-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <span class="font-medium text-gray-900">${escapeHtml(testName)}</span>
                                            <span class="ml-2 text-xs text-gray-500">(${escapeHtml(testCode)})</span>
                                        </div>
                                    </td>
                                    <td class="py-3 px-4 whitespace-nowrap">
                                        <span class="text-sm font-semibold text-gray-800">${escapeHtml(result)}</span>
                                    </td>
                                    <td class="py-3 px-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                                <div class="bg-blue-600 h-2 rounded-full" style="width: ${testData.confidence ? (testData.confidence * 100) : 0}%"></div>
                                            </div>
                                            <span class="text-xs text-gray-600">${confidence}</span>
                                        </div>
                                    </td>
                                    <td class="py-3 px-4 whitespace-nowrap">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                                            ${statusText}
                                        </span>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
            <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p class="text-sm text-blue-800">
                    <strong>Total Parameters Analyzed:</strong> ${Object.keys(urinalysisResults).length} | 
                    <strong>Pads Detected:</strong> ${data.raw?.pads_detected || 'N/A'}
                </p>
            </div>
        ` : `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Primary Result</label>
                    <div class="text-lg font-semibold text-gray-800">${escapeHtml(resultText)}</div>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Result Classification</label>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusColor} ${statusBg}">
                        ${resultStatus}
                    </span>
                </div>
            </div>
        `}
    </div>
</div>

<!-- Clinical Interpretation -->
<div class="p-6 border-b border-gray-200">
    <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <svg class="w-6 h-6 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        Clinical Interpretation
    </h3>
    <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
        <p class="text-gray-800 leading-relaxed">${escapeHtml(diagnosis || 'Analysis completed. Please consult with a healthcare professional for clinical interpretation of results.')}</p>
    </div>
    
    ${resultStatus === 'Abnormal' ? `
    <div class="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
        <div class="flex">
            <svg class="w-5 h-5 text-yellow-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <p class="text-sm text-yellow-800"><strong>Important:</strong> Abnormal results detected. Please consult with a healthcare professional for proper medical evaluation.</p>
        </div>
    </div>
    ` : ''}
</div>

<!-- Technical Details -->
<div class="p-6">
    <details class="group">
        <summary class="cursor-pointer text-lg font-semibold text-gray-800 mb-2 flex items-center group-open:mb-4">
            <svg class="w-5 h-5 mr-2 text-gray-600 transform group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
            Technical Analysis Details
        </summary>
        <div class="bg-gray-50 rounded-lg p-4">
            <pre class="text-xs text-gray-600 whitespace-pre-wrap font-mono">${escapeHtml(JSON.stringify(data.raw || {message: 'No additional technical data available'}, null, 2))}</pre>
        </div>
    </details>
</div>

<!-- Footer -->
<div class="bg-gray-50 p-4 text-center text-sm text-gray-600">
    <p><strong>Disclaimer:</strong> This analysis is for informational purposes only. Results should be verified by a qualified healthcare professional. This system is not intended to replace professional medical diagnosis.</p>
    <div class="mt-2 text-xs">
        Generated by Rapid Test Analyzer v1.0 | Report ID: ${reportId} | ${analysisDate}
    </div>
</div>
`;

// Add print functionality
document.getElementById('printReportBtn').addEventListener('click', () => {
    window.print();
});

document.getElementById('newAnalysisBtn').addEventListener('click', ()=>{
    window.location.href = '/';
});

function escapeHtml(s){
    if(!s) return '';
    return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
}
})();