function dragstarted(d, force) {
  if (!d3.event.active) force.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}
function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}
function dragended(d, force) {
  if (!d3.event.active) force.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}
function makeNodeLine(id_list, label_list, conn_list) {
  let nodes = [], edges = [];
  for(let i=0; i < id_list.length; ++ i) {
    if(typeof(label_list) == "undefined")
      nodes.push({id:id_list[i]});
    else
      nodes.push({id:id_list[i], label: label_list[i]});
  }
  for(let i=0; i < conn_list.length; ++ i) {
    edges.push({"source": conn_list[i][0], "target":conn_list[i][1]});
  }
  return [nodes, edges];
}
function rendertcGraph(taskRes) {
  var {subg_list, label_list, conn_list, count, task_id="0"} = taskRes;
  var [nodes, edges] = makeNodeLine(subg_list, label_list, conn_list);
  var svg = d3.select('#maingraph');
  var force = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(edges).id((d)=>d.id).distance(100))
        .force('center', d3.forceCenter().x(graphEnv.mw/2).y(graphEnv.mh/2))
        .force("charge", d3.forceManyBody())

  var lines = svg.append("g").selectAll("line").data(edges).enter().append('line').style('stroke', 'black').style('stroke-width', 2);
  var circles = svg.append("g").selectAll("circle").data(nodes).enter().append('circle').attr('r', 10)
        .style('fill', (d, i)=> graphEnv.colorScale(i%24))
        .call(d3.drag()
           .on('start', function(d){dragstarted(d, force);})
           .on('drag', dragged)
           .on('end', function(d){dragended(d, force);}));
  circles.append("title").text((d)=>"id:"+d.id);
  force.on('tick', function() {
    circles.attr('cx', (d, i)=>d.x).attr('cy', (d,i)=>d.y);
    lines.attr('x1', (d,i)=>d.source.x)
      .attr('y1', (d,i)=>d.source.y)
      .attr('x2', (d,i)=>d.target.x)
      .attr('y2', (d,i)=>d.target.y);
  });

  if($('#graphnote>h4').length === 0){
    $('#graphnote').append('<h4>Realtime TC Task Sample</h4>');
    $('#graphnote').append('<table></table>');
    $('#graphnote table').append(
      ['<tr><td>task id: <span id="taskId">', task_id,'</span></td></tr>'].join(''));
    $('#graphnote table').append(
      ['<tr><td>task triangle count: <span id="tccount">', count,'</span></td></tr>'].join(''));
  }else{
    $('#taskId').text(task_id);
    $('#tccount').text(count);
  }
  $('#graphnote').show();
}
function rendergmGraph(taskRes) {
  var {subg_list, label_list, conn_list, count, task_id="0"} = taskRes;
  var [nodes, edges] = makeNodeLine(subg_list, label_list, conn_list);
  var svg = d3.select('#maingraph');
  var force = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(edges).id((d)=>d.id).distance(100))
        .force('center', d3.forceCenter().x(graphEnv.mw/2).y(graphEnv.mh/2))
        .force("charge", d3.forceManyBody())
  var lines = svg.append("g").selectAll("line").data(edges).enter().append('line').style('stroke', 'black').style('stroke-width', 2);
  var circles = svg.append("g").selectAll("circle").data(nodes).enter().append('circle').attr('r', 10)
        .style('fill', (d, i)=> graphEnv.colorScale(d.label))
        .call(d3.drag()
           .on('start', function(d){dragstarted(d, force);})
           .on('drag', dragged)
           .on('end', function(d){dragended(d, force);}));
  circles.append("title").text((d)=>"id: "+d.id+"\n"+"label: "+d.label);
  force.on('tick', function() {
    circles.attr('cx', (d, i)=>d.x).attr('cy', (d,i)=>d.y);
    lines.attr('x1', (d,i)=>d.source.x)
      .attr('y1', (d,i)=>d.source.y)
      .attr('x2', (d,i)=>d.target.x)
      .attr('y2', (d,i)=>d.target.y);
  });
  
  if($('#graphnote>h4').length === 0){
    $('#graphnote').append('<h4>Realtime GM Task Sample</h4>');
    $('#graphnote').append('<table></table>');
    $('#graphnote table').append(
      ['<tr><td>task id: <span id="taskId">', task_id,'</span></td></tr>'].join(''));
    $('#graphnote table').append(
      ['<tr><td>task matched pattern count: <span id="gmcount">', count,'</span></td></tr>'].join(''));
  }else{
    $('#taskId').text(task_id);
    $('#gmcount').text(count);
  }
  $('#graphnote').show();
}
function renderGraphVisualize(taskRes) {
  console.log('graph visual: ', taskRes);
  if(typeof(taskRes) == "undefined" || taskRes.length === 0) return;
  d3.select('#maingraph').selectAll('*').remove();
  if (ENV.apps === "tc"){
    rendertcGraph(taskRes);
  }
  else if (ENV.apps === "mc"){
    rendermcGraph(taskRes);
  }
  else if (ENV.apps === "gm"){
    rendergmGraph(taskRes);
  }
  else if (ENV.apps === "cd"){
    rendercdGraph(taskRes);
  }
  else if (ENV.apps === "fco"){
    renderfcoGraph(taskRes);
  }
}
var graphEnv = {};
$(document).ready(function() {
  $('#gmgt').hide();
  $('#graphnote').hide();
  var colorScale = d3.scaleOrdinal(d3.schemeSet1).domain(d3.range('a'.charCodeAt(0), 'z'.charCodeAt(0)));
  var mh = $('#graphPanel').height(), mw = $('#graphPanel #maingraph').width();
  var mainsvg = d3.select('#graphPanel #maingraph').style('height', mh);
  graphEnv.colorScale = colorScale;
  graphEnv.mh = mh;
  graphEnv.mw = mw;
  
  function makeGmPattern(svg) {
    var gt_nodes = [
      {name: "a", cx: 47.52, cy:48.59},
      {name: "b", cx: 33.44, cy: 75.08},
      {name: "c", cx: 63.43, cy: 74.02},
      {name: "b", cx: 49.25, cy: 100.46},
      {name: "d", cx: 50.13, cy: 130.44}];
    var gt_edges = [
      {"source": 0, "target": 1}, {"source": 0, "target": 2},
      {"source": 1, "target": 2}, {"source": 2, "target": 3},
      {"source": 3, "target": 4}];
    
    var ls = svg.append("g").selectAll("line").data(gt_edges).enter().append('line')
      .style('stroke', 'black').style('stroke-width', 2)
      .attr('x1', (d,i)=>gt_nodes[d["source"]].cx)
      .attr('y1', (d,i)=>gt_nodes[d["source"]].cy)
      .attr('x2', (d,i)=>gt_nodes[d["target"]].cx)
      .attr('y2', (d,i)=>gt_nodes[d["target"]].cy);
    var cirs = svg.append("g").selectAll("circle").data(gt_nodes).enter().append('circle').attr('r', 10)
      .style('fill', (d, i)=> colorScale(d.name))
      .attr('cx', (d, i)=> d.cx).attr('cy', (d,i)=>d.cy);
    cirs.append('title').text((d)=>d.name);
  }
  makeGmPattern(d3.select('#graphPanel #gmgt>svg'));
});


