// DOM Elements
const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("file-input");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const croppedImg = document.getElementById("cropped-img");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");
const loading = document.getElementById("loading");
const cropInstructions = document.getElementById("crop-instructions");
const cropBtn = document.getElementById("crop-btn");
const resetBtn = document.getElementById("reset-btn");
const submitBtn = document.getElementById("submit-btn");
const newImageBtn = document.getElementById("new-image-btn");
const resultsSection = document.getElementById("results-section");
const resultsContent = document.getElementById("results-content");

// Global Variables
let uploadedImageFile = null;
let image = new Image();
let cropping = false;
let startX, startY, currentX, currentY;
let scale = 1; // For canvas scaling

// Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

// Utility Functions
function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  successMessage.style.display = 'none';
  setTimeout(() => {
    errorMessage.style.display = 'none';
  }, 5000);
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.style.display = 'block';
  errorMessage.style.display = 'none';
  setTimeout(() => {
    successMessage.style.display = 'none';
  }, 7000); // Increased from 3 to 7 seconds
}

function showResults(data) {
  let resultClass = '';
  let resultTitle = '';
  let resultDetails = '';

  if (data.type === 'fob') {
    const result = data.result.toLowerCase();
    if (result.includes('positive')) {
      resultClass = 'result-fob-positive';
      resultTitle = '🔴 FOB Test: POSITIVE';
    } else if (result.includes('negative')) {
      resultClass = 'result-fob-negative';
      resultTitle = '🟢 FOB Test: NEGATIVE';
    } else {
      resultClass = 'result-fob-invalid';
      resultTitle = '⚠️ FOB Test: INVALID';
    }
    resultDetails = `<strong>Result:</strong> ${data.result}<br><strong>Status:</strong> Test completed successfully`;
  } else if (data.type === 'ph') {
    resultClass = 'result-ph';
    resultTitle = '🔵 pH Test Results';
    resultDetails = `<strong>Estimated pH:</strong> ${data.estimated_ph}<br><strong>Status:</strong> Analysis completed`;
  }

  resultsContent.innerHTML = `
    <div class="result-item ${resultClass}">
      <div class="result-title">${resultTitle}</div>
      <div class="result-details">${resultDetails}</div>
    </div>
  `;
  
  resultsSection.style.display = 'block';
  
  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
  
  // Update success message to mention reset option
  showSuccess("Analysis completed! Use the reset button below to start a new test.");
}

function clearResults() {
  resultsSection.style.display = 'none';
  resultsContent.innerHTML = '';
}

function resetForNewTest() {
  try {
    // Clear all image data
    image.src = "";
    uploadedImageFile = null;
    canvas.style.display = "none";
    croppedImg.style.display = "none";
    cropInstructions.style.display = "none";
    
    // Clear canvas
    if (canvas.width && canvas.height) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    // Reset crop coordinates
    startX = startY = currentX = currentY = undefined;
    
    // Reset file input
    fileInput.value = "";
    
    // Clear results
    clearResults();
    
    // Hide any success/error messages
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Update button states
    updateButtonStates();
    
    // Show success message for reset
    showSuccess("Ready for new test! Please upload an image.");
    
    // Scroll back to upload area
    uploadArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
  } catch (error) {
    showError("Error resetting. Please refresh the page if issues persist.");
  }
}

function showLoading(show = true) {
  loading.style.display = show ? 'block' : 'none';
}

function updateButtonStates() {
  const hasImage = image.src && canvas.style.display === 'block';
  const hasCrop = croppedImg.style.display === 'block';
  
  cropBtn.disabled = !hasImage;
  resetBtn.disabled = !hasImage;
  newImageBtn.disabled = !hasImage;
  submitBtn.disabled = !hasCrop;
}

function validateFile(file) {
  if (!file) {
    showError("Please select a valid file.");
    return false;
  }
  
  if (!ALLOWED_TYPES.includes(file.type)) {
    showError("Please upload a JPEG or PNG image file.");
    return false;
  }
  
  if (file.size > MAX_FILE_SIZE) {
    showError("File size must be less than 5MB.");
    return false;
  }
  
  return true;
}

function calculateScale() {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return { x: scaleX, y: scaleY };
}

