$(document).ready(function(){
    $("#chat-launcher").click(function(){
        $("#chat-container").fadeIn();
        $(this).fadeOut();
    });

    $("#chat-toggle").click(function(){
        $("#chat-container").fadeOut();
        $("#chat-launcher").fadeIn();
    });

    $("#chat-form").on("submit", function(e){
        e.preventDefault();
        var message = $("#message").val();
        if(message.trim() === "") return;
        $("#chatbox").append("<p><strong>Ty:</strong> " + message + "</p>");
        $("#message").val("");
        $.post("/ask", { message: message }, function(data){
            $("#chatbox").append("<p><strong>BiznesBot:</strong> " + data.response + "</p>");
            $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
        });
    });
});
