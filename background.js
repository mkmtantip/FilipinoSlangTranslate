chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse){
        // chrome.downloads.download({filename: temp.png , conflictAction: "overwrite", });
        if(request.msg == "capture")
            sendResponse({url: fetch(dataUrl)});   
    }
);