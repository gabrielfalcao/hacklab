$(function (){
      $("#change-password-form").validate({
            rules: {
                password: {
                    required: true
                },
                confirm: {
                    required: true,
		    equalTo: "#password"
                }
            },
            messages: {
                password: {
                        required: "Please provide a password"
                },
                confirm: {
                        required: "Please provide a confirmation",
                        equalTo: "The passwords doesn't match"
                }
            }
    });
      $("#change-password-form").ajaxForm(
          {
              success: function (textStatus, other) {
                  $.shout('message-user', {
                              text: 'Password changed successfully!',
                              type: 'success',
                              timeout: 3
                          });
              }
          }
      );
});