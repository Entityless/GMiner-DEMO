

$(document).ready(function(){
  /* init */
  $('body').css('height', window.innerHeight - 20).css('width', window.innerWidth - 20);
  $('#appParam').hide();
  $('p[group=std]').hide();

  $('#compareModal .slider').slick({
    dots: true,
    infinite: true,
    centerMode: true,
    draggable: false,
  });
  /* config */
  $('#apps').change(function(){
    var opt = $('#apps option:selected');
    var data_value = opt.attr('value');
    if(data_value === "cd" || data_value=="fco"){
      var title = opt.text() + " Parameters";
      $('#appParam .header:first-of-type').text(title);
      $('#appParam .field.param').hide();
      var selector_str = '#appParam .' + data_value;
      $(selector_str).show();
      $('#appParam').fadeIn();
    }
    else{
      $('#appParam').fadeOut();
    }
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

  /* content block */
  $('#contentMenu>.item').click(function(){
    if($(this).hasClass('active')){
      return;
    }
    // reset past active
    let orig_active = $('#contentMenu>.item.active');
    let group = orig_active.attr('group');
    let selector = '#console [group=' + group + ']';
    $(selector).hide();
    orig_active.removeClass('active');

    // activate this item
    group = $(this).attr('group');
    selector = '#console [group=' + group + ']';
    $(selector).show();
    $(this).addClass('active');

    if(group === "std") {
      $('#console').css('overflow-y', 'scroll');
    }
    else {
      $('#console').css('overflow-y', 'unset');
    }
  });
});
