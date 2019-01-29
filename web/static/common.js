$(document).ready(function(){
  /* init */
  $('body').css('height', window.innerHeight - 20).css('width', window.innerWidth - 20);
  $('#appParam').hide();
  $('p[group=std]').hide();
  $('.compare-item').height(window.innerHeight * 0.7).first().addClass('active').show();
  $('.compare-item').css('bottom', window.innerHeight - $('#compareModal .actions').height() - $('#compreModal .actions').css('bottom'));

  $('#prev').click(function() {
    let active_item = $('.compare-item.active')[0];
    let length = $('.compare-item').length;
    let new_idx, idx = -1;
    for(let i=0; i < length; ++ i) {
      if($('.compare-item')[i] === active_item){
        idx = i;
        break;
      }
    }
    if(idx === 0) {
      new_idx = length - 1;
    }
    else {
      new_idx = idx - 1;
    }
    $('.compare-item.active').fadeOut(400,
      function() {
        $($('.compare-item')[new_idx]).fadeIn().addClass('active');
      }
    ).removeClass('active');
    console.log('prev now active image ', idx);
  });

  $('#next').click(function() {
    let active_item = $('.compare-item.active')[0];
    let length = $('.compare-item').length;
    let new_idx, idx = -1;
    for(let i=0; i < length; ++ i) {
      if($('.compare-item')[i] === active_item){
        idx = i;
        break;
      }
    }

    new_idx = (idx + 1) % length;
    $('.compare-item.active').fadeOut(400,
      function() {
        $($('.compare-item')[new_idx]).addClass('active').fadeIn();
      }
    ).removeClass('active');
    console.log('next now active image ', idx);
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


  $('#aboutOpen').click(
    function(){
      $('#aboutModal').modal('show');
    });
  $('#configOpen').click(
    function(){
      $('#configModal').modal('show');
      $('.popup').popup(
        {on: 'click'}
      );
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
