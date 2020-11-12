/**
 * NEW JS FILE SO THAT BROWSERS WILL UPDATE CACHE FOR CHANGES
 */

/**
 * Zone constants based on scale defined in class strikezone
 */
var zone_constants = {
    //x plane coords
    x_left: -2,
    x_zone_left: -0.833,
    x_zone_left_third: -0.277,
    x_zone_middle: 0,
    x_zone_right_third: 0.277,
    x_zone_right: 0.833,
    x_right: 2,
    //y plane coords
    y_top: 4,
    y_zone_top: 3.4,
    y_zone_upper_third: 2.85,
    y_zone_middle: 2.575,
    y_zone_lower_third: 2.3,
    y_zone_bottom: 1.75,
    y_bottom: 0
}

/** Class representing a d3 strikezone as an object*/
class strikezone {

    /** 
     * Create a strikezone svg in the div_id provided with width and height provided. 
     * 
     * @param {String} div_id - The id of the div to add strikezone svg to
     * @param {Number} width - The width of the strikezone svg
     * @param {Number} height - The height of the strikezone svg
     * 
     */

    constructor(div_id, width=457, height=457){

        this.width = width;
        this.height = height;
        //setup pitch colors array for drawing circles
        this.pitch_colors = {
            "1": 'rgb(230, 25, 75)',
            "2": 'rgb(0, 130, 200)',
            "3": 'rgb(0, 200, 0)',
            "4": 'rgb(200, 200, 0)',
            "5": 'rgb(0, 200, 200)',
            "7": 'rgb(255, 128, 0)'
        };

        //create svg
        this.zone = d3.select("#"+div_id)
            .append("svg")
                .attr("width", this.width)
                .attr("height", this.height)
                .attr("class", "plot")
                .attr("id", "strikezone")
        
        //create graphics part of svg
        this.g = this.zone.append("g")
            .attr("tramsform", null);

        //Setup zone background ppearance
        this.zone.style('background-color', 'white')
            .style('border', '1px solid black')
            .style('margin', '10px');

        //setup strikezone scale variables
        this.xScale = d3.scaleLinear().range([this.width, 0]).domain([2, -2]);
        this.yScale = d3.scaleLinear().range([this.height, 0]).domain([0, 4]);

        //draw the appearance of the strikezone
        this.g.append('path')
            .attr('id', 'zone')
            .attr(
                'd',
                //draw zone box
                'M ' + this.xScale(-.833) + ',' + this.yScale(1.75) +   //bottom left
                ' L ' + this.xScale(-.833) + ',' + this.yScale(3.4) +   //top left
                ' L ' + this.xScale(.833) + ',' + this.yScale(3.4) +    //top right
                ' L ' + this.xScale(.833) + ',' + this.yScale(1.75) +   //bottom right
                ' L ' + this.xScale(-.833) + ',' + this.yScale(1.75) +  //bottom left
                //draw home plate
                'M' + this.xScale(0) + ',' + this.yScale(0.2) +
                'L' + this.xScale(-.843) + ',' + this.yScale(0.4) +
                'L' + this.xScale(-.833) + ',' + this.yScale(0.6) +
                'L' + this.xScale(.833) + ',' + this.yScale(0.6) +
                'L' + this.xScale(.843) + ',' + this.yScale(0.4) +
                'L' + this.xScale(0) + ',' + this.yScale(0.2)
            )
            .style('stroke', 'black')
            .style('fill', 'none')
            .style('stroke-width', 2);
    }

    /**
     * Draws a circle on the strikezone svg at point (x,y) with respect 
     * to svg as if (0,0) were in center
     * 
     * @param {Number} x - x coordinate of circle
     * @param {Number} y - y coordinate
     * @param {String} pitch_type - type of pitch to draw for circle color
     * @param {String} pitch_num - number of pitch to place on circle
     */
    drawCircle(x, y, pitch_type=null, pitch_num=null) {

        //add circle to the zone svg
        let circle = this.zone.append("circle")
            .attr("class", "zone-pitch-circle")
            .attr("cx", this.xScale(x))
            .attr("cy", this.yScale(y))
            .attr('r', '8');

            if(pitch_type != null){
                circle.style("fill", this.pitch_colors[pitch_type]);
            } else {
                circle.style("fill", "black");
            }

        //add pitch_type to circle
        let text = this.zone.append("text")
            .attr("class", "zone-pitch-text")
            .attr("x", this.xScale(x))
            .attr("y", this.yScale(y))
            .attr("dy", 5)
            .attr("font-size", "9pt")
            .attr("text-anchor", "middle")
            .attr("fill", "black");

        if(pitch_num != null){
            text.text(pitch_num);
        }
    }
    
