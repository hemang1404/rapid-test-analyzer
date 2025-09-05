// Client-side logic for index.html
(function(){
    // DOM element references
    const previewImg = document.getElementById('previewImg');
    const previewText = document.getElementById('previewText');
    const previewContent = document.getElementById('previewContent');
    const uploadIcon = document.getElementById('uploadIcon');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeIcon = document.getElementById('analyzeIcon');
    const fileInput = document.getElementById('fileInput');
    const analyzeSpinner = document.getElementById('analyzeSpinner');
    const statusMessages = document.getElementById('statusMessages');

    // Placeholder for selectedTest and url
    let selectedTest = null;
    let url = null;

    // Utility functions for better UX
    function showStatus(message, type = 'info') {
        // Use global status container that's always visible
        const globalStatusContainer = document.getElementById('globalStatusMessages');
        const localStatusContainer = document.getElementById('statusMessages');
        
        // Determine which container to use - prefer global if available
        const statusContainer = globalStatusContainer || localStatusContainer;
        
        if (!statusContainer) {
            // Fallback to alert if no containers are available
            alert(message);
            return;
        }
        
        const statusEl = document.createElement('div');
        statusEl.className = `p-3 rounded-lg text-sm transition-all duration-300 transform translate-x-full opacity-0 ${
            type === 'success' ? 'bg-green-500/90 border border-green-400/50 text-white' :
            type === 'error' ? 'bg-red-500/90 border border-red-400/50 text-white' :
            type === 'warning' ? 'bg-yellow-500/90 border border-yellow-400/50 text-white' :
            'bg-blue-500/90 border border-blue-400/50 text-white'
        } backdrop-blur-sm shadow-lg`;
        statusEl.textContent = message;
        
        statusContainer.appendChild(statusEl);
        
        // Animate in
        setTimeout(() => {
            statusEl.classList.remove('translate-x-full', 'opacity-0');
            statusEl.classList.add('translate-x-0', 'opacity-100');
        }, 10);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            statusEl.classList.add('translate-x-full', 'opacity-0');
            statusEl.classList.remove('translate-x-0', 'opacity-100');
            setTimeout(() => statusEl.remove(), 300);
        }, 5000);
    }

    function animateModal(show = true) {
        const modal = document.getElementById('testModal');
        const modalContent = document.getElementById('testModalContent');
        
        if (show) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            // Trigger animation
            setTimeout(() => {
                modalContent.classList.remove('scale-95', 'opacity-0');
                modalContent.classList.add('scale-100', 'opacity-100');
            }, 10);
        } else {
            modalContent.classList.add('scale-95', 'opacity-0');
            modalContent.classList.remove('scale-100', 'opacity-100');
            setTimeout(() => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }, 300);
        }
    }

    // Hamburger menu functionality
    document.getElementById('hamburgerBtn').addEventListener('click', function() {
        const menu = document.getElementById('hamburgerMenu');
        menu.classList.toggle('hidden');
    });

    // Login button - show under development popup (simplified and more robust)
    function setupLoginButton() {
        const loginBtn = document.querySelector('[data-feature="login"]');
        if (loginBtn) {
            // Remove any existing listeners first to prevent duplicates
            loginBtn.removeEventListener('click', handleLoginClick);
            loginBtn.addEventListener('click', handleLoginClick);
        }
    }
    
    function handleLoginClick(e) {
        e.preventDefault();
        e.stopPropagation();
        showStatus('🚧 Login feature is under development and will be available in a future update.', 'warning');
        // Also close the hamburger menu
        const hamburgerMenu = document.getElementById('hamburgerMenu');
        if (hamburgerMenu) {
            hamburgerMenu.classList.add('hidden');
        }
    }
    
    // Try multiple approaches to ensure the login button works
    setupLoginButton(); // Try immediately
    setTimeout(setupLoginButton, 100); // Try after 100ms
    document.addEventListener('DOMContentLoaded', setupLoginButton); // Try when DOM is ready
    
    // Event delegation as a failsafe - this will work even if other methods fail
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-feature="login"]') || e.target.closest('[data-feature="login"]')) {
            handleLoginClick(e);
        }
    });

    // Close hamburger menu when clicking outside
    document.addEventListener('click', function(event) {
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        const hamburgerMenu = document.getElementById('hamburgerMenu');
        
        if (!hamburgerBtn.contains(event.target) && !hamburgerMenu.contains(event.target)) {
            hamburgerMenu.classList.add('hidden');
        }
    });

    // Show test modal when Start Diagnosis is clicked
    document.getElementById('startBtn').addEventListener('click', function() {
        animateModal(true);
    });

    // Close test modal
    document.getElementById('closeTestModal').addEventListener('click', function() {
        animateModal(false);
    });

    // Close modal when clicking outside
    document.getElementById('testModal').addEventListener('click', function(e) {
        if (e.target === this) {
            animateModal(false);
        }
    });

    // Change test button - show modal and hide upload section
    document.getElementById('changeTestBtn').addEventListener('click', function() {
        animateModal(true);
        document.getElementById('uploadSection').classList.add('hidden');
        document.getElementById('landingSection').classList.remove('hidden'); // Show landing section again
        selectedTest = null;
        resetFileInput();
        showStatus('Select a different test type to continue', 'info');
    });

    function resetFileInput() {
        fileInput.value = '';
        previewImg.classList.add('hidden');
        previewContent.style.display = '';
        previewText.textContent = 'Click here to select an image';
        analyzeBtn.disabled = true;
        analyzeIcon.style.display = '';
        if (url) {
            URL.revokeObjectURL(url);
            url = null;
        }
    }

    // Set selectedTest when a test button is clicked
    document.querySelectorAll('[data-test]').forEach(btn => {
        btn.addEventListener('click', function() {
            const testType = btn.getAttribute('data-test');
            
            // Check if urinalysis - show under development popup
            if (testType === 'urinalysis') {
                showStatus('🚧 Urinalysis feature is coming soon! We\'re working hard to bring you this capability.', 'warning');
                return;
            }
            
            selectedTest = testType;
            document.getElementById('uploadSection').classList.remove('hidden');
            document.getElementById('landingSection').classList.add('hidden'); // Hide landing section
            animateModal(false);
            
            // Update title with more descriptive text
            const testDisplayNames = {
                'ph': 'pH Strip Analysis',
                'fob': 'Fecal Occult Blood Test'
            };
            document.getElementById('chosenTestTitle').textContent = testDisplayNames[testType] || btn.textContent;
            
            showStatus(`✅ ${testDisplayNames[testType] || btn.textContent} selected. Now upload an image to analyze.`, 'success');
            
            // Auto-focus on the preview box for better UX
            setTimeout(() => {
                document.getElementById('previewBox').focus();
            }, 500);
        });
    });

    // Set url and preview image when file is selected
    document.getElementById('selectImageBtn').addEventListener('click', function() {
        fileInput.click();
    });

    // Make preview box clickable to select image
    document.getElementById('previewBox').addEventListener('click', function() {
        fileInput.click();
    });

    // Drag and drop functionality for preview box
    const previewBox = document.getElementById('previewBox');
    
    previewBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        previewBox.classList.add('border-blue-400', 'bg-blue-500/10');
        previewBox.classList.remove('border-white/10');
    });

    previewBox.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        previewBox.classList.remove('border-blue-400', 'bg-blue-500/10');
        previewBox.classList.add('border-white/10');
    });

    previewBox.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        previewBox.classList.remove('border-blue-400', 'bg-blue-500/10');
        previewBox.classList.add('border-white/10');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            // Check if it's an image file
            if (file.type.startsWith('image/')) {
                // Simulate file input change
                const dt = new DataTransfer();
                dt.items.add(file);
                fileInput.files = dt.files;
                
                // Trigger the change event
                const changeEvent = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(changeEvent);
            } else {
                alert('Please drop an image file (PNG, JPG, JPEG, GIF, BMP)');
                showStatus('❌ Please drop a valid image file', 'error');
            }
        }
    });

    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if(file) {
            // Validate file type with better error messaging
            const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/bmp'];
            if (!allowedTypes.includes(file.type.toLowerCase())) {
                showStatus(`❌ Invalid file type: ${file.type}. Please select a valid image file (PNG, JPG, JPEG, GIF, BMP)`, 'error');
                fileInput.value = '';
                return;
            }
            
            // Check file size (max 10MB) with size display
            const maxSize = 10 * 1024 * 1024;
            if (file.size > maxSize) {
                const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
                showStatus(`❌ File too large: ${fileSizeMB}MB. Maximum size is 10MB`, 'error');
                fileInput.value = '';
                return;
            }
            
            // Show loading state
            previewContent.style.display = 'none';
            const loadingDiv = document.createElement('div');
            loadingDiv.id = 'imageLoading';
            loadingDiv.className = 'flex flex-col items-center justify-center';
            loadingDiv.innerHTML = `
                <svg class="animate-spin h-8 w-8 text-white/60 mb-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <span class="text-sm text-white/60">Loading image...</span>
            `;
            document.getElementById('previewBox').appendChild(loadingDiv);
            
            url = URL.createObjectURL(file);
            previewImg.src = url;
            previewImg.onload = ()=> {
                URL.revokeObjectURL(url);
                document.getElementById('imageLoading')?.remove();
                previewImg.classList.remove('hidden');
                analyzeBtn.disabled = false;
                showStatus(`✅ Image loaded successfully! Ready to analyze your ${selectedTest?.toUpperCase()} test.`, 'success');
            };
            previewImg.onerror = ()=> {
                document.getElementById('imageLoading')?.remove();
                previewContent.style.display = '';
                showStatus('❌ Error loading image. Please try a different file.', 'error');
                fileInput.value = '';
            };
        } else {
            resetFileInput();
        }
    });

    // Analyze: send to backend and navigate to result page
    analyzeBtn.addEventListener('click', async ()=>{
        if(!selectedTest){ 
            showStatus('❌ Please select a test type first', 'error'); 
            return; 
        }
        const file = fileInput.files[0];
        if(!file){ 
            showStatus('❌ Please select an image to analyze', 'error'); 
            return; 
        }

        // Show loading state with enhanced feedback
        analyzeBtn.disabled = true;
        analyzeSpinner.classList.remove('hidden');
        analyzeIcon.style.display = 'none';
        showStatus('🔄 Analyzing your image... This may take a few moments.', 'info');
        
        // Add progress indicator
        let progressMessages = [
            'Processing image...',
            'Running AI analysis...',
            'Generating results...'
        ];
        let progressIndex = 0;
        const progressInterval = setInterval(() => {
            if (progressIndex < progressMessages.length) {
                showStatus(`🔄 ${progressMessages[progressIndex]}`, 'info');
                progressIndex++;
            }
        }, 2000);

        const form = new FormData();
        form.append('image', file);
        form.append('test_type', selectedTest);

        // default endpoint — change this if your backend is hosted elsewhere
        const ENDPOINT = 'http://127.0.0.1:5000/analyze';

        try{
            clearInterval(progressInterval); // Clear progress messages
            const resp = await fetch(ENDPOINT, { 
                method: 'POST', 
                body: form,
                // Add timeout handling
                signal: AbortSignal.timeout(30000) // 30 second timeout
            });
            
            if(!resp.ok) {
                const errorText = await resp.text();
                throw new Error(`Server error (${resp.status}): ${errorText || 'Unknown error'}`);
            }
            
            const data = await resp.json();

            // Check if the response indicates success
            if (!data.success && data.error) {
                throw new Error(data.error);
            }

            showStatus('✅ Analysis completed successfully! Redirecting to results...', 'success');

            // Map backend response to frontend format
            const resultObj = {
                test: selectedTest,
                raw: data,
                result: data.result || data.message || JSON.stringify(data),
                diagnosis: data.diagnosis || data.interpretation || 'Analysis completed successfully.'
            };

            sessionStorage.setItem('rta_last_result', JSON.stringify(resultObj));
            
            // Small delay for user to see success message
            setTimeout(() => {
                window.location.href = 'result.html';
            }, 1000);

        }catch(err){
            clearInterval(progressInterval); // Clear any remaining progress messages
            console.error('Analysis failed:', err);
            
            // Enhanced error handling with specific error types
            let errorMessage = '❌ Analysis failed. ';
            
            if (err.name === 'AbortError' || err.message.includes('timeout')) {
                errorMessage += 'Request timed out. Please check your connection and try again.';
            } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                errorMessage += 'Network error. Please check your internet connection.';
            } else if (err.message.includes('Server error')) {
                errorMessage += err.message;
            } else {
                errorMessage += err.message || 'Unknown error occurred.';
            }
            
            showStatus(errorMessage, 'error');
            
            // Only show demo result if it's a network/connection error (not a server error)
            if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                showStatus('⚠️ Backend unreachable. Showing demo result for testing.', 'warning');
                
                // fallback: simulate a result so the flow can be tested without backend
                const fallback = {
                    test: selectedTest,
                    raw: null,
                    result: 'Simulated result (backend unreachable)',
                    diagnosis: 'No backend response — this is a demo result.'
                };
                sessionStorage.setItem('rta_last_result', JSON.stringify(fallback));
                
                setTimeout(() => {
                    window.location.href = 'result.html';
                }, 1000);
            }
        } finally{
            clearInterval(progressInterval); // Clear any remaining progress interval
            analyzeSpinner.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeIcon.style.display = '';
        }    });

    // Keyboard accessibility and shortcuts
    document.addEventListener('keydown', function(e) {
        // ESC to close modal
        if (e.key === 'Escape') {
            const modal = document.getElementById('testModal');
            if (!modal.classList.contains('hidden')) {
                animateModal(false);
            }
        }
        
        // Enter to trigger analyze when ready
        if (e.key === 'Enter' && !analyzeBtn.disabled && selectedTest && fileInput.files[0]) {
            analyzeBtn.click();
        }
        
        // Space or Enter to open file dialog when preview box is focused
        if ((e.key === ' ' || e.key === 'Enter') && e.target.id === 'previewBox') {
            e.preventDefault();
            fileInput.click();
        }
        
        // Ctrl/Cmd + O to open file dialog
        if ((e.ctrlKey || e.metaKey) && e.key === 'o' && selectedTest) {
            e.preventDefault();
            fileInput.click();
        }
        
        // Ctrl/Cmd + Enter to analyze (if ready)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !analyzeBtn.disabled && selectedTest && fileInput.files[0]) {
            e.preventDefault();
            analyzeBtn.click();
        }
    });

    // Add focus styles and accessibility
    document.getElementById('previewBox').setAttribute('tabindex', '0');
    document.getElementById('previewBox').setAttribute('role', 'button');
    document.getElementById('previewBox').setAttribute('aria-label', 'Click to select an image file');

})();