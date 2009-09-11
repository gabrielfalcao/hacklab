jQuery.extend(jQuery.fn,
              {
                  rockMyForm: function (rules, messages, success, formOptions) {
                      if (typeof rules != 'object') {
                          rules = {};
                      }
                      if (typeof messages != 'object') {
                          messages = {};
                      }
                      if (!formOptions) {
                          formOptions = {};
                      }
                      if (typeof rules === 'function') {
                          success = rules;
                      } else if (typeof messages === 'function') {
                          success = messages;
                      }
                      return this.each(function (){
                                           $(this).validate(
                                               {
                                                   rules: rules,
                                                   messages: messages,
                                                   submitHandler: function (form) {
                                                       $(form).ajaxSubmit(
                                                           $.extend(
                                                               formOptions,
                                                               {
                                                                   success: function (textStatus, other) {
                                                                       var data = $.hacklab.handleResponse(textStatus);
                                                                       if (success) {
                                                                           success(data);
                                                                       }
                                                                   }
                                                               })
                                                       )
                                                   }
                                               }
                                           );
                                       });
                  }
              });
$.extend({
             hacklab: {
                 request: function (options) {
                     var self = this;
                     var originalErrorCallback = null;
                     var originalSucessCallback = null;
                     if (options.error) {
                         originalErrorCallback = options.error;
                     }
                     if (options.success) {
                         originalSuccessCallback = options.success;
                     }

                     var settings = {
                         success: function (data, textStatus){
                             var json = self.handleResponse(data);
                             return originalSuccessCallback(json, data, textStatus);
                         },
                         error: function (XMLHttpRequest, textStatus, errorThrown) {
                             $.shout('message-user', {
                                         text: "Oops! Something went wrong!",
                                         type: 'error'
                                     });
                             if (typeof originalErrorCallback === 'function') {
                                 return originalErrorCallback(XMLHttpRequest, textStatus, errorThrown);
                             }
                             return false;
                         }
                     }
                     options = $.extend(options, settings);
                     $.ajax(options);
                 },
                 parseJSON: function (text){
                     return eval("(" + text + ")");
                 },
                 handleResponse: function (text) {
                     var data = this.parseJSON(text);

                     if (data.error) {
                         $.shout('message-user', {
                                     text: data.error,
                                     type: 'error',
                                     timeout: 7
                                 });
                         return null;
                     }
                     return data
                 }
             }
         });

$(function(){
      $("#top-message").hear('message-user', function ($self, data){
                                 var $text = $("#top-message-text");
                                 $self.hide();
                                 if (!data.type) {
                                     data.type = 'success';
                                 }
                                 $text.addClass(data.type);
                                 $text.text(data.text);
                                 $self.show('drop', {'direction': 'up'}, 'slow', function () {
                                                setTimeout(function () {
                                                               $self.hide('drop', {'direction': 'up'}, 'slow');
                                                               $text.removeClass(data.type);
                                                           }, 1000 * (data.timeout || 3));
                                            });
                             });


  });

