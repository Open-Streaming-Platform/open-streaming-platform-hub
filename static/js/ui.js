var nsfwToggle = false;

var lazyLoadInstance = new LazyLoad({
    elements_selector: ".lazy"
});

// Stream Card png to gif Handler
$(document).ready(function(){
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
});

// NSFW Toggle Handler
document.getElementById('nsfwToggle').addEventListener('change', function (evt) {
    nsfwToggle = !nsfwToggle
    var divsToHide = document.getElementsByClassName("nsfw");
    for(var i = 0; i < divsToHide.length; i++){
        if (nsfwToggle === true) {
            divsToHide[i].style.display = "block";
        } else {
            divsToHide[i].style.display = "none";
        };
    }
    console.log("NSFW Toggle: " + nsfwToggle)
});