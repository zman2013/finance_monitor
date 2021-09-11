// https://observablehq.com/@d3/grouped-bar-chart@87
export default function define(runtime, observer) {
  const main = runtime.module();
  const fileAttachments = new Map([["data.csv",new URL("./files/72eda648679b19ee477d3b70a598c977219672ab0c809bd42a0e15fb322894dc78dead25bd50ad1613de459d161dc6278b3add8d5f251547b393b10c4cf00a05",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], function(md){return(
md`# Grouped Bar Chart

Compare to a [stacked bar chart](/@d3/stacked-bar-chart).`
)});
  main.variable(observer("chart")).define("chart", ["d3","DOM","width","height","data","x0","groupKey","keys","x1","y","color","xAxis","yAxis","legend"], function(d3,DOM,width,height,data,x0,groupKey,keys,x1,y,color,xAxis,yAxis,legend)
{
  const svg = d3.select(DOM.svg(width, height));

  svg.append("g")
    .selectAll("g")
    .data(data)
    .join("g")
      .attr("transform", d => `translate(${x0(d[groupKey])},0)`)
    .selectAll("rect")
    .data(d => keys.map(key => ({key, value: d[key]})))
    .join("rect")
      .attr("x", d => x1(d.key))
      .attr("y", d => y(d.value))
      .attr("width", x1.bandwidth())
      .attr("height", d => y(0) - y(d.value))
      .attr("fill", d => color(d.key));

  svg.append("g")
      .call(xAxis);

  svg.append("g")
      .call(yAxis);

  svg.append("g")
      .call(legend);

  return svg.node();
}
);
  main.variable(observer("legend")).define("legend", ["width","color"], function(width,color){return(
svg => {
  const g = svg
      .attr("transform", `translate(${width},0)`)
      .attr("text-anchor", "end")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("g")
    .data(color.domain().slice().reverse())
    .join("g")
      .attr("transform", (d, i) => `translate(0,${i * 20})`);

  g.append("rect")
      .attr("x", -19)
      .attr("width", 19)
      .attr("height", 19)
      .attr("fill", color);

  g.append("text")
      .attr("x", -24)
      .attr("y", 9.5)
      .attr("dy", "0.35em")
      .text(d => d);
}
)});
  main.variable(observer("x0")).define("x0", ["d3","data","groupKey","margin","width"], function(d3,data,groupKey,margin,width){return(
d3.scaleBand()
    .domain(data.map(d => d[groupKey]))
    .rangeRound([margin.left, width - margin.right])
    .paddingInner(0.1)
)});
  main.variable(observer("x1")).define("x1", ["d3","keys","x0"], function(d3,keys,x0){return(
d3.scaleBand()
    .domain(keys)
    .rangeRound([0, x0.bandwidth()])
    .padding(0.05)
)});
  main.variable(observer("y")).define("y", ["d3","data","keys","height","margin"], function(d3,data,keys,height,margin){return(
d3.scaleLinear()
    .domain([0, d3.max(data, d => d3.max(keys, key => d[key]))]).nice()
    .rangeRound([height - margin.bottom, margin.top])
)});
  main.variable(observer("color")).define("color", ["d3"], function(d3){return(
d3.scaleOrdinal()
    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"])
)});
  main.variable(observer("xAxis")).define("xAxis", ["height","margin","d3","x0"], function(height,margin,d3,x0){return(
g => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x0).tickSizeOuter(0))
    .call(g => g.select(".domain").remove())
)});
  main.variable(observer("yAxis")).define("yAxis", ["margin","d3","y","data"], function(margin,d3,y,data){return(
g => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(null, "s"))
    .call(g => g.select(".domain").remove())
    .call(g => g.select(".tick:last-of-type text").clone()
        .attr("x", 3)
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .text(data.y))
)});
  main.variable(observer("data")).define("data", ["d3","FileAttachment"], async function(d3,FileAttachment){return(
Object.assign(d3.csvParse(await FileAttachment("data.csv").text(), d3.autoType), {y: "Population"})
)});
  main.variable(observer("groupKey")).define("groupKey", ["data"], function(data){return(
data.columns[0]
)});
  main.variable(observer("keys")).define("keys", ["data"], function(data){return(
data.columns.slice(1)
)});
  main.variable(observer("margin")).define("margin", function(){return(
{top: 10, right: 10, bottom: 20, left: 40}
)});
  main.variable(observer("height")).define("height", function(){return(
500
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@6")
)});
  return main;
}
