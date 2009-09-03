$(function (){
      $("#new-repository-form").validate({
            rules: {
                name: {
                    required: true,
                    minlength: 2
                }
            },
            messages: {
                name: "Well, your project deserve a name, right ?"
            }
    });
});