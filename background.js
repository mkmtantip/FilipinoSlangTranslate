chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse){
        // chrome.downloads.download({filename: temp.png , conflictAction: "overwrite", });
        if(request.msg == "capture")
            chrome.downloads.download({url: url, path: ".images/temp.png"})
            chrome.tabs.captureVisibleTab()
            sendResponse({url: fetch(dataUrl)});   
    }
);