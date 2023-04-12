async function getHubLiveChannels(url) {
    const response = await fetch(url);
    var data = await response.json();
    if (response) {
        return data['results']
    }
}

function updateLiveChannels(data) {
    var ul = document.getElementById("liveChannelsList");
    
    // Verify Length of Returned Data
    if (data.length > 0) {
        data.sort((a, b) => (a.channelViewers < b.channelViewers) ? 1 : -1) // Sort by # of Viewers
    }

    // Iterate and Create Hub Stream Cards
    for (let i = 0; i < data.length; i++) {
        streamData = data[i];
        var channelUUID = streamData['channelLocation'];
        var serverURI = streamData['serverProtocol'] + "://" + streamData['serverAddres'];
        var linkURL = serverURI + "/view/" + channelUUID;
        var linkImageURL = serverURI + "/stream-thumb/" + channelUUID + ".png";
        var channelName =  streamData['channelName'];
        var streamerUsername = streamData['channelOwnerUsername'];
        var streamerPicture = serverURI + "/images/" + streamData['channelOwnerPicture'];
        var channelDescription = streamData['channelDescription'];
        var channelViewers = streamData['channelViewers']
        var channelNSFW = streamData['channelNSFW']

        if (channelDescription === null || channelDescription === "") {
            channelDescription = "No Description Provided...";
        }

        var li = document.createElement("li");
        li.setAttribute("id", "channel-" + channelUUID);
        
        // Set NSFW Class if Channel is identified as NSFW
        if (channelNSFW === true){
            li.setAttribute("class", "mx-2 nsfw")
        } else (
            li.setAttribute("class", "mx-2")
        );
        
        li.innerHTML = '\
            <a href="' + linkURL + '">\
                <div class="zoom">\
                    <div class="streamcard-thumbBox">\
                        <div class="streamcard-badges">\
                            <span class="live-badge boxShadow textShadow"><b>Live</b></span>\
                            <span class="live-viewers-badge boxShadow textShadow ms-1"><i class="bi bi-eye-fill pe-1"></i> <b class="justify-content-end">' + channelViewers + '</b></span>\
                        </div>\
                        <img class="streamcard-img boxShadow gif lazy" src="/static/img/video-placeholder.jpg" data-src="' + linkImageURL + '">\
                    </div>\
                    <div class="streamcard-metadata boxShadow">\
                        <div class="row">\
                            <div class="col-auto">\
                                <img src="' + streamerPicture + '"onerror="this.src=\'/static/img/user2.png\'" class="streamcard-user-img rounded-circle boxShadow lazy"> \
                            </div> \
                            <div class="col-6">\
                            <b class="textShadow">' + channelName + '</b><br>\
                            ' + streamerUsername + '<br>\
                            </div>\
                        </div> \
                        <div class="row">\
                            <div class="col-12 streamcard-metadata-description">\
                                <small>' + channelDescription + '</small>\
                            </div>\
                    </div>\
                </div>\
            </a>';
        ul.appendChild(li);
    }
    enableGifHover();
    $('#liveChannelsLoader').hide();
    $('#liveChannelsList').show();
}

function enableGifHover() {
    $(".gif").hover
    (
        function(){
            var src = $(this).attr("src");
            $(this).attr("src", src.replace(/\.png$/i, ".gif"));
        },
        function(){
            var src = $(this).attr("src");
            $(this).attr("src", src.replace(/\.gif$/i, ".png"));
        }
    );
}

const hubURL = "/api/channel/live";
//hubURL = "https://hub.openstreamingplatform.com/api/channel/live"

document.addEventListener("DOMContentLoaded", function(){
    getHubLiveChannels(hubURL)
    .then((data) => updateLiveChannels(data)) 
});