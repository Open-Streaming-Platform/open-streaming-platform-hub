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