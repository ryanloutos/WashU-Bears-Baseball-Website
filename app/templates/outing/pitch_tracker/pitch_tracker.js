var pitches = [];

document.addEventListener('DOMContentLoaded', function() {
    // set up the field 
    var field = d3.select("#field")
    width = +field.attr('width')
    height = +field.attr('height')
    x1 = null
    y1 = null
    xf = null
    yf = null
    g1 = field.append('g').attr('transform', 'translate(0,95)')
    field.append("svg:image")
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', 435)
    .attr('height', 430)
    .attr('transform', 'translate(17,17)')
    .style('alignment-baseline', 'middle')
    .attr("xlink:href", "field.png")

    // set up the location tracker
    var svg = d3.select("#main")
    margin = {top: 10, right: 10, bottom: 10, left: 20}
    width = +svg.attr('width')
    height = +svg.attr('height')
    g = svg.append('g').attr('transform', null)
    svg.style('background-color', 'white').style('border', '1px solid black').style('margin', '10px')

    var xScale = d3.scaleLinear().range([width, 0]).domain([2,-2])
    var yScale = d3.scaleLinear().range([height, 0]).domain([0,4])
    var xScalef = d3.scaleLinear().range([width, 0]).domain([250,-250])
    var yScalef = d3.scaleLinear().range([height, 0]).domain([-100,400])

    function drawCircle(x, y) {
        svg.append('circle')
        .attr('class', 'click-circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', '8')
        .style('fill', 'red')
    }

    g.append('path')
    .attr('id', 'zone')
    .attr(
        'd', 'M ' + xScale(-.833) + ',' + yScale(1.75) + ' L ' + xScale(-.833) + ',' + yScale(3.4) + ' L ' +
        xScale(.833) + ',' + yScale(3.4) + ' L ' + xScale(.833) + ','  + yScale(1.75) + ' L ' + xScale(-.833) +  ',' + yScale(1.75)
        + 'M' + xScale(0) + ',' + yScale(0.2) + 'L' + xScale(-.843) + ',' + yScale(0.4) + 'L'  + xScale(-.833) + ',' + yScale(0.6) + 'L' +
        xScale(.833)+ ',' + yScale(0.6) + 'L' + xScale(.843) + ',' + yScale(0.4) + 'L' + xScale(0) + ',' + yScale(0.2)
    )
    .style('stroke', 'black')
    .style('fill', 'none')
    .style('stroke-width', 2)
    
    // move or place circle on chart
    svg.on('click', function() {
        svg.selectAll('circle').remove()
        svg.selectAll('text').remove()
        var local = d3.mouse(this)

        drawCircle(local[0], local[1])
        x1 = Math.round(xScale.invert(local[0])*100,3)/100
        y1 = Math.round(yScale.invert(local[1])*100,3)/100
        svg.append('text')
            .attr('y', yScale(3.8))
            .attr('x', xScale(1.8))
            .style('text-anchor', 'end')
            .style('font-size', '16px')
            .text('(' + Math.round(xScale.invert(local[0])*100)/100 + ', ' + y1 + ')');
        $('#btn').show
    });

    // move or place circle on chart
    field.on('click', function(){
        field.selectAll('circle').remove()
        var local = d3.mouse(this)
        field.append('circle')
        .attr('class', 'click-circle1')
        .attr('cx', local[0])
        .attr('cy', local[1])
        .attr('r', '8')
        .style('fill', 'navy')
        xf = Math.round(xScalef.invert(local[0])*100,3)/100
        yf = Math.round(yScalef.invert(local[1])*100,3)/100
        $('#ipTable').css('visibility', 'visible')
    });

    // gather data based on selections
    var pitch_type = ''
    $('.pitch-type').click(function(){
        $('.pitch-type').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        pitch_type = $(this).attr('value')
    })

    var hit_spot = 0
    $('.hit-spot-answer').click(function(){
        $('.hit-spot-answer').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        hit_spot = $(this).attr('value')
    })

    var traj = ''
    $('.traj-answer').click(function(){
        $('.traj-answer').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        $('#outDiv').css('visibility', 'visible')
        $('#fielderDiv').css('display', 'block')
        traj = $(this).attr('value')
    })

    var ab_result = ''
    $('.ip-at-bat-result').click(function(){
        $('.ip-at-bat-result').css('background-color', 'white').css('color', 'black')
        $(".ab-result-other").css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        ab_result = $(this).attr('value')
    })

    $('.strikeout-answer').click(function(){
        $('.strikeout-answer').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        ab_result = $(this).attr('value')
    })

    $('.bb-or-hbp-answer').click(function(){
        $('.bb-or-hbp-answer').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        ab_result = $(this).attr('value')
    })

    $(".ab-result-other").click(function(){
        $(".ab-result-other").css('background-color', 'white').css('color', 'black')
        $('.ip-at-bat-result').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        ab_result = $(this).attr('value')
    })

    var pitch_result = ''
    $('.prAnswer').click(function(){
        $('.prAnswer').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        $('#ab-result-other').css('display', 'block')
        if($(this).attr('value') == 'IP'){
            $('#fieldDiv').css('visibility', 'visible')
            $('#field').css('visibility', 'visible')
            $('#K').css('display', 'none')
            $('#KL').css('display', 'none')
            $('#bb-or-hbp').css('display', 'none')
            pitch_result = 'IP'
        }
        if($(this).attr('value') == 'F'){
            $('#fieldDiv').css('visibility', 'hidden')
            $('#ipTable').css('visibility', 'hidden')
            $('#K').css('display', 'none')
            $('#KL').css('display', 'none')
            $('#bb-or-hbp').css('display', 'none')
            pitch_result = 'F'
        }
        if($(this).attr('value') == 'B'){
            $('#bb-or-hbp').css('display', 'block')
            $('#K').css('display', 'none')
            $('#KL').css('display', 'none')
            $('#fieldDiv').css('visibility', 'hidden')
            $('#ipTable').css('visibility', 'hidden')
            pitch_result = 'B'
        }
        if($(this).attr('value') == 'SS'){
            $('#bb-or-hbp').css('display', 'none')
            $('#K').css('display', 'block')
            $('#KL').css('display', 'none')
            $('#fieldDiv').css('visibility', 'hidden')
            $('#ipTable').css('visibility', 'hidden')
            pitch_result = $(this).attr('value')
        }
        if($(this).attr('value') == 'CS'){
            $('#bb-or-hbp').css('display', 'none')
            $('#K').css('display', 'none')
            $('#KL').css('display', 'block')
            $('#fieldDiv').css('visibility', 'hidden')
            $('#ipTable').css('visibility', 'hidden')
            pitch_result = $(this).attr('value')
        }
    })

    var lead_runner = ''
    $('.lead-runner').click(function(){
        $('.lead-runner').css('background-color', 'white').css('color', 'black')
        $(this).css('background-color', 'navy').css('color', 'white')
        lead_runner = $(this).attr('value')
    })

    $('#Add').click(function(){
        // get some more pitch values
        inning = $('#inning').val()
        fielder = $('#select-fielder').val()
        batter_id = $('#select-batter').val()
        velocity = $('#velocity-input').val()
        time_to_plate = $('#time-to-plate-input').val()

        // set pitch data
        pitchData = {
            'batter_id': batter_id, 'velocity': velocity, 'lead_runner': lead_runner,
            'time_to_plate': time_to_plate, 'pitch_type': pitch_type, 'pitch_result': pitch_result, 
            'loc_x': x1, 'loc_y': y1, 'hit_spot': hit_spot, 'ab_result': ab_result, 
            'traj': traj, 'fielder': fielder, 'spray_x': xf*1.3, 'spray_y': yf*1.3,
            'inning': inning
        }

        pitches.push(pitchData)

        addPitchToTable(pitches)
        // clear some of the inputs
        $('#select-fielder').val('')
        $('#outSelect').val('')
        $('#velocity-input').val('')
        $('#time-to-plate-input').val('')

        // clear some of the variables set above
        pitch_type, traj, ab_result, pitch_result  =  ""
        lead_runner, fielder, velocity, time_to_plate = ""
        hit_spot = 0
        x1, y1, xf, yf = null

        // reset buttons or values that were clicked
        $('div').not('.lead-runner').not('#Add').css('background-color', 'white').css('color', 'black')
        
        // hide certain buttons
        $('#ipTable').css('visibility', 'hidden')
        $('#field').css('visibility', 'hidden')
        $('#outDiv').css('visibility', 'hidden')
        $('#fielderDiv').css('display', 'none')
        $('.strikeout').css('display', 'none')
        $('#bb-or-hbp').css('display', 'none')
        $('.strikeout-answer').css('background-color', 'white').css('color', 'black')
        $('.strikeout-no').css('background-color', 'navy').css('color', 'white')
        $('#hit-spot-no').css('background-color', 'navy').css('color', 'white')

        // remove circles and text from diagrams
        svg.selectAll('circle').remove()
        field.selectAll('circle').remove()
        svg.selectAll('text').remove()

    })
});

function addPitchToTable(pitches) {
    // empty table
    pitch_table = $("#pitch-table > tbody");
    pitch_table.empty();

    // add headers to table
    new_row = pitch_table.append('<tr></tr>');
    new_row.append("<th>No.</th>");
    new_row.append("<th>Batter</th>");
    new_row.append("<th>Velo</th>");
    new_row.append("<th>Lead RNR</th>");
    new_row.append("<th>Time to Plate</th>");
    new_row.append("<th>Pitch Type</th>");
    new_row.append("<th>Pitch Result</th>");
    new_row.append("<th>Hit Spot</th>");
    new_row.append("<th>AB Result</th>");
    new_row.append("<th>Traj</th>");
    new_row.append("<th>Fielder</th>");
    new_row.append("<th>Inning</th>");

    // add all pitches
    for (let i=0; i<pitches.length; i++) {
        new_row = pitch_table.append('<tr></tr>');
        new_row.append("<td>"+(i+1)+"</td>")
        new_row.append("<td>"+pitches[i]["batter_id"]+"</td>")
        new_row.append("<td>"+pitches[i]["velocity"]+"</td>")
        new_row.append("<td>"+pitches[i]["lead_runner"]+"</td>")
        new_row.append("<td>"+pitches[i]["time_to_plate"]+"</td>")
        new_row.append("<td>"+pitches[i]["pitch_type"]+"</td>")
        new_row.append("<td>"+pitches[i]["pitch_result"]+"</td>")
        new_row.append("<td>"+pitches[i]["hit_spot"]+"</td>")
        new_row.append("<td>"+pitches[i]["ab_result"]+"</td>")
        new_row.append("<td>"+pitches[i]["traj"]+"</td>")
        new_row.append("<td>"+pitches[i]["fielder"]+"</td>")
        new_row.append("<td>"+pitches[i]["inning"]+"</td>")
    }
}
