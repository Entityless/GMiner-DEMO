$(document).ready(function(){
  const jsonPath = "/data/mc-data.json";
  var w = 1000;
  var h = 600;
  var refreshInterval = 2000;

  var svg = d3.select("#MCGraphView").append("svg").attr({"width":w,"height":h});
  var div = d3.select("#MCGraphView").append("div").attr("class", "tooltip").style("opacity", 0);
  var div1 = d3.select("#MCGraphView").append("div").attr("class", "tooltip");

  var startX = svg.node().getBBox().x;
  var startY = svg.node().getBBox().y;
  div1.html("Max CLIQUE Size: 0")
     .style("left", startX + 20)
     .style("top", startY + 20);
     
  var updateMCGraph = function(){
  $.getJSON(jsonPath, function(data){
      d3.layout.force().stop();
      div.style("opacity", 0);
      var dataset = {
          version : 0,
          size : 67,
          count : 1,
          group1 : [],
          group2 : []
      };
      for(i = 0; i < dataset.size; i ++){
          dataset.group1.push(i);
      }
      for(i = dataset.size; i < 2 * dataset.size; i ++){
          dataset.group2.push(i);
      }
      div1.html("Max CLIQUE Size: " + size);
      labels = {};
      edges = [];
      nodes = [];
      nodeCount = 0;
      gap = w / (dataset.count + 1);
      linkDistance = 3.33 * size + 100;
      for(i = 0; i < dataset.count; i ++){
         label = "";
         group = dataset["group"+(i+1)];
         x = gap * (i * 1.3 + 0.7) + startX;
         y = h / 2 + startY;
         for(j = 0; j < group.length; j ++){
           nodes.push({idx: group[j], x:x, y:y, connGroup: i});
           label += group[j] + ", ";
         }
         label = label.substring(0, label.length - 2);
         labels[i] = label;
         for(j = 0; j < group.length; j ++){
          for(z = j + 1; z < group.length; z++){
              edge = {};
              edge.source = nodes[j + nodeCount];
              edge.target = nodes[z + nodeCount];
              edges.push(edge);
          }
         }
         nodeCount += group.length;
      }
     
      
      svg.selectAll("*").remove();
      var force = d3.layout.force()
          .nodes(nodes)
          .links(edges)
          .size([w,h])
          .linkDistance([linkDistance])
          .linkStrength(0.1)
          .charge(-0.1)
          .theta(0.1)
          .gravity(0)
          .start();
          
      var edgeItems = svg.selectAll("line")
        .data(edges)
        .enter()
        .append("line")
        .attr("id",function(d,i) {return 'edge'+i})
        .style("stroke","#ccc")
        .style("pointer-events", "none")
        .style("stroke-width", 1 - size * 4 / 400);
      
      var nodeItems = svg.selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr({"r":5})
        .style("fill",function(d,i){return "#888888";})
        .call(force.drag)
        .on("mouseover", function(d){
          div.style("opacity", 0.8);
          div.html("Node id: " + d.idx + "<br/>CLIQUE Group: " + labels[d.connGroup])
             .style("left", (d3.event.pageX) + "px")
             .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function(d){
          div.style("opacity", 0);
        });

      for(i = 0; i < 50 + size; i++) force.tick();
      
      force.on("tick", function(){
          edgeItems.attr({"x1": function(d){return d.source.x;},
                      "y1": function(d){return d.source.y;},
                      "x2": function(d){return d.target.x;},
                      "y2": function(d){return d.target.y;},});

          nodeItems.attr({"cx":function(d){return d.x;},
                      "cy":function(d){return d.y;}});
      });
  }};
  updateMCGraph();
  setInterval(updateMCGraph, refreshInterval);

});
