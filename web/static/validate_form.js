var cache_field = {
  identifier: 'cache-size',
  rules: [{ type: 'integer[10000..10000000]'}]
};
var comp_th_field = {
  identifier: 'num-comp-thread',
  rules: [{type: 'integer[1..50]'}]
};
var pipe_pop_field = {
  identifier: 'pipe-pop-num',
  rules: [{type: 'integer[10..1000]'}]
};
var pop_field = {
  identifier: 'pop-num',
  rules: [{type: 'integer[10..1000]'}]
}
var subg_field = {
  identifier: 'subg-size-t',
  rules: [{type: 'integer[1..1000]'}]
};
var gc_mweight_field = {
  identifier: 'min-weight',
  optional: true,
  rules: [{type: 'regExp', value: /^(0+\.?|0*\.\d+|0*1(\.0*)?)$/}]
};
var gc_diff_ratio_field = {
  identifier: 'diff-ratio',
  optional: true,
  rules: [{type: 'regExp', value: /^(0+\.?|0*\.\d+|0*1(\.0*)?)$/}]
};
var gc_mcore_field = {
  identifier: 'min-core-size',
  rules: [{type: 'integer[1..]'}]
};
var gc_mres_field = {
  identifier: 'min-result-size',
  rules: [{type: 'integer[1..]'}]
};
var gc_iter_field = {
  identifier: 'iter-round-max',
  rules: [{type: 'integer[1..3000]'}]
};
var gc_cand_field = {
  identifier: 'cand-max-time',
  rules: [{type: 'integer[1..3000]'}]
};
var cd_thre_field = {
  identifier: 'k-threshold',
  rules: [{type: 'integer[2..1000000]'}]
};
var has_default_fields = {
  cache: cache_field,
  thread: comp_th_field,
  pipe: pipe_pop_field,
  pop: pop_field,
  subg: subg_field,
  cd:cd_thre_field,
  min_weight: gc_mweight_field,
  diffr: gc_diff_ratio_field,
  mcore: gc_mcore_field,
  mres: gc_mres_field,
  iter: gc_iter_field,
  cand: gc_cand_field
}
var ENV = { stdpt: 0 , key: undefined, timeid: undefined}; // global environment

function stopAll(data = 0) {
  $('#runButton').removeClass('disabled');
  $('#stopButton').removeClass('red').addClass('disabled');
  $('#queues .progress').removeClass('blue').addClass('disabled');
  if(typeof(ENV.timeid) != "undefined"){
    clearTimeout(ENV.timeid);
    ENV.timeid = undefined;
  }
}

function renderComponents(data){
  // 1. flush console
  let stdout = data['text'];
  let text = $('#console>p').html();
  $('#console>p').html(text + stdout);
  $('#console').scrollTop($('#console')[0].scrollHeight);
  data['text'] = '';
  console.log(data);
  ENV.stdpt = data.stdpt;
  // 2. flush queues
  $('#pq').progress({
    text: {percent: String(data['task_num_in_disk']) },
    percent: Number(data['task_num_in_disk_float']) * 100
  });
  $('#cmq').progress({
    text: {percent: String(data['cmq_size'])},
    percent: Number(data['cmq_size_float']) * 100
  });
  $('#cpq').progress({
    text: {percent: String(data['cpq_size'])},
    percent: Number(data['cpq_size_float']) * 100
  });
  return data['end'];  
}

function confirmContinue(is_end){
  if(is_end == '1'){
    stopAll();
    return;
  }
  ENV.timeid = setTimeout(manageInteraction, 1000);
}

function manageInteraction(){
  let request = {"key": ENV.key, "stdpt": ENV.stdpt};
  let url = '/interaction';
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(request),
    headers: new Headers({'Content-Type': 'application/json'})
  })
  .then(resp => resp.json())
  .then(renderComponents)
  .then(confirmContinue)
  .catch(err => console.error('Interaction error', err));
}

function changeComponents(data){
  console.log(data, data.status);
  if(data.status === "ok"){
    $('#content .segment').removeClass('loading');
    $('#stopButton').removeClass('disabled').addClass('red');
    $('#queues .progress').removeClass('disabled').addClass('blue');
    ENV.key = data.key;
    ENV.timeid = setTimeout(manageInteraction, 1000); // run after 1s
    ENV.stdpt = 0;
    return;
  }
  stopAll();
  alert('Run command fail, please reset parameters and try again!');
  throw "changeComponents error";
}

// life cycle start
function submitRunForm(e, fields){
  console.log('start submit');
  $('#console>p').text('');
  var url = '/runrequest';
  var data = JSON.stringify(fields);
  console.log(data);
  $('#runButton').addClass('disabled');
  $('#content .segment').addClass('loading');
  fetch(url, {
    method: 'POST',
    body: data,
    headers: new Headers({'Content-Type': 'application/json'})
  })
  .then(resp => resp.json())
  .then(changeComponents)
  .catch(e => {
    console.error(e);
    $('#content .segment').removeClass('loading');
    $('#runButton').removeClass('disabled');
    $('#stopButton').removeClass('red').addClass('disabled');
  });
}

$(document).ready(function(){
  /* initialize */
  $('.ui.form').form({
    fields: {
      apps: 'empty',
      dataset: 'empty'
    },
    onSuccess: submitRunForm
  });
  $('.ui.form').form('add fields', has_default_fields);
  /* actions */
  $('#runButton').click(function(){
    if($(this).hasClass('.disabled')){
      return;
    }
    let now_field_values = $('.ui.form').form('get values');
    for(let v in has_default_fields){
      let field = has_default_fields[v];
      let now_val = now_field_values[field.identifier];
      if(now_val === ""){
        let selector = '#' + field.identifier;
        let val = $(selector).attr('placeholder');
        $(selector).attr('value', val);
      }
    }
    $('.ui.form').form('validate form');
  });

  // bind stop
  $('#stopButton').on('click', function(){
    if(!$(this).hasClass('.disabled')){
      let stop_req = { "key": ENV.key };
      let url = '/stoprequest';
      console.log(ENV.key, " request stop");
      $(this).addClass('disabled');
      fetch(url, {
        method: 'POST',
        body: JSON.stringify(stop_req),
        headers: new Headers({'Content-Type': 'application/json'})
      })
      .then(stopAll)
      .catch(error => {console.log('stop failed'); throw error;});
    }
  });

});
