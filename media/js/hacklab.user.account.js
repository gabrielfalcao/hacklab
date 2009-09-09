$(function (){
                $("#total-of-keys").hear('ssh-key-added',
                                         function ($self, key){
                                             var total = $self.text();
                                             var number = parseInt(total) + 1;
                                             $self.text(number);
                                         }
                                        );
                $("#key-list").hear('ssh-key-added',
                                    function ($self, key){
                                        $list = $self.find('li.template').clone(true);
                                        $list.find("span.text").text(key.description);
                                        $list.find("a.edit-key").attr("id", "edit:" + key.uuid);
                                        $list.find("a.delete-key").attr("id", "delete:" + key.uuid);
                                        $list.removeClass("template");
                                        $self.prepend($list);
                                    }
                                   );

                $("#add-ssh-key").live('click',
                                       function (){
                                           $("#add-key-box").dialog(
                                               {
                                                   draggable: true,
                                                   resizable: true,
                                                   width: '600px',
                                                   modal: true,
                                                   title: "Add a public ssh key"
                                               });

                                       }
                                      );


      $("#change-password-form").validate(
          {
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
              },
              submitHandler: function(form) {
		  $(form).ajaxSubmit(
                      {
                          success: function (textStatus, other) {
                              var data = eval("(" + textStatus + ")");
                              var msg = 'Password changed successfully!';
                              var type = 'success';

                              if (data.error) {
                                  msg = data.error;
                                  type = 'error';
                              }

                              $.shout('message-user', {
                                          text: msg,
                                          type: type,
                                          timeout: 5
                                      });
                          }
                      }
                  );
              }
          }
      );

      $("#add-key-form").validate(
          {
              rules: {
                  description: {
                      required: true
                  },
                  key: {
                      required: true
                  }
              },
              messages: {
                  password: {
                      required: "Please add a description to your key"
                  },
                  key: {
                      required: "Please add your key"
                  }
              },
              submitHandler: function(form) {
		  $(form).ajaxSubmit(
                      {
                          success: function (textStatus, other) {
                              var data = $.hacklab.handleResponse(textStatus);
                              if (data) {
                                  $.shout('message-user', { text: 'key added successfully!' });
                                  $.shout('ssh-key-added', data);
                                  $("#add-key-box").dialog('close');
                                  $("#add-key-form").resetForm();
                              }
                          }
                      }
                  );
              }
          }
      );

  });