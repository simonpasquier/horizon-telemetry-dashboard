// Draw all metric graphs for all instances of the Telemetry overview page
function draw_graphs(selector, proxy_url, graph_height, graph_width) {

  // loop over every instance
  $("body").find(selector).each(function (i, el){

    var instance_id = el.attributes["data-object-id"];
    if (undefined == instance_id) {
        console.debug("No instances");
        return;
    }
    // jquery doesn't support dot in selector
    instance_id = instance_id.value.replace(/\./g,'\\.');

    // loop over every graph
    $(el).find("td div").each(function(i, el) {
        metric = $(el).attr('metric');
        if (undefined != metric) {
            var adjusted_height = graph_height
            if (metric == "virt_cpu_time") {
                adjusted_height = 2 * graph_height
            }
            draw_graph($(el).attr('id'), instance_id, metric, proxy_url, adjusted_height, graph_width);
        } else {
            console.warn("Attribute 'metric' not found!")
        }
      });
  });
}

// Draw the graph for the given instance and metric
function draw_graph(graph_id, instance_id, metric, proxy_url, graph_height, graph_width) {
    var context = get_context(graph_width),
        horizon = context.horizon().height(graph_height);

    // hide the title
    horizon.title(function(d){return ""});

    // create the Cubism metric object associated to the graph
    //
    // start and end are Date objects
    // step is an interval in milliseconds
    // callback is the result function which expects 2 arguments:
    //   - an error message, it should be null if the result is ok
    //   - an array of values to draw
    proxy_metric = context.metric(function(start, end, step, callback) {
      d3.json(proxy_url
            + "?metric=" + encodeURI(metric)
            + "&instance_id=" + encodeURI(instance_id)
            + "&start=" + Math.floor(start / 1e3)
            + "&end=" + Math.floor(end / 1e3)
            + "&interval=" + (step / 1e3),
        function(data) {
            if (!data) {
                return callback(new Error("unable to load " + metric));
            }
            callback(null, data);
        }
      );
    }, instance_id + '_' + metric);

    d3.select('#'+graph_id)
      .selectAll(".horizon")
      .data([proxy_metric])
      .enter()
      .insert("div", ".bottom")        // Insert the graph in a div. Turn the div into
      .attr("class", "horizon")        // a horizon graph and format to 2 decimals places.
      .call(horizon);
}

function get_context(graph_width) {
    var context = cubism.context()
                        .step(1 * 60 * 1000) // 1-minute interval
                        .size(graph_width); // Number of data points
                        //.stop();   // Fetching from a static data source; don't update values
    return context;
}


function draw_axis(id, from, to, graph_width){
    // simple helper which draw graph axis in header
    //
    // id, the main selector which is usually the id of a table
    // from and to, integers identifying the range of columns where the axis is rendered

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
