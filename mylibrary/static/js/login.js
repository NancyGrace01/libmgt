$(document).ready(function() {
    $('#login-form').submit(function(e) {
        e.preventDefault();  // Prevent default form submission

        $.ajax({
            type: 'POST',
            url: '/login/',
            data: $(this).serialize(),
            dataType: "json",
            success: function(response) {
                $('#login-message').text(response.message);
                if (response.success) {
                    window.location.href = "/dashboard/"; 
                }
            },
            error: function() {
                $('#login-message').text("An error occurred. Please try again.");
            }
        });
    });
});
