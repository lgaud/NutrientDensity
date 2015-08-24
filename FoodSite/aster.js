// Based on sample from: http://bl.ocks.org/bbest/2de0e25d4840c68f2db1
var maxScore = 10.0; // Maximum value shown on the chart & score
var margin = { top: 50, right: 30, bottom: 30, left: 30 };
var width = 400
    height = 400
    radius = Math.min(width, height) / 2,
    innerRadius = 0.2 * radius;

var chartHeight = height + margin.top + margin.bottom;
var chartWidth = width + margin.right + margin.bottom

var pie = d3.layout.pie()
    .sort(null)
    .value(function (d) { return d.width; });

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([0, 0])
  .html(function (d) {
      return d.data.label + ": <span style='color:orangered'>" + d3.round(d.data.score,2) + "</span>";
  });

var arc = d3.svg.arc()
  .innerRadius(innerRadius)
  .outerRadius(function (d) {
      return (radius - innerRadius) * (d.data.cappedScore / maxScore) + innerRadius;
  });

var oneArc = d3.svg.arc().innerRadius(innerRadius).outerRadius((radius - innerRadius) * (1 / maxScore) + innerRadius)

var outlineArc = d3.svg.arc()
        .innerRadius(innerRadius)
        .outerRadius(radius);

d3.csv('food_out.csv', function (error, input) {
    var selectorData = $.map(input, function (val, index) {
        return { label: val.Shrt_Desc, data: val };
    });
    
    var svg1 = d3.select("#chart1");
    svg1.attr("width", chartWidth)
            .attr("height", chartHeight)
    svg1.call(tip);
    
    asterChart(input[Math.floor(Math.random() * input.length)], svg1);

    var svg2 = d3.select("#chart2");
    svg2.attr("width", chartWidth)
            .attr("height", chartHeight)

    svg2.call(tip);
    asterChart(input[Math.floor(Math.random() * input.length)], svg2);

    $("#food1Picker").autocomplete({
        source: selectorData,
        select: function (event, ui) {
            var svg = d3.select("#chart1");
            asterChart(ui.item.data, svg);
        }
    });

    $("#food2Picker").autocomplete({
        source: selectorData,
        select: function (event, ui) {
            var svg = d3.select("#chart2");            
            asterChart(ui.item.data, svg);
        }
    });
});

function asterChart(row, svg) {
    var data = foodRowToAster(row)
    var title = row.Shrt_Desc;

    svg.selectAll("*").remove();
    var chart = svg.append("g").attr("transform", "translate(" + ((width / 2) + margin.right) + "," + ((height / 2) + margin.top) + ")");
    chart.call(tip);

    var path = chart.selectAll(".solidArc")
        .data(pie(data))
      .enter().append("path")
        .attr("fill", function (d) { return d.data.color; })
        .attr("class", "solidArc")
        .attr("stroke", "gray")
        .attr("d", arc)
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

    var outerPath = chart.selectAll(".outlineArc")
        .data(pie(data))
        .enter().append("path")
        .attr("fill", "none")
        .attr("stroke", "gray")
        .attr("class", "outlineArc")
        .attr("d", outlineArc);

    // calculate the weighted mean score
    var score =
      data.reduce(function (a, b) {
          //console.log('a:' + a + ', b.score: ' + b.score + ', b.weight: ' + b.weight);
          return a + (b.cappedScore * b.weight);
      }, 0) /
      data.reduce(function (a, b) {
          return a + b.weight;
      }, 0);

    chart.append("svg:text")
      .attr("class", "aster-score")
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .text(d3.round(score, 1));

    var maxTitleLength = 50; // Truncate long titles
    svg.append("text")
    .attr("x", (width / 2) + margin.left)
    .attr("y", margin.top / 2)
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .text(title.substr(0, maxTitleLength));

}
function foodRowToAster(row) {
    var columns = ["Iron_Density", "Calcium_Density", 
        "Magnesium_Density", "Potassium_Density", "Vit_C_Density", 
        "Folate_Density", "Vit_A_Density", "Vit_E_Density", "Vit_D_Density"];
    var labels = ["Iron", "Calcium", "Magnesium", "Potassium", "Vitamin C", "Folate", "Vitamin A", "Vitamin E", "Vitamin D"];
    
    var colors = d3.scale.category20();
    var asterData = [];
    for (var i = 0; i < columns.length; i++)
    {
        var name = columns[i];
        var nutrientInfo = {};
        nutrientInfo.id = name;
        nutrientInfo.order = i;
        nutrientInfo.color = colors(i);
        nutrientInfo.score = row[name];
        nutrientInfo.cappedScore = Math.min(nutrientInfo.score, maxScore)
        nutrientInfo.weight = 1;
        nutrientInfo.width = nutrientInfo.weight;
        nutrientInfo.label = labels[i];
        asterData.push(nutrientInfo)
    }
    return asterData;
}
