$(document).ready(function() {
    $("#chat-form").on("submit", function(e) {
        e.preventDefault();
        var message = $("#message").val().trim();
        if (message === "") return;
        $("#chatbox").append("<p><strong>Ty:</strong> " + message + "</p>");
        $("#message").val("");
        $.post("/ask", { message: message }, function(data) {
            $("#chatbox").append("<p><strong>BiznesBot:</strong> " + data.response + "</p>");
            $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
        });
    });

    $("#chat-toggle").on("click", function() {
        $("#chat-container").toggle();
    });
});
