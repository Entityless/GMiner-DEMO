

$(document).ready(function(){
  /* init */
  $('.body').css('height', window.innerHeight).css('width', window.innerWidth);
  $('.dimmer.param').dimmer('hide');
  $('select.ui.dropdown').dropdown();
  $('#param-button').hide();
  $('.ui.modal').modal({detachable:false});

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

});
