$(document).ready(function(){
  const jsonPath = "load_json/runtime-infos/monitor-data.json";
  const refreshInterval = 500; //In ms
  const numOfType = 3;         //Number of type to display
  const maxItem   = 60;        //Maximun number of item in each json file
  const chartColors = ['#1890ff', '#ff1429', '#2ef924'];
  var chartheight = window.innerHeight * 0.4;
  var items = [];
  var chart = new G2.Chart({
      container: 'chartView',
      forceFit: true,
      height: chartheight,
      animate: false,
    });
  chart.scale('time', {
      tickInterval: maxItem
    });
  chart.scale('value', {
      max:1,
      min:0,
      formatter: val=>{ return val * 100 + "%";},
  });
  chart.axis('value', {
    label: {
      textStyle: {
        fill: '#000000'
      }
    }
  });
  chart.axis('time', {
    label: {
      textStyle: {
        fill: '#000000'
      }
    }
  });
  chart.tooltip(false);
  chart.line().position('time*value').color('type', chartColors);

  for(i = 0; i < maxItem; i++){
      items.push({name: "0%",
                  marker:{
                      symbol:'square',
                      fill: chartColors[i]
                  }});
  }

  chart.legend({
    custom: true,
    items: items,
    textStyle: {
      fill: '#000000',
    }
  });
  chart.render();

  var updateChart = function(){
     $.getJSON(jsonPath, function(data){
        index = 0;
        for(i = 0; i < data.length / numOfType; i++){
          for(j = 0; j < numOfType; j ++){
            data[index].time = i;
            index ++;
          }
        }
        index -= numOfType;
        // Update Current Value for each type
        for(j = 0; j < numOfType; j ++){
            items[j].value = data[index].type + ": " + (data[index].value*100).toFixed(2) + "%";
            index++;
        }
        chart.changeData(data);
     });
  };

  setInterval(updateChart, refreshInterval);
});
