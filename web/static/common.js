$(document).ready(function(){

  /* init */
  $('.dimmer.param').dimmer('hide');
  $('select.ui.dropdown').dropdown();
  $('#param-button').hide();
  $('.ui.modal').modal({detachable:false});
  $('.container').css('max-height', window.screen.availHeight);
  $('#queues .progress').progress({percent: 0});
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
