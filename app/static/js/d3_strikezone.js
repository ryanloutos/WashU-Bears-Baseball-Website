//import d3 so can build objects out of it
// var d3 = import("../packages/d3/d3.js");
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
                .attr("width", width)
                .attr("height", height)
                .attr("class", "plot")
                .attr("id", "strikezone");
        
        //create graphics part of svg
        this.g = this.zone.append("g")
            .attr("tramsform", null);

        //Setup zone background ppearance
        this.zone.style('background-color', 'white')
            .style('border', '1px solid black')
            .style('margin', '10px');

        //setup strikezone scale variables
        this.xScale = d3.scaleLinear().range([width, 0]).domain([2, -2]);
        this.yScale = d3.scaleLinear().range([height, 0]).domain([0, 4]);

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
     * @param {*} coords
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
}

class strikezone_legend {

    constructor(div_id){
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
                .attr("width", '457')
                .attr("height", '70')
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