$.extend({
    hacklab: {
        parseJSON: function (text){
            return eval("(" + text + ")");
        },
        handleResponse: function (text) {
            var data = this.parseJSON(text);

            if (data.error) {
                $.shout('message-user', {
                            text: data.error,
                            type: error,
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