$(function (){
      $("#add-key-box").dialog(
          {
              autoOpen: false,
              draggable: true,
              resizable: true,
              width: '600px',
              modal: true,
              title: "Add a public ssh key"
          });

      $(".delete-key").live(
          'click',
          function (){
              var almostKeyUUID = $(this).attr("id");
              var keyUUID = /delete[:]([a-z0-9-]+)/.exec(almostKeyUUID)[1];
              $.hacklab.request({
                                    url: "/user/key/" + keyUUID + "/delete",
                                    success: function(data, textStatus) {
                                        $.shout('ssh-key-deleted', data);
                                        $.shout('message-user', { text: 'key deleted successfully!' });
                                    }
                                });
              return false;
          }
      );

      $(".edit-key").live(
          'click',
          function (){
              var almostKeyUUID = $(this).attr("id");
              var keyUUID = /edit[:]([a-z0-9-]+)/.exec(almostKeyUUID)[1];
              $.hacklab.request({
                                    url: "/user/key/" + keyUUID + "/json",
                                    success: function(data, textStatus) {
                                        $.shout('ssh-key-edited', data);
                                        $.shout('message-user', { text: 'key edited successfully!' });
                                    }
                                });

              return false;
          }
      );

      $("#change-password-form").hear('password-changed', function ($self, data){
                                          $self.resetForm();

                                      });
      $("#total-of-keys").hear('ssh-key-added',
                               function ($self, key){
                                   var total = $self.text();
                                   var number = parseInt(total) + 1;
                                   $self.text(number);
                               }
                              );
      $("#total-of-keys").hear('ssh-key-deleted',
                               function ($self, key){
                                   var total = $self.text();
                                   var number = parseInt(total) - 1;
                                   $self.text(number);
                               }
                              );

      $("#key-list").hear('ssh-key-deleted',
                          function ($self, key){
                              $self.find("#" + key.uuid).remove();
                              if ($self.find("li.ssh-key").length == 0) {
                                  $("#add-ssh-key").text("add a key");
                              } else {
                                  $("#add-ssh-key").text("add another key");
                              }
                          }
                         );

      $("#key-list").hear('ssh-key-added',
                          function ($self, key){
                              $list = $self.find('li.template').clone(true);
                              $list.attr("id", key.uuid);
                              $list.find("span.text").text(key.description);
                              $list.find("a.edit-key").attr("id", "edit:" + key.uuid);
                              $list.find("a.delete-key").attr("id", "delete:" + key.uuid);
                              $list.addClass("ssh-key");
                              $list.removeClass("template");
                              $self.prepend($list);
                              if ($self.find("li.ssh-key").length == 0) {
                                  $("#add-ssh-key").text("add a key");
                              } else {
                                  $("#add-ssh-key").text("add another key");
                              }

                          }
                         );

      $("#add-ssh-key").live('click',
                             function (){
                                 $("#add-key-box").dialog('open');
                             }
                            );


      $("#change-password-form").rockMyForm(
          {
              password: {
                  required: true
              },
              confirm: {
                  required: true,
		  equalTo: "#password"
              }
          },
          {
              password: {
                  required: "Please provide a password"
              },
              confirm: {
                  required: "Please provide a confirmation",
                  equalTo: "The passwords doesn't match"
              }
          },
          function (data, other) {
              var msg = 'Password changed successfully!';
              var type = 'success';

              if (data.error) {
                  msg = data.error;
                  type = 'error';
              } else {
                  $.shout('password-changed', data);
              }

              $.shout('message-user', {
                          text: msg,
                          type: type,
                          timeout: 5
                      });
          }
      );

      $("#add-key-form").rockMyForm(
          {
              description: {
                  required: true
              },
              key: {
                  required: true
              }
          },
          {
              password: {
                  required: "Please add a description to your key"
              },
              key: {
                  required: "Please add your key"
              }
          },
          function (data, other) {
              if (data) {
                  $.shout('message-user', { text: 'key added successfully!' });
                  $.shout('ssh-key-added', data);
                  $("#add-key-box").dialog('close');
                  $("#add-key-form").resetForm();
              }
          });

      $("#form-save-new-repos").rockMyForm(
          {}, {},
          function (data, other) {
              if (data) {
                  $.shout('message-user', { text: data.name + ' created successfully!' });
                  $.shout('repository-created', data);
              }
          });
      $("#create-new-repos").live(
          'click',
          function (){
              $("#create-new-repos-div").hide(
                  'drop', {'direction': 'up'}, 'fast',
                  function () {
                      $("#save-new-repos-div").show('drop', {'direction': 'down'}, 'fast');
                  });
          });

          $("#save-new-repos-div").hear(
              'repository-created',
              function ($self, repository) {
                  $self.find("form").resetForm();

                  $self.hide('drop', {'direction': 'up'}, 'fast', function (){
                      $("#create-new-repos-div").show('drop', {'direction': 'down'}, 'fast');
                             });
              }
          );
  });