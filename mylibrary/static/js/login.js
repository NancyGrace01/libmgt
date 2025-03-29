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
                window.location.href = "/dashboard/";
            },
            error: function (xhr) {
                var errorMsg = JSON.parse(xhr.responseText).error;
                $("#login-message").html("<p class='text-danger'>" + errorMsg + "</p>");
            },
        });
    });
});
