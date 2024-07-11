document.getElementById('plezwork').addEventListener('click', async () => {
  try {
    // Capture the visible tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' }, async (dataUrl) => {
      // Convert dataUrl to a Blob
      const response = await fetch(dataUrl);
      const blob = await response.blob();
      
      // Create a temporary URL for the blob
      const url = URL.createObjectURL(blob);
      
      // Create an anchor element and trigger a download
      const a = document.createElement('a');
      a.href = url;
      a.download = 'temp.png';
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
    });
  } catch (error) {
    console.error('Error taking screenshot:', error);
  } 
});