    drawOpaqueCircle(x, y, pitch_type=null) {

        //add circle to the zone svg
        let circle = this.zone.append("circle")
            .attr("class", "zone-pitch-circle")
            .attr("cx", this.xScale(x))
            .attr("cy", this.yScale(y))
            .attr('r', '8')
            .style("opacity", 0.5);

            if(pitch_type != null){
                circle.style("fill", this.pitch_colors[pitch_type]);
            } else {
                circle.style("fill", "black");
            }
    }

    /**
     * Delete all existing circles and labels from strikezone svg
     */
    removeCircles(){
        this.zone.selectAll('zone-pitch-circle').remove();
        this.zone.selectAll('zone-pitch-text').remove();
    }

    /**
     * Highlights areas of the strikezone based on user input. Takes input
     * of an array of (x, y) pairs. Each pair given will highlight that
     * area of the zone.
     * @param {Array} coords Array of (x,y) coordinate pairs correlating to zone
     *      regions
     * 
     * Coordinate plane for zone highlighting:
     * 
     *       x   0     1  2  3     4
     *       __ __ __ __ __ __ __ __ __
     *     y|        |  |  |  |        |
     *     0|        |  |  |  |        |
     *      |________|__|__|__|________|
     *     1|________|__|__|__|________|
     *     2|________|__|__|__|________|
     *     3|________|__|__|__|________|
     *      |        |  |  |  |        |
     *     4|        |  |  |  |        |
     *      |________|__|__|__|________|
     * 
     */
    highlightZonesDynamically(coords){

        if(!Array.isArray(coords)){
            //Passed parameter is not an array... Do nothing
            return;
        }

        let index = 0;
        while(index < coords.length){
            let pair = coords[index];
            let x = pair[0];
            let y = pair[1];

            let dx = -2, dy = 4;

            let width = 0, height = 0;

            // zone width
            switch(x){
                case 4:
                    dx+=2.833;
                case 0:
                    width = this.xScale(-0.833);
                    break;

                case 3:
                    dx+=0.556
                case 2:
                    dx+=0.556
                case 1:
                    dx+=1.167
                    width = this.xScale(-1.444);
                    break;

                default:
                    width = 0;
                    break;
            }

            // zone height
            switch(y){
                case 0:
                    dy = 4;
                    height = this.yScale(3.4);
                    break;

                case 4:
                    dy = 1.75;
                    height = this.yScale(1.75);
                    break;

                case 3:
                    dy -= 0.55;
                case 2:
                    dy -= 0.55;
                case 1:
                    dy -= 0.6;
                    height = this.yScale(3.45)
                    break;

                default:
                    width = 0;
                    break;
            }

            this.zone.append("rect")
                .attr("id", "".concat("zone-highlight-", x, "-", y))
                .attr("x", this.xScale(dx))
                .attr("y", this.yScale(dy))
                .attr("width", width)
                .attr("height", height)
                .attr("opacity", "0.5")
                .attr("fill", "MidnightBlue");

            index++;
        }
    }

    /**
     * Place a semi-transparent screen over the upper half of the zone
     */
    highlightUpperHalf(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(-2))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(4))
            .attr("height", this.yScale(2.575))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }

    highlightLowerHalf(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(-2))
            .attr("y", this.yScale(2.57))
            .attr("width", this.xScale(4))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }

    highlight3bSide(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(-2))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(-0.833))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }

    highlightInnerThird(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(-0.833))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(-1.444))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");

    }
    highlightMiddleThird(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(-0.277))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(-1.444))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }
    highlightOuterThird(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(0.277))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(-1.444))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }
    highlight1bSide(){
        let rect = this.zone.append("rect")
            .attr("x", this.xScale(0.833))
            .attr("y", this.yScale(4))
            .attr("width", this.xScale(-0.8))
            .attr("height", this.yScale(0))
            .attr("opacity", "0.5")
            .attr("fill", "MidnightBlue");
    }

    highlightDensityRegion(coords){
        if (!Array.isArray(coords)) {
            //Passed parameter is not an array... Do nothing
            return;
        }
        
        
        let density_data = d3.contourDensity()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScale(d[1]))
            .size([this.xScale(2), this.yScale(0)])
            .bandwidth(5)
            (coords);
        
        var color = d3.scaleLinear()
            .domain([0, 0.1]) // Points per square pixel.
            .range(["white", "#69b3a2"]);
        console.log(density_data);
            
        this.zone.insert("g", "g2")
        .selectAll("path")
            .data(density_data)
            .enter().append("path")
                .attr("d", d3.geoPath())
                .attr("fill", function (d) {return color(d.value);})
    }
}

class strikezone_legend {

    constructor(div_id, width=457, height=70){
        //setup pitch colors array for drawing circles
        this.legend_items = {
            "1": 'rgb(230, 25, 75)',
            "2": 'rgb(0, 130, 200)',
            "3": 'rgb(0, 200, 0)',
            "4": 'rgb(200, 200, 0)',
            "5": 'rgb(0, 200, 200)',
            "7": 'rgb(255, 128, 0)'
        };

        //add the svg to the div provided
        this.legend = d3.select("#"+div_id)
            .append("svg")
                .attr("id", "zone-legend")
                .attr("width", width)
                .attr("height", height)
                .attr("align", "center")
                .attr("class", "chart")
                .style("margin", "10px");

        //setup graphics element of svg
        this.g = this.legend
            .append('g')
                .attr("transform", null);

        this.g.append("text")
            .attr("class", "legend-text")
            .attr("font-size", "14pt")
            .attr("fill", "black")
            .attr("x", 10)
            .attr("y", 50)
            .text("Pitch Types:");

        //make pitch individual circles
        let x_index = 0;
        for(var color in this.legend_items){
            //setup legend circle
            this.g.append('circle')
                .attr('class', 'legend-circle')
                .attr('r', '8')
                .attr('cy', 50)
                .attr('cx', 145 + x_index)
                .attr('fill', this.legend_items[color]);
            
            // setup legend text
           this.g.append('text')
                .attr('class', 'legend-text')
                .attr('font-size', "9pt")
                .attr('fill', 'black')
                .attr('y', 50)
                .attr('dy', 5)
                .attr('x', 145 + x_index)
                .attr('text-anchor', 'middle')
                .text(color);

            x_index += 20;
        }
    }
}

/**
 * Class representing a d3_dynamic scouting strikezone whic inherits
 * from the d3_strikezone.
 */
class dynamic_scouting_strikezone extends strikezone{

    /*
    Inherited Variables:
    this.width
    this.height
    this.pitch_colors
    this.zone
    this.g
    this.xScale
    this.yScale
    */ 

    /**
     * 
     * @param {String} div_id The id of the div to create a strikezone in
     * @param {Number} width  Width of the strikezone svg
     * @param {Number} height Height of the strikeone svg
     * 
     * Creates an object of type dynamic_scouting_strikezone, which extends
     * from the strikezone class. The additions include guidelines for the 
     * different regions of the strikezone, stat calculations, and click
     * based dynamic highlighting.
     */
    constructor(div_id, stats_table_div, data_obj={}, width = 457, height = 457){
        super(div_id, width, height);

        this.stats_table_div = d3.select("#".concat(stats_table_div));
        //Creates entire stats table associated with zone, in the div provided
        this.stats_table_div.html(`
            <table class="table">
                <thead>
                    <tr class="table-headers">
                        <th>Pitch</th>
                        <th>Num</th>
                        <th>Swing %</th>
                        <th>Whiff %</th>
                        <th>Foul %</th>
                        <th>In Play %</th>
                        <th>In Play Out %</th>
                        <th>In Play Safe %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr id="FB-data-row">
                        <td class="pitch_type">FB</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                    <tr id="SM-data-row">
                        <td class="pitch_type">2S</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                    <tr id="CB-data-row">
                        <td class="pitch_type">CB</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                    <tr id="SL-data-row">
                        <td class="pitch_type">SL</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                    <tr id="CH-data-row">
                        <td class="pitch_type">CH</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                    <tr id="CT-data-row">
                        <td class="pitch_type">CT</td>
                        <td class="pitch_count">0</td>
                        <td class="swing_rate">0</td>
                        <td class="whiff_rate">0</td>
                        <td class="foul_rate">0</td>
                        <td class="in_play_rate">0</td>
                        <td class="in_play_out_rate">0</td>
                        <td class="in_play_safe_rate">0</td>
                    </tr>
                </tbody>
            </table>
        `);

        //Add guidelines to base appearance of strikezone
        this.g.append('path')
            .attr('id', "zone-divisions")
            .attr(
                'd',
                //draw vertical zone guidelines
                'M ' + this.xScale(zone_constants.x_zone_left) + ', ' + this.yScale(zone_constants.y_top) + ' ' + 
                'L ' + this.xScale(zone_constants.x_zone_left) + ', ' + this.yScale(zone_constants.y_bottom) + ' ' +
                'M ' + this.xScale(zone_constants.x_zone_left_third ) + ', ' + this.yScale(zone_constants.y_top) + ' ' + 
                'L ' + this.xScale(zone_constants.x_zone_left_third) + ', ' + this.yScale(zone_constants.y_bottom) + ' ' +
                'M ' + this.xScale(zone_constants.x_zone_right_third) + ', ' + this.yScale(zone_constants.y_top) + ' ' + 
                'L ' + this.xScale(zone_constants.x_zone_right_third) + ', ' + this.yScale(zone_constants.y_bottom) + ' ' +
                'M ' + this.xScale(zone_constants.x_zone_right) + ', ' + this.yScale(zone_constants.y_top) + ' ' + 
                'L ' + this.xScale(zone_constants.x_zone_right) + ', ' + this.yScale(zone_constants.y_bottom) + ' ' +
                //draw horizontal zone guidelines
                'M ' + this.xScale(zone_constants.x_left) + ', ' + this.yScale(zone_constants.y_zone_top) + ' ' + 
                'L ' + this.xScale(zone_constants.x_right) + ', ' + this.yScale(zone_constants.y_zone_top) + ' ' +
                'M ' + this.xScale(zone_constants.x_left) + ', ' + this.yScale(zone_constants.y_zone_upper_third) + ' ' + 
                'L ' + this.xScale(zone_constants.x_right) + ', ' + this.yScale(zone_constants.y_zone_upper_third) + ' ' +
                'M ' + this.xScale(zone_constants.x_left) + ', ' + this.yScale(zone_constants.y_zone_lower_third) + ' ' + 
                'L ' + this.xScale(zone_constants.x_right) + ', ' + this.yScale(zone_constants.y_zone_lower_third) + ' ' +
                'M ' + this.xScale(zone_constants.x_left) + ', ' + this.yScale(zone_constants.y_zone_bottom) + ' ' + 
                'L ' + this.xScale(zone_constants.x_right) + ', ' + this.yScale(zone_constants.y_zone_bottom) + ' '
            )
            .style('stroke', 'grey')
            .style('fill', 'none')
            .style('stroke-width', 0.5);


        //Setup the click highlighting of the regions of the zone
        this.zone_highlight_bools = {    //state checking for zones
            "00": false, "01": false, "02": false, "03": false, "04": false,
            "10": false, "11": false, "12": false, "13": false, "14": false,
            "20": false, "21": false, "22": false, "23": false, "24": false,
            "30": false, "31": false, "32": false, "33": false, "34": false,
            "40": false, "41": false, "42": false, "43": false, "44": false
        };
        var self = this;    //used so that in access class values and functions from within below func
        this.zone.on('click', function(){
            var mouse = d3.mouse(this);
            let x_coord, y_coord;

            //get x grid region
            if(mouse[0] < self.xScale(zone_constants.x_zone_left)){
                //left of zone
                x_coord = 0;
            }
            else if(mouse[0] < self.xScale(zone_constants.x_zone_left_third)){
                //left third of zone
                x_coord = 1;
            }
            else if(mouse[0] < self.xScale(zone_constants.x_zone_right_third)){
                //middle third of zone
                x_coord = 2;
            }
            else if(mouse[0] < self.xScale(zone_constants.x_zone_right)){
                //right third of zone
                x_coord = 3;
            }
            else{
                //right of strikezone
                x_coord = 4;
            }

            //get y grid region
            if(mouse[1] < self.yScale(zone_constants.y_zone_top)){
                //above zone region
                y_coord = 0;
            }
            else if(mouse[1] < self.yScale(zone_constants.y_zone_upper_third)){
                //above zone region
                y_coord = 1;
            }
            else if(mouse[1] < self.yScale(zone_constants.y_zone_lower_third)){
                //above zone region
                y_coord = 2;
            }
            else if(mouse[1] < self.yScale(zone_constants.y_zone_bottom)){
                //above zone region
                y_coord = 3;
            }
            else {
                //above zone region
                y_coord = 4;
            }

            //unhighlights the clicked zone
            if(self.zone_highlight_bools["".concat(x_coord, y_coord)]){
                self.zone.select("#".concat("zone-highlight-", x_coord, "-", y_coord)).remove();
            } 
            //Highlights the clicked zone
            else{
                self.highlightZonesDynamically([[x_coord, y_coord]]);
            }
            //switch bool and calc new values
            self.zone_highlight_bools["".concat(x_coord, y_coord)] = !self.zone_highlight_bools["".concat(x_coord, y_coord)];
            self.calcStatValue()
        });

        //to be filled in by function
        this.pitches_data = data_obj;
    }

