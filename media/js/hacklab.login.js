$(function (){
      $("#login").validate({
            rules: {
                password: {
                    required: true
                },
                email: {
                    required: true,
                    email: true
                }
            },
            messages: {
                password: {
                    required: "Humm, how could you login without providing a password ?",
                },
                email: "Well, we need your email to identify you :)"
            }
    });
});