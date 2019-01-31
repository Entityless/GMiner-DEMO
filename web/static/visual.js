function getEdgeCoor(nodes, edge) {
  let x1 = nodes[edge["source"]].cx, y1 = nodes[edge["source"]].cy;
  let x2 = nodes[edge["target"]].cx, y2 = nodes[edge["target"]].cy;
  return {"x1": x1,"y1": y1,"x2":x2,"y2":y2};
}
$(document).ready(function() {
  var colorScale = d3.scaleOrdinal(d3.schemeSet1).domain(d3.range('a'.charCodeAt(0), 'z'.charCodeAt(0)));
  var mh = $('#graphPanel').height(), mw = $('#graphPanel #maingraph').width();
  var mainsvg = d3.select('#graphPanel #maingraph').style('height', mh);
  
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
  /* show gm gt
  var gt_force = d3.forceSimulation().nodes(gt_nodes)
    .force('link', d3.forceLink(gt_edges))

  var lines = g.append("g").selectAll("line").data(gt_edges).enter().append('line').style('stroke', 'black').style('stroke-width', 2);
  var circles = g.append("g").selectAll("circle").data(gt_nodes).enter().append('circle').attr('r', 10)
    .style('fill', (d, i)=> colorScale(d.name))
    .call(d3.drag()
       .on('start', dragstarted)
       .on('drag', dragged)
       .on('end', dragended));
  circles.append("title").text((d)=>d.name);

  gt_force.on('tick', function() {
    circles.attr('cx', (d, i)=>{return d.x}).attr('cy', (d,i)=>{return d.y});
    lines.attr('x1', (d,i)=>d.source.x)
      .attr('y1', (d,i)=>d.source.y)
      .attr('x2', (d,i)=>d.target.x)
      .attr('y2', (d,i)=>d.target.y);
  });
  function dragstarted(d) {
    if (!d3.event.active) gt_force.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    if (!d3.event.active) gt_force.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  console.log(gt_nodes);
  console.log(gt_edges);
  */
});


