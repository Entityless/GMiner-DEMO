$(document).ready(function() {
  var gt_nodes = [{name: "a"}, {name: "b"}, {name: "c"} , {name: "b"}, {name: "d"}];
  var gt_edges = [
    {source: 0, target: 1}, {source: 0, target: 2},
    {source: 1, target: 2}, {source: 2, source: 3},
    {source: 3, target: 4}];
  var colorScale = d3.scaleOrdinal().domain(d3.range('a'.charCodeAt(0), 'z'.charCodeAt(0)))
                    .range(d3.schemeSet3);
  /*
  var gt_force = d3.forceSimulation()
          .force("link",d3.forceLink())
          .force("charge",d3.forceManyBody())
          .force("center",d3.forceCenter());
  gt_force.nodes(gt_nodes);
  gt_force.force("link").links(gt_edges).distance(150);
  console.log(nodes);
  console.log(gt_edges);
  */
});
