$(document).mousemove(function (e) {
    $("#tooltip").css({ left: e.pageX, top: e.pageY });
});
function sliceEntered(d) {

    d3.select("#genre")
        .html(
            '<strong>' + Math.round(d.value) + '</strong>&nbsp;@&nbsp;' + d.data.price +
            '&nbsp;*&nbsp;' + d.data.balance
        ); //this calls the data

    d3.select("#tooltip").classed("hidden", false); //this unhides the tooltip

};
function sliceExited(d) {

    d3.select("#genre")
        .html(''); //this calls the data

    d3.select("#tooltip").classed("hidden", true); //this unhides the tooltip

};
function renderSvg(data) {
    'use strict';

    var w = 800,                        //width
        h = 800,                            //height
        r = 200,                            //radius
        color = d3.scale.category20c();     //builtin range of colors

    var vis = d3.select("body")
        .append("svg:svg")              //create the SVG element inside the <body>
        .data([data])                   //associate our data with the document
        .attr("width", w)           //set the width and height of our visualization (these will be attributes of the <svg> tag
        .attr("height", h)
        .append("svg:g")                //make a group to hold our pie chart
        .attr("transform", "translate(" + r + "," + r + ")")    //move the center of the pie chart from 0, 0 to radius, radius
    var arc = d3.svg.arc()              //this will create <path> elements for us using arc data
        .outerRadius(r);
    var pie = d3.layout.pie()           //this will create arc data for us given a list of values
        .value(function (d) { return d.value; });    //we must tell it out to access the value of each element in our data array
    var arcs = vis.selectAll("g.slice")     //this selects all <g> elements with class slice (there aren't any yet)
        .data(pie)                          //associate the generated pie data (an array of arcs, each having startAngle, endAngle and value properties) 
        .enter()                            //this will create <g> elements for every "extra" data element that should be associated with a selection. The result is creating a <g> for every object in the data array
        .append("svg:g")                //create a group to hold each slice (we will have a <path> and a <text> element associated with each slice)
        .attr("class", "slice");    //allow us to style things in the slices (like text)
    arcs.append("svg:path")
        .attr("fill", function (d, i) { return color(i); }) //set the color for each slice to be chosen from the color function defined above
        .attr("d", arc)
        .on('mouseenter', sliceEntered)
        .on('mouseout', sliceExited);                                    //this creates the actual SVG path using the associated data (pie) with the arc drawing function
    arcs.append("svg:text")                                     //add a label to each slice
        .attr("transform", function (d) {                    //set the label's origin to the center of the arc
            //we have to make sure to set these before calling arc.centroid
            d.innerRadius = 0;
            d.outerRadius = r;
            return "translate(" + arc.centroid(d) + ")";        //this gives us a pair of coordinates like [50, 50]
        })
        .attr("text-anchor", "middle")                          //center the text on it's origin
        .text(function (d, i) { return data[i].label; })
        .on('mouseenter', sliceEntered)
        .on('mouseout', sliceExited);      //get the label from our original data array
}

function renderTotal(data) {
    var total = 0;
    data.forEach(element => {
        total += element.value;
    });
    d3.select('#total-value').html('<strong>Total:</strong><span>&nbsp;&nbsp;' + Math.round(total) + '</span>');
}

(function (d3) {

    // var data = [{ "value": 658.4735999999999, "label": "ETH" }, { "value": 2989.78015231071, "label": "EOS" }, { "value": 0.12497406, "label": "USD" }, { "value": 1451.488434434091, "label": "BTC" }, { "value": 1410.52938, "label": "OMG" }];
    d3.json('data', function(data){
        renderSvg(data);
        renderTotal(data);
    });

})(window.d3);