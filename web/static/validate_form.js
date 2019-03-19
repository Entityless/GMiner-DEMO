function stopAll(data = 0) {
  $('#runButton').removeClass('disabled');
  $('#stopButton,#pauseButton').addClass('disabled');
  $('#queues .progress').addClass('disabled');
  $('.arrows i').removeClass('move');
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
  $('#pq .arrow-label').text(String(data['task_transfer_1']));
  $('#cmq').progress({
    text: {percent: String(data['cmq_size'])},
    percent: Number(data['cmq_size_float']) * 100
  });
  $('#cpq').progress({
    text: {percent: String(data['cpq_size'])},
    percent: Number(data['cpq_size_float']) * 100
  });
  $('#qlabel1').text(String(data['task_transfer_1']));
  $('#qlabel2').text(String(data['task_transfer_2']));
  $('#qlabel3').text(String(data['task_transfer_3']));
  $('#qlabel4').text(String(data['task_transfer_4']));

  renderGraphVisualize(data['taskRes']);
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
    $('#stopButton,#pauseButton').removeClass('disabled');
    $('#queues .progress').removeClass('disabled');
    $('.arrows i').addClass('move');
    d3.select('#maingraph').selectAll('*').remove();
    if(data["apps"] === "gm"){
      $('#gmgt').show();      
    }
    else {
      $('#gmgt').hide();      
    }
    ENV.key = data.key;
    ENV.timeid = setTimeout(manageInteraction, 1000); // run after 1s
    ENV.apps = data.apps;
    ENV.stdpt = 0;
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
  $('#graphnote').hide();
  $('#graphnote *').remove();
  var url = '/runrequest';
  var data = JSON.stringify(fields);
  console.log(data);
  $('#runButton').addClass('disabled');
  $('#content>.segment').addClass('loading');
  fetch(url, {
    method: 'POST',
    body: data,
    headers: new Headers({'Content-Type': 'application/json'})
  })
  .then(resp => resp.json())
  .then(changeComponents)
  .catch(function(e) {
    $('.arrows i').removeClass('move');
    $('#content .segment').removeClass('loading');
    $('#runButton').removeClass('disabled');
    $('#stopButton,#pauseButton').addClass('disabled');
    $('#resumeButton').hide();
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
function updateTableInfo() {
  let now_field_values = $('#config .ui.form').form('get values');
  console.log('updateTableInfo: ',now_field_values);
  for(let v in now_field_values){
    let selector = '#table' + v;
    let table_item = $(selector);
    let input_selector = '#' + v;
    
    if(v === "ib"){
      let val;
      if(now_field_values[v]) val="Infiniband";
      else val = "Ethernet";
      table_item.text(val);
    }
    else if(now_field_values[v] === ""){
      let val = $(input_selector).attr('placeholder');
      if(typeof(val)=="undefined"){
        val = "unset";
      }
      else{
        val = val + ' (default)';
      }
      table_item.text(val);
    }
    else if(v === "apps"){
      let opt = $('#apps option:selected');
      let val = opt.text();
      table_item.text(val);
    }
    else{
      table_item.text(now_field_values[v]);
    }
  }
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
    onApprove: validateFormWithDefault,
    onHidden: updateTableInfo
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
    if(!$(this).hasClass('disabled')){
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

  $('#pauseButton').on('click', function(){
    if(!$(this).hasClass('disabled')){
      $(this).hide();
      $('#resumeButton').show();
    }
  });

  $('#resumeButton').on('click', function(){
    $(this).hide();
    $('#stopButton').addClass('disabled');
  });

});
