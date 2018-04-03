(function () {
  d3.soccerfield = function() {
	var field_length  = 9000,
	    field_width   = 6000,
	    field_border  = 700,
	    field_color   = '#54dc54',
	    line_width    = 50,
	    line_color    = '#ffffff',
	    penalty_area_length = 600,
	    penalty_area_width  = 2200,
	    penalty_cross_distance = 1300,
	    penalty_cross_size = 100,
	    center_circle_radius = 1500 / 2,
	    goal_width = 1600,
	    goal_length = 500,
	    scale = 0.1
    ;

    soccerfield.scale = function(s) {
    	if (!arguments.length) return scale;
      scale = s;
      return soccerfield;
    };

    soccerfield.width = function(l) {
    	if (!arguments.length) return field_length;
    	field_length = l;
    	return soccerfield;
    };

    soccerfield.height = function(w) {
    	if (!arguments.length) return field_width;
    	field_width = w;
    	return soccerfield;
    };

    soccerfield.fieldColor = function(c) {
    	if (!arguments.length) return field_color;
    	field_color = c;
    	return soccerfield;
    };

    soccerfield.lineColor = function(c) {
    	if (!arguments.length) return line_color;
    	line_color = c;
    	return soccerfield;
    };

    soccerfield.margin = function(m) {
    	if (!arguments.length) return field_border;
    	field_border = m;
    	return soccerfield;
    };

    function soccerfield(selection) {
		var holder = selection
		      .append("svg")           // append an SVG element to the div
		      .attr("width", (field_length + 2 * field_border)*scale)
		      .attr("height", (field_width + 2 * field_border)*scale);

		// draw a rectangle - field
		holder.append("rect")        // attach a rectangle
		    .attr("x", 0)         // position the left of the rectangle
		    .attr("y", 0)          // position the top of the rectangle
		    .attr("height", (field_width + 2 * field_border)*scale)    // set the height
		    .attr("width", (field_length + 2 * field_border)*scale)    // set the width
		    .style("stroke-width", 0)    // set the stroke width
		    // .style("stroke", "#001400")    // set the line colour
		    .style("fill", field_color);    // set the fill colour 

		// draw a rectangle - field border
		holder.append("rect")        // attach a rectangle
		    .attr("x", field_border * scale)         // position the left of the rectangle
		    .attr("y", field_border * scale)          // position the top of the rectangle
		    .attr("height", field_width * scale)    // set the height
		    .attr("width", field_length * scale)    // set the width
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line colour
		    .style("fill", 'transparent');    // set the fill colour 

		// draw a rectangle - field penalty box (left)
		holder.append("rect")        // attach a rectangle
		    .attr("x", field_border * scale)         // position the left of the rectangle
		    .attr("y", (field_border + field_width/2 - penalty_area_width/2) * scale)          // position the top of the rectangle
		    .attr("height", penalty_area_width * scale)    // set the height
		    .attr("width", penalty_area_length * scale)    // set the width
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line colour
		    .style("fill", 'transparent');    // set the fill colour 

		// draw a rectangle - field penalty box (right)
		holder.append("rect")        // attach a rectangle
		    .attr("x", (field_border + field_length - penalty_area_length) * scale)         // position the left of the rectangle
		    .attr("y", (field_border + field_width/2 - penalty_area_width/2) * scale)          // position the top of the rectangle
		    .attr("height", penalty_area_width * scale)    // set the height
		    .attr("width", penalty_area_length * scale)    // set the width
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line colour
		    .style("fill", 'transparent');    // set the fill colour 

		// draw center line
		holder.append("line")
		    .attr("x1", (field_border + field_length/2) * scale)
		    .attr("y1", field_border * scale)
		    .attr("x2", (field_border + field_length/2) * scale)
		    .attr("y2", (field_border + field_width) * scale)
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line color

		// draw the center circle
		holder.append("circle")        // attach a circle
		    .attr("cx", (field_border + field_length/2) * scale)           // position the x-centre
		    .attr("cy", (field_border + field_width/2) * scale)           // position the y-centre
		    .attr("r", center_circle_radius * scale)             // set the radius
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line color
		    .style("fill", "transparent");     // set the fill colour
		    ;

		// draw penalty cross (left)
		holder.append("circle")        // attach a circle
		    .attr("cx", (field_border + penalty_cross_distance - penalty_cross_size/2) * scale)           // position the x-centre
		    .attr("cy", (field_border + field_width / 2) * scale)           // position the y-centre
		    .attr("r", penalty_cross_size * scale)             // set the radius
		    .style("fill", "white");     // set the fill colour

		// draw penalty cross (right)
		holder.append("circle")        // attach a circle
		    .attr("cx", (field_border + field_length - penalty_cross_distance + penalty_cross_size/2) * scale)           // position the x-centre
		    .attr("cy", (field_border + field_width / 2) * scale)           // position the y-centre
		    .attr("r", penalty_cross_size * scale)             // set the radius
		    .style("fill", "white");     // set the fill colour

		// draw goal (left)
		holder.append("rect")        // attach a rectangle
		    .attr("x", (field_border - goal_length) * scale)         // position the left of the rectangle
		    .attr("y", (field_border + field_width/2 - goal_width/2) * scale)          // position the top of the rectangle
		    .attr("height", goal_width * scale)    // set the height
		    .attr("width", goal_length * scale)    // set the width
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line colour
		    .style("fill", 'transparent');    // set the fill colour 

		// draw goal (left)
		holder.append("rect")        // attach a rectangle
		    .attr("x", (field_border + field_length) * scale)         // position the left of the rectangle
		    .attr("y", (field_border + field_width/2 - goal_width/2) * scale)          // position the top of the rectangle
		    .attr("height", goal_width * scale)    // set the height
		    .attr("width", goal_length * scale)    // set the width
		    .style("stroke-width", line_width * scale)    // set the stroke width
		    .style("stroke", line_color)    // set the line colour
		    .style("fill", 'transparent');    // set the fill colour 
    }
    return soccerfield;
  };
})();