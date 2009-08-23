$(function (){
      $("input.field").change(function (){
          var done = true;
          $("input.field").each(function () {
                                    if (!$(this).val()) {
                                        done = false;
                                    }
                                });
                                  if (done) {
                                      $("#submit").removeAttr("disabled");
                                  }
      });
});