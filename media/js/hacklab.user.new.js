$(function (){
      $("#new-user-form").validate({
            rules: {
                name: {
                    required: true
                },
                username: {
                    required: true,
                    minlength: 3
                },
                password: {
                    required: true
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
                    required: "Please provide a password"
                },
                email: "Please enter a valid email address"
            }
    });
});