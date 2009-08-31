$(function (){
      $("#actions-sticker").find(".label").click(function (){
                                                     $(this).parents("#actions-sticker").find('.content').toggle('blind');
      });
});