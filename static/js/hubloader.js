async function getHubLiveChannels(url) {
    const response = await fetch(url);
    var data = await response.json();
    if (response) {
        return data['results']
    }
}

function updateLiveChannels(data) {
    var ul = document.getElementById("liveChannelsList");
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

        if (channelDescription === null || channelDescription === "") {
            channelDescription = "No Description Provided...";
        }

        var li = document.createElement("li");
        li.setAttribute("id", "channel-" + channelUUID);
        li.setAttribute("class", "mx-2");
        li.innerHTML = '\
            <a href="' + linkURL + '">\
                <div class="zoom">\
                    <img class="streamcard-img boxShadow gif" src="' + linkImageURL + '">\
                    <div class="streamcard-metadata boxShadow">\
                        <div class="row">\
                            <div class="col-auto">\
                                <img src="' + streamerPicture + '"onerror="this.src=\'img/user2.png\'" class="streamcard-user-img rounded-circle boxShadow"> \
                            </div> \
                            <div class="col-6">\
                            <b>' + channelName + '</b><br>\
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

const hubURL = "http://hubapi.internal.divby0.net/api/channel/live";

document.addEventListener("DOMContentLoaded", function(){
    getHubLiveChannels(hubURL)
    .then((data) => updateLiveChannels(data)) 
});