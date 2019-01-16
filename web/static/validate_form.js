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
function changeComponents(data){
  console.log(data);
  if(data.status === "ok"){
    $('#content .segment').removeClass('loading');
    $('#stopButton').removeClass('disabled');
    $('#queues .progress').removeClass('disabled').addClass('blue');
  }
  else{
    alert('Run command fail, please reset parameters and try again!');
    throw "changeComponents error";
  }
}
function submitRunForm(e, fields){
  console.log('start submit');
  var url = '/runrequest';
  var data = JSON.stringify(fields);
  console.log(data);
  fetch(url, {
    method: 'POST',
    body: data,
    headers: new Headers({
      'Content-Type': 'application/json'
    })
  })
  .then(resp => resp.json())
  .then(changeComponents)
  .catch(error => console.error(error));
  $('#runButton').addClass('disabled');
  $('#content .segment').addClass('loading');
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
});
