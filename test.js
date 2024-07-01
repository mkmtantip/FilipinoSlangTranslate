// Load Tesseract.js from a CDN
const tesseractScript = document.createElement('script');
tesseractScript.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@2.1.5/dist/tesseract.min.js';
document.head.appendChild(tesseractScript);

// Function to process the image with Tesseract.js
function processImage(imageUrl) {
  tesseractScript.onload = () => {
    Tesseract.recognize(
      imageUrl,
      'eng',
      {
        logger: (m) => console.log(m)
      }
    ).then(({ data: { text } }) => {
      console.log('Recognized text:', text);
      alert('Recognized text: ' + text);
    });
  };
}

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'processImage') {
    processImage(request.imageUrl);
    sendResponse({ status: 'processing' });
  }
});
