$('.ui.dropdown')
  .dropdown();
 
$('.ui.botton.switch').click(function(){
  if(!$(this).hasClass('active')){
    $('.ui.botton.pageSwitch.active').removeClass('active');
    $(this).addClass('active');
  }
});