// Image Handling
function handleImage(file) {
  if (!validateFile(file)) return;
  
  showLoading(true);
  uploadedImageFile = file;
  
  const reader = new FileReader();
  reader.onerror = () => {
    showLoading(false);
    showError("Error reading file. Please try again.");
  };
  
  reader.onload = (e) => {
    image.onerror = () => {
      showLoading(false);
      showError("Error loading image. Please try a different file.");
    };
    
    image.onload = () => {
      try {
        // Limit canvas size for performance
        const maxWidth = 1200;
        const maxHeight = 800;
        let { width, height } = image;
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width *= ratio;
          height *= ratio;
        }
        
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(image, 0, 0, width, height);
        canvas.style.display = "block";
        croppedImg.style.display = "none";
        cropInstructions.style.display = "block";
        
        updateButtonStates();
        showLoading(false);
        showSuccess("Image uploaded successfully! Click and drag to crop.");
      } catch (error) {
        showLoading(false);
        showError("Error processing image. Please try again.");
      }
    };
    image.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// Crop Functions
function cropImage() {
  if (!startX && startX !== 0) {
    showError("Please select an area to crop first.");
    return;
  }
  
  try {
    const x = Math.min(startX, currentX);
    const y = Math.min(startY, currentY);
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    
    if (width < 10 || height < 10) {
      showError("Please select a larger area to crop.");
      return;
    }
    
    const croppedCanvas = document.createElement("canvas");
    croppedCanvas.width = width;
    croppedCanvas.height = height;
    const croppedCtx = croppedCanvas.getContext("2d");
    croppedCtx.drawImage(canvas, x, y, width, height, 0, 0, width, height);
    
    croppedImg.src = croppedCanvas.toDataURL("image/png", 0.9);
    croppedImg.style.display = "block";
    cropInstructions.style.display = "none";
    
    updateButtonStates();
    showSuccess("Image cropped successfully!");
  } catch (error) {
    showError("Error cropping image. Please try again.");
  }
}

function resetCrop() {
  if (image.src) {
    try {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      croppedImg.style.display = "none";
      cropInstructions.style.display = "block";
      
      // Reset crop coordinates
      startX = startY = currentX = currentY = undefined;
      
      updateButtonStates();
      showSuccess("Crop reset successfully!");
    } catch (error) {
      showError("Error resetting crop. Please try again.");
    }
  }
}

function selectNewImage() {
  try {
    // Clear all image data
    image.src = "";
    uploadedImageFile = null;
    canvas.style.display = "none";
    croppedImg.style.display = "none";
    cropInstructions.style.display = "none";
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Reset crop coordinates
    startX = startY = currentX = currentY = undefined;
    
    // Reset file input
    fileInput.value = "";
    
    // Clear previous results
    clearResults();
    
    // Update button states
    updateButtonStates();
    
    // Trigger file selection
    fileInput.click();
    
    showSuccess("Select a new image to upload.");
  } catch (error) {
    showError("Error clearing current image. Please refresh the page.");
  }
}

// Submit Function
function submitImage() {
  if (!croppedImg.src || croppedImg.style.display === 'none') {
    showError("Please crop an area first before analyzing.");
    return;
  }

  try {
    showLoading(true);

    const blob = dataURLToBlob(croppedImg.src);
    const formData = new FormData();
    formData.append("image", blob, "cropped.png");
    formData.append("test_type", document.getElementById("test-type").value);

    fetch('/analyze', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        showError(data.error);
        clearResults(); // Clear any previous results on error
      } else {
        showResults(data); // Show persistent results (includes success message)
      }
    })
    .catch(error => {
      console.error(error);
      showError("Analysis failed. Please try again.");
      clearResults(); // Clear any previous results on error
    })
    .finally(() => {
      showLoading(false);
    });

  } catch (error) {
    showLoading(false);
    showError("Error submitting image. Please try again.");
  }
}

// Utility Function
function dataURLToBlob(dataurl) {
  try {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    const n = bstr.length;
    const u8arr = new Uint8Array(n);
    
    for (let i = 0; i < n; i++) {
      u8arr[i] = bstr.charCodeAt(i);
    }
    
    return new Blob([u8arr], { type: mime });
  } catch (error) {
    showError("Error processing image data.");
    return null;
  }
}

// Event Listeners
uploadArea.addEventListener("click", () => fileInput.click());

uploadArea.addEventListener("keydown", (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});

uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
  handleImage(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", () => handleImage(fileInput.files[0]));

// Canvas Mouse Events
canvas.addEventListener("mousedown", (e) => {
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const scaleData = calculateScale();
  startX = (e.clientX - rect.left) * scaleData.x;
  startY = (e.clientY - rect.top) * scaleData.y;
  cropping = true;
  canvas.style.cursor = 'crosshair';
});

canvas.addEventListener("mousemove", (e) => {
  if (!cropping) return;
  e.preventDefault();
  
  const rect = canvas.getBoundingClientRect();
  const scaleData = calculateScale();
  currentX = (e.clientX - rect.left) * scaleData.x;
  currentY = (e.clientY - rect.top) * scaleData.y;

  // Redraw image and selection rectangle
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
  
  // Draw selection rectangle
  ctx.strokeStyle = "#e53e3e";
  ctx.lineWidth = 3;
  ctx.setLineDash([8, 4]);
  ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
});

canvas.addEventListener("mouseup", (e) => {
  e.preventDefault();
  cropping = false;
  canvas.style.cursor = 'default';
});

// Touch Events for Mobile
canvas.addEventListener("touchstart", (e) => {
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const scaleData = calculateScale();
  const touch = e.touches[0];
  startX = (touch.clientX - rect.left) * scaleData.x;
  startY = (touch.clientY - rect.top) * scaleData.y;
  cropping = true;
});

canvas.addEventListener("touchmove", (e) => {
  if (!cropping) return;
  e.preventDefault();
  
  const rect = canvas.getBoundingClientRect();
  const scaleData = calculateScale();
  const touch = e.touches[0];
  currentX = (touch.clientX - rect.left) * scaleData.x;
  currentY = (touch.clientY - rect.top) * scaleData.y;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#e53e3e";
  ctx.lineWidth = 3;
  ctx.setLineDash([8, 4]);
  ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
});

canvas.addEventListener("touchend", (e) => {
  e.preventDefault();
  cropping = false;
});

// Initialize
window.addEventListener('load', () => {
  updateButtonStates();
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch(e.key) {
      case 'o':
        e.preventDefault();
        fileInput.click();
        break;
      case 'n':
        if (!newImageBtn.disabled) {
          e.preventDefault();
          selectNewImage();
        }
        break;
      case 'r':
        if (!resetBtn.disabled) {
          e.preventDefault();
          resetCrop();
        } else if (resultsSection.style.display === 'block') {
          e.preventDefault();
          resetForNewTest();
        }
        break;
      case 'c':
        if (!cropBtn.disabled) {
          e.preventDefault();
          cropImage();
        }
        break;
    }
  }
  
  // ESC key to clear results
  if (e.key === 'Escape' && resultsSection.style.display === 'block') {
    e.preventDefault();
    clearResults();
  }
});
