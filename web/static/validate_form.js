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
var ENV = { stdpt: 0 , key: undefined, timeid: undefined, chart: undefined}; // global environment

function stopAll(data = 0) {
  $('#runButton').removeClass('disabled');
  $('#stopButton').removeClass('red').addClass('disabled');
  $('#queues .progress').removeClass('blue').addClass('disabled');
  $('#finish-label').addClass('disabled');
  if(typeof(ENV.timeid) != "undefined"){
    clearTimeout(ENV.timeid);
    ENV.timeid = undefined;
  }
  if(typeof(ENV.chart) != "undefined") {
    ENV.chart.scale('time', {
      tickInterval: 120
    });
    ENV.chart.render();
  }
}

function renderComponents(data){
  // 1. flush console
  let stdout = data['text'];
  let text = $('#stdConsole>p').html();
  $('#stdConsole>p').html(text + stdout);
  if($('#contentMenu>.item.active').attr('group') === 'std'){
    $('#stdConsole').scrollTop($('#stdConsole')[0].scrollHeight);
  }
  data['text'] = '';
  console.log(data);
  ENV.stdpt = data.stdpt;

  arrow_label_suffix = ' Tasks/sec';
  // 2. flush queues
  $('#pq').progress({
    text: {percent: String(data['task_num_in_disk']) },
    percent: Number(data['task_num_in_disk_float']) * 100
  });
  $('#pq .arrow-label').text(String(data['task_transfer_1']) + arrow_label_suffix);

  $('#cmq').progress({
    text: {percent: String(data['cmq_size'])},
    percent: Number(data['cmq_size_float']) * 100
  });
  $('#cmq .arrow-label').text(String(data['task_transfer_2']) + arrow_label_suffix);

  $('#cpq').progress({
    text: {percent: String(data['cpq_size'])},
    percent: Number(data['cpq_size_float']) * 100
  });
  $('#cpq .arrow-label').text(String(data['task_transfer_3']) + arrow_label_suffix);
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
    $('#finish-label').removeClass('disabled');
    if(data.apps === "gm"){
    }
    else {
    }
    ENV.key = data.key;
    ENV.timeid = setTimeout(manageInteraction, 1000); // run after 1s
    ENV.stdpt = 0;
    ENV.chart.scale('time', {
      tickInterval: 300
    });
    ENV.chart.render();
    return;
  }
  stopAll();
  alert('Run command fail, please reset parameters and try again!');
  throw "changeComponents error";
}

// life cycle start
function submitRunForm(fields){
  console.log('start submit');
  $('#stdConsole>p').text('');
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
  .catch(function(e) {
    console.error(e);
    $('#content .segment').removeClass('loading');
    $('#runButton').removeClass('disabled');
    $('#stopButton').removeClass('red').addClass('disabled');
  });
}

function validateFormWithDefault() {
  let now_field_values = $('#config .ui.form').form('get values');
  console.log(now_field_values);
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
  return $('.ui.form').form('is valid');
}
$(document).ready(function(){
  /* initialize */
  $('.ui.form').form({
    fields: {
      apps: 'empty',
      dataset: 'empty'
    },
    duration: 800
  });
  $('.ui.form').form('add fields', has_default_fields);
  /* actions */
  $('#configModal').modal({
    onApprove: validateFormWithDefault
  });

  $('#runButton').click(function(){
    if($(this).hasClass('.disabled')){
      return;
    }
    let res = validateFormWithDefault();
    if(res === true) {
      submitRunForm($('#config .ui.form').form('get values'));
    }
    else{
      $('#configModal').modal('show');
    }
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
      .catch(error => {console.log('stop failed'); throw error;});
      stopAll();
    }
  });

});
