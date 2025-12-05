// Client-side logic for index.html
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - JavaScript initializing...');
    
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
    
    console.log('Elements found:', {
        selectImageBtn: !!document.getElementById('selectImageBtn'),
        sampleImagesBtn: !!document.getElementById('sampleImagesBtn'),
        fileInput: !!fileInput
    });

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
        
        // Hide sample images button  
        document.getElementById('sampleImagesBtn').style.display = 'none';
        
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
            
            selectedTest = testType;
            document.getElementById('uploadSection').classList.remove('hidden');
            document.getElementById('landingSection').classList.add('hidden'); // Hide landing section
            
            // Show sample images button
            document.getElementById('sampleImagesBtn').style.display = 'flex';
            
            animateModal(false);
            
            // Update title with more descriptive text
            const testDisplayNames = {
                'ph': 'pH Strip Analysis',
                'fob': 'Fecal Occult Blood Test',
                'urinalysis': 'Urinalysis Strip Test'
            };
            document.getElementById('chosenTestTitle').textContent = testDisplayNames[testType] || btn.textContent;
            
            showStatus(`✅ ${testDisplayNames[testType] || btn.textContent} selected. Now upload an image to analyze.`, 'success');
            
            // Auto-focus on the preview box for better UX
            setTimeout(() => {
                document.getElementById('previewBox').focus();
            }, 500);
        });
    });

    // Sample Images functionality - Modal with static images
    document.getElementById('sampleImagesBtn').addEventListener('click', function() {
        if (!selectedTest) {
            showStatus('❌ Please select a test type first before viewing sample images', 'error');
            return;
        }
        showSampleImagesModal();
    });

    // Close sample images modal
    const closeSampleImagesModal = document.getElementById('closeSampleImagesModal');
    if (closeSampleImagesModal) {
        closeSampleImagesModal.addEventListener('click', function() {
            hideSampleImagesModal();
        });
    }

    // Close modal when clicking outside
    const sampleImagesModal = document.getElementById('sampleImagesModal');
    if (sampleImagesModal) {
        sampleImagesModal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideSampleImagesModal();
            }
        });
    }

    function showSampleImagesModal() {
        console.log('showSampleImagesModal called');
        
        const modal = document.getElementById('sampleImagesModal');
        const modalContent = document.getElementById('sampleImagesModalContent');
        const contentDiv = document.getElementById('sampleImagesContent');
        
        console.log('Modal elements check:', {
            modal: !!modal,
            modalContent: !!modalContent,
            contentDiv: !!contentDiv
        });
        
        if (!modal || !modalContent || !contentDiv) {
            console.error('Sample images modal elements not found');
            console.log('Available elements with sample in id:', 
                Array.from(document.querySelectorAll('[id*="sample"]')).map(el => el.id)
            );
            showStatus('❌ Sample images feature not available', 'error');
            return;
        }
        
        // Check if config is loaded
        console.log('Sample images config:', window.sampleImagesConfig);
        
        // Get sample images for the selected test
        const config = window.sampleImagesConfig || {};
        const images = config[selectedTest] || [];
        
        console.log(`Found ${images.length} images for ${selectedTest} test`);
        
        if (images.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold mb-2">No Sample Images Available</h3>
                    <p class="text-white/70">Sample images for ${selectedTest.toUpperCase()} tests are coming soon!</p>
                </div>
            `;
        } else {
            const testName = selectedTest === 'ph' ? 'pH Strip' : selectedTest === 'fob' ? 'FOB Test' : selectedTest.toUpperCase();
            contentDiv.innerHTML = `
                <div class="mb-6">
                    <h4 class="text-xl font-semibold mb-4 text-center">${testName} Sample Images</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${images.map((image, index) => `
                            <div class="sample-image-card glass rounded-lg p-4 hover:bg-white/10 transition-all duration-300 cursor-pointer group" data-image-url="${image.url}" data-image-name="${image.name}" data-is-placeholder="${image.placeholder || false}">
                                <div class="aspect-video bg-white/5 rounded-lg mb-3 flex items-center justify-center border-2 border-dashed border-white/20 group-hover:border-purple-400/50 transition-colors overflow-hidden">
                                    ${image.placeholder ? `
                                        <div class="text-center">
                                            <svg class="w-8 h-8 text-white/40 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                            </svg>
                                            <p class="text-xs text-white/60">Demo Image</p>
                                        </div>
                                    ` : `
                                        <img src="${image.url}" alt="${image.name}" class="w-full h-full object-cover rounded" onload="this.classList.add('loaded')" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                                        <div class="text-center hidden">
                                            <svg class="w-8 h-8 text-white/40 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                            </svg>
                                            <p class="text-xs text-white/60">Loading...</p>
                                        </div>
                                    `}
                                </div>
                                <h5 class="font-semibold text-sm mb-2 group-hover:text-purple-300 transition-colors">${image.name}</h5>
                                <div class="mt-3 text-center">
                                    <span class="inline-block px-3 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full border border-purple-400/30">Click to Use</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            // Add click listeners to sample image cards
            document.querySelectorAll('.sample-image-card').forEach(card => {
                card.addEventListener('click', function() {
                    const imageUrl = this.dataset.imageUrl;
                    const imageName = this.dataset.imageName;
                    const isPlaceholder = this.dataset.isPlaceholder === 'true';
                    
                    if (isPlaceholder) {
                        // Create a demo image
                        createDemoSampleImage(imageName);
                        hideSampleImagesModal();
                        showStatus(`✅ Loaded demo sample: ${imageName}`, 'success');
                    } else {
                        // Try to load the actual image
                        fetch(imageUrl)
                            .then(response => {
                                if (!response.ok) throw new Error('Image not found');
                                return response.blob();
                            })
                            .then(blob => {
                                const file = new File([blob], `sample-${imageName.toLowerCase().replace(/\s+/g, '-')}.jpg`, { type: 'image/jpeg' });
                                loadSampleImageFile(file, imageName);
                                hideSampleImagesModal();
                                showStatus(`✅ Loaded sample image: ${imageName}`, 'success');
                            })
                            .catch(error => {
                                console.log('Sample image not found, creating demo preview');
                                createDemoSampleImage(imageName);
                                hideSampleImagesModal();
                                showStatus(`✅ Loaded demo sample: ${imageName}`, 'success');
                            });
                    }
                });
            });
        }
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        setTimeout(() => {
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
    }

    function hideSampleImagesModal() {
        const modal = document.getElementById('sampleImagesModal');
        const modalContent = document.getElementById('sampleImagesModalContent');
        
        modalContent.classList.add('scale-95', 'opacity-0');
        modalContent.classList.remove('scale-100', 'opacity-100');
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }, 300);
    }

    function loadSampleImageFile(file, imageName) {
        // Update the file input (for backend processing)
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        
        // Update the preview
        const url = URL.createObjectURL(file);
        previewImg.src = url;
        previewImg.classList.remove('hidden');
        previewContent.style.display = 'none';
        analyzeBtn.disabled = false;
        
        // Update preview text for demo
        if (previewText) {
            previewText.textContent = `Sample: ${imageName}`;
        }
    }

    function createDemoSampleImage(imageName) {
        // Create a demo image using canvas
        const canvas = document.createElement('canvas');
        canvas.width = 400;
        canvas.height = 300;
        const ctx = canvas.getContext('2d');
        
        // Create a gradient background based on test type
        const gradient = ctx.createLinearGradient(0, 0, 400, 300);
        if (selectedTest === 'ph') {
            // pH strip colors
            gradient.addColorStop(0, '#FF6B6B');
            gradient.addColorStop(0.5, '#4ECDC4');
            gradient.addColorStop(1, '#45B7D1');
        } else if (selectedTest === 'fob') {
            // FOB test colors
            gradient.addColorStop(0, '#96CEB4');
            gradient.addColorStop(1, '#FFEAA7');
        } else {
            gradient.addColorStop(0, '#74b9ff');
            gradient.addColorStop(1, '#6c5ce7');
        }
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 400, 300);
        
        // Add border
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 4;
        ctx.strokeRect(0, 0, 400, 300);
        
        // Add text
        ctx.fillStyle = 'white';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 2;
        ctx.fillText('DEMO SAMPLE', 200, 130);
        
        ctx.font = '18px Arial';
        ctx.fillText(imageName, 200, 160);
        
        ctx.font = '14px Arial';
        ctx.fillText('(Generated for Testing)', 200, 190);
        
        // Convert to blob and load
        canvas.toBlob(blob => {
            const file = new File([blob], `demo-${imageName.toLowerCase().replace(/\s+/g, '-')}.png`, { type: 'image/png' });
            loadSampleImageFile(file, imageName);
        });
    }

    // Handle sample file selection (fallback for local file input)
    document.getElementById('sampleFileInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Use the same file handling as the main file input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Trigger the change event to update the preview
            fileInput.dispatchEvent(new Event('change'));
            
            showStatus(`✅ Loaded sample image: ${file.name}`, 'success');
        }
    });

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

        // Use backend URL from config (supports separate frontend/backend deployment)
        const ENDPOINT = window.APP_CONFIG ? window.APP_CONFIG.apiUrl('analyze') : '/analyze';

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
        } finally {
            clearInterval(progressInterval); // Clear any remaining progress interval
            analyzeSpinner.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeIcon.style.display = '';
        }    });

    // Keyboard accessibility and shortcuts
    document.addEventListener('keydown', function(e) {
        // ESC to close modal
        if (e.key === 'Escape') {
            const testModal = document.getElementById('testModal');
            
            if (!testModal.classList.contains('hidden')) {
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
        
        // Ctrl/Cmd + S to open sample images
        if ((e.ctrlKey || e.metaKey) && e.key === 's' && selectedTest) {
            e.preventDefault();
            document.getElementById('sampleFileInput').click();
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

});