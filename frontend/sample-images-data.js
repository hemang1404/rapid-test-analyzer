// Sample images data structure
const sampleImages = {
    ph: [
        {
            name: "pH Strip - Acidic (pH 4.0)",
            filename: "ph-acidic-sample.jpg",
            description: "Sample pH strip showing acidic reading around pH 4.0",
            url: "sample-images/ph/ph-acidic-sample.jpg"
        },
        {
            name: "pH Strip - Neutral (pH 7.0)",
            filename: "ph-neutral-sample.jpg", 
            description: "Sample pH strip showing neutral reading around pH 7.0",
            url: "sample-images/ph/ph-neutral-sample.jpg"
        },
        {
            name: "pH Strip - Basic (pH 9.0)",
            filename: "ph-basic-sample.jpg",
            description: "Sample pH strip showing basic reading around pH 9.0",
            url: "sample-images/ph/ph-basic-sample.jpg"
        }
    ],
    fob: [
        {
            name: "FOB Test - Negative",
            filename: "fob-negative-sample.jpg",
            description: "Sample FOB test showing negative result",
            url: "sample-images/fob/fob-negative-sample.jpg"
        },
        {
            name: "FOB Test - Positive",
            filename: "fob-positive-sample.jpg",
            description: "Sample FOB test showing positive result",
            url: "sample-images/fob/fob-positive-sample.jpg"
        },
        {
            name: "FOB Test - Borderline",
            filename: "fob-borderline-sample.jpg",
            description: "Sample FOB test showing borderline result",
            url: "sample-images/fob/fob-borderline-sample.jpg"
        }
    ]
};

// Export for use in analyze.js
window.sampleImages = sampleImages;