    /**
     * Gives an opportinity to pass a dataset to the class after
     * construction.
     * 
     * @param {Object} data_obj Object to be given to the class' data
     */
    provideData(data_obj){
        this.pitches_data = data_obj;
    }

    /**
     * Creates a statistical summary for all currently highlighted zones, and
     * displays all of the stats in the table of the provided id.
     */
    calcStatValue(){

        //hold the totals for each stat type for the current state
        var temp_totals = {
            "FB": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0},
            "CB": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0},
            "SL": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0},
            "CH": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0},
            "SM": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0},
            "CT": {"count": 0, "swing_rate": 0, "whiff_rate": 0, "foul_rate": 0, "in_play_rate": 0, "in_play_out_rate" :0, "in_play_safe_rate": 0}
        };

        //process through selected zones
        console.log("Adding values to control var");
        for(let coord in this.zone_highlight_bools){
            if(this.zone_highlight_bools[coord]){
                for(let stat in this.pitches_data[coord]){
                    for(let p_type in this.pitches_data[coord][stat]){
                        temp_totals[p_type][stat] += this.pitches_data[coord][stat][p_type];
                    }
                }
            }
        }

        //do calculations for accrued data
        console.log("Performing Stat Calculations");
        for(let p_type in temp_totals){
            temp_totals[p_type]["whiff_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["whiff_rate"], temp_totals[p_type]["swing_rate"]));

            temp_totals[p_type]["foul_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["foul_rate"], temp_totals[p_type]["swing_rate"]));

            temp_totals[p_type]["in_play_out_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["in_play_out_rate"], temp_totals[p_type]["in_play_rate"]));

            temp_totals[p_type]["in_play_safe_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["in_play_safe_rate"], temp_totals[p_type]["in_play_rate"]));

            temp_totals[p_type]["in_play_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["in_play_rate"], temp_totals[p_type]["swing_rate"]));

            temp_totals[p_type]["swing_rate"] = this.percentage(this.zero_division_handler(temp_totals[p_type]["swing_rate"], temp_totals[p_type]["count"]));
        }

        //place values in table
        console.log("Placing values in html");
        for (let p_type in temp_totals) {
            for (let stat in temp_totals[p_type]) {

                let stat_loc;
                if (stat == "count") {
                    stat_loc = document.getElementById("".concat(p_type, "-data-row")).getElementsByClassName("pitch_count")[0];
                } else {
                    stat_loc = document.getElementById("".concat(p_type, "-data-row")).getElementsByClassName(stat)[0];
                }

                let stat_value = stat_loc.innerHTML;
                stat_value = Number(temp_totals[p_type][stat]);
                stat_loc.innerHTML = stat_value;
            }
        }
    }

    /**
     * Utility function for doing division without having to worry about
     * divide by 0 errors.
     * @param {Number} val1 Division Numerator
     * @param {Number} val2 Division Denomenator
     */
    zero_division_handler(val1, val2){
        if(Number(val2) != 0){
            return Number(val1)/Number(val2)
        }
        else {
            return 0
        }
    }

    /**
     * Utility function for creating a whole number percent value out of 
     * a decimal. Currently set to 0 places
     * @param {Number} val Value to be turned to percentage
     * @param {Number} places Number of places after decimal. Default=0
     */
    percentage(val, places=0){
        let percentage = (100 * val).toFixed(places);
        return percentage;
    }
}
