

$(document).ready(function(){
  /* init */
  $('body').css('height', window.innerHeight - 20).css('width', window.innerWidth - 20);
  // let tmp_console_h = $('#content').height() - $('#content>.menu').height() - 45;
  // $('#console').height(tmp_console_h);

  $('.ui.modal').modal({'useFlex':false});

  $('.slider').on('lazyLoaded', function(e, slick, image, imageSource){
    console.log(image);
    // $(image[0].offsetParent).removeClass('active').addClass('disabled');
  });
  $('#compareModal .slider').slick({
    dots: true,
    infinite: true,
    centerMode: true,
    draggable: false,
  });
  /* config */
  $('#apps').change(function(){
    var data_value = $('#apps option:selected').attr('value');
    if(data_value === "cd" || data_value=="fco"){
      $('#param-button').show().transition('jiggle');
    }
    else{
      $('#param-button').hide();
    }
  });

  $('#param-button').click(function(){ /* modal show */
    var opt = $('#apps option:selected');
    var title = opt.text() + " Parameters";
    $('#param-modal .field.param').hide();
    var selector_str = '#param-modal .' + opt.attr('value');
    $(selector_str).show();
    $('#param-modal .header:first-of-type').text(title);
    $('#param-modal').modal('show');
  });

  $('#config .popup').popup({ /* popupnote */
    on: 'click'
  });

  $('#aboutOpen').click(
    function(){
      $('#aboutModal').modal('show');
    });
  $('#configOpen').click(
    function(){
      $('#configModal').modal('show');
    });
  $('#aboutOpen').click(
    function(){
      $('#aboutModal').modal('show');
    });
  $('#compareOpen').click(
    function(){
      $('#compareModal .slider').slick('slickGoTo', 0);
      $('#compareModal').modal('show');
    });
  $('#teamOpen').click(
    function(){
      $('#teamModal').modal('show');
    }
  );
  

});
