$(document).ready(function () {
    $("#login-form").submit(function (e) {
        e.preventDefault();

        var formData = $(this).serialize();
        var csrftoken = $("input[name=csrfmiddlewaretoken]").val();

        $.ajax({
            type: "POST",
            url: "/login/",
            data: formData,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (response) {
                $("#login-message").html("<p class='text-success'>" + response.message + "</p>");
                
                if (response.redirect_url) {
                    setTimeout(function () {
                        window.location.href = response.redirect_url;
                    }, 1000);
                } else {
                    $("#login-message").html("<p class='text-danger'>Missing redirect URL.</p>");
                }
            },
            
            error: function (xhr) {
                var errorMsg = xhr.responseJSON?.error || "An error occurred.";
                $("#login-message").html("<p class='text-danger'>" + errorMsg + "</p>");
            },
        });
    });
});
