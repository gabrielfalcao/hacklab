$.extend($.hacklab,
         {
             user: {}
         });

$(function (){
    $("#actions-sticker").find(".label").click(function (){
        $(this).parents("#actions-sticker").find('.content').toggle('blind');
        return false;
    });
});