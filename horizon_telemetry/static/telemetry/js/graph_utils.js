function draw_graphs(selector, graphite_endpoint, graph_height, graph_width) {

  $("body").find(selector).each(function (i, el){

    var id = el.attributes["data-object-id"];
    if (undefined == id) {
        console.debug("No instances");
        return;
    }

    // jquery doesn't support dot in selector
    id = id.value.replace(/\./g,'\\.');
    $(el).find("td div").each(function(i, el) {
        type = $(el).attr('data-name');
        if (undefined != type) {
            if (type =="cpu_util") {
                // double cpu_util graph height
                var adjusted_height = 2 * graph_height
                draw_graph(id, type, graphite_endpoint, adjusted_height, graph_width);
            } else {
                var adjusted_height = graph_height
                draw_graph(id, type, graphite_endpoint, adjusted_height, graph_width);
            }
        }
      });
  });
}


function draw_graph(id, type, graphite_endpoint, graph_height, graph_width) {
    /* main function for rendering graphs */

    horizon = init_cubism(graphite_endpoint, graph_height, graph_width);

    var graph_id = "#graph_" + type + "_" + id;
    metric = $(graph_id).attr('data-metric');

    d3.select(graph_id)
      .selectAll(".horizon")
      .data([metric])
      .enter()
      .insert("div", ".bottom")        // Insert the graph in a div. Turn the div into
      .attr("class", "horizon")        // a horizon graph and format to 2 decimals places.
      .call(horizon);

}

function get_context(graph_width) {
    var context = cubism.context()
                        .step(1 * 60 * 1000) // 1 minute
                        .size(graph_width); // Number of data points
                        //.stop();   // Fetching from a static data source; don't update values
    return context;
}


function get_graphite(graphite_endpoint, graph_width) {
    return get_context(graph_width).graphite(graphite_endpoint);
}


function init_cubism(graphite_endpoint, graph_height, graph_width){
    /*
      inicialization of horizon-cubism
    */

    var context = get_context(graph_width),
        graphite = context.graphite = get_graphite(graphite_endpoint, graph_width),
        horizon = context.horizon();

    horizon = horizon.metric(graphite.metric).height(graph_height);//.shift( - 0 * 24 * 60 * 60 * 1000 );

    // hide metric name
    horizon.title(function(d){return ""});

    return horizon;
}


function draw_axis(id, from, to, graph_width){
    /* simple helper which draw graph axis in header
    you must prive main select which is usually id of table and next
    from-to is integers which specifies columns where wi will rener axis
    */
    // draw axis :D
    for (i = from; i < to; i++) {
      d3.select("#" + id + " > thead > tr:nth-child(2) > th:nth-child("+ i +")")                 // Select the div on which we want to act
        .selectAll(".axis")              // This is a standard D3 mechanism to bind data
        .data(["top"])                   // to a graph. In this case we're binding the axes
        .enter()                         // "top" and "bottom". Create two divs and give them
        .append("div")                   // the classes top axis and bottom axis respectively.
        .attr("class", function(d) {
          return d + " axis";
        })
        .each(function(d) {              // For each of these axes, draw the axes with 4
          d3.select(this)              // intervals and place them in their proper places.
            .call(get_context(graph_width).axis()       // 4 ticks gives us an hourly axis.
            .ticks(4).orient(d));
        });
    }

}
