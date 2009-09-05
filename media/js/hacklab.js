$.extend({
    hacklab: {
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