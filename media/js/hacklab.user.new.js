$(function (){
      $("#new-user-form").validate({
            rules: {
                name: {
                    required: true,
                    minlength: 5
                },
                username: {
                    required: true,
                    minlength: 3
                },
                password: {
                    required: true,
                    minlength: 5
                },
                email: {
                    required: true,
                    email: true
                }
            },
            messages: {
                name: "Please enter your name",
                username: "Please choose a username",
                password: {
                    required: "Please provide a password",
                    minlength: "Your password must be at least 5 characters long"
                },
                email: "Please enter a valid email address"
            }
    });
});