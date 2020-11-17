//global var holding the color codes for balls put in play
var traj_colors = {
    "GB": "rgb(255, 0, 0)",
    "LD": "rgb(0, 255, 0)",
    "FB": "rgb(51, 204, 255)",
    "": "yellow" // outcomes with no trajectory will be black
}

//base code for hard hit star
var star = d3.symbol().type(d3.symbolStar).size(30);
var legend_star = d3.symbol().type(d3.symbolStar).size(50);

//design vars
var legend_circle_size = 8;
var field_circle_size = 6;

/**
 * Class for creating the field svg for spray charts
 */
class field {
    /**
     * Creates a svg of height and width in the div of div_id provided. This svg
     * represents the baseball field, for which batter sprays can be potted
     * 
     * @param {String} div_id Id of div you wish to place field svg into
     * @param {Number} width Width of svg
     * @param {Number} height Height of svg
     */
    constructor(div_id, width=457, height=457){


        this.field_svg = d3.select("#"+div_id)
            .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("id", "field-sprays");

        //add graphics object
        this.g = this.field_svg.append("g")
            // .attr("transform", "translate(0, 95)");
/*
        //add image to svg
        this.field_svg.append("svg:image")
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', 435)
            .attr('height', 430)
            .attr('transform', 'translate(17,17)')
            .style('alignment-baseline', 'middle')
            .attr("xlink:href", window.location.origin + "/static/images/field.png");
*/
        //scale variables for field image
        this.xScalef = d3.scaleLinear().range([width, 0]).domain([250, -250]);
        this.yScalef = d3.scaleLinear().range([height, 0]).domain([-100, 400]);

        this.create_field()
    }

    /**
     * This class is meant to be called by the constructor only. If called externally, 
     * no action will happen. 
     * 
     * create_field contains the variables and statements to create an svg baseball field, which should 
     * scale to both the height and width variables in the constructor.
     */
    create_field(){

        //path to create field outline
        let field_outline_path =
            "M " + this.xScalef(0) + " " +    this.yScalef(-45) + " " + //backstop center
            "L " + this.xScalef(50) + " " +   this.yScalef(-25) + " " + //backstop bottom right corner
            "L " + this.xScalef(242) + " " +  this.yScalef(222) + " " + //field rf corner @ 330
            "L " + this.xScalef(145) + " " +   this.yScalef(334) + " " + // field rf straight away
            "L " + this.xScalef(68) + " " +   this.yScalef(375) + " " + 
            "L " + this.xScalef(0) + " " +   this.yScalef(395) + " " + // dead center @ 395
            "L " + this.xScalef(-68) + " " +  this.yScalef(375) + " " + 
            "L " + this.xScalef(-145) + " " +  this.yScalef(334) + " " + // field lf straight away
            "L " + this.xScalef(-242) + " " + this.yScalef(222) + " " + //field lf corner @ 330
            "L " + this.xScalef(-50) + " " +  this.yScalef(-25) + " " + // backstop bottom left corner
            "L " + this.xScalef(0) + " " +    this.yScalef(-45) + " " + //backstop center
            "Z";

        let field_inner_outline_path =
            "M " + this.xScalef(0) + " " + this.yScalef(-40) + " " + //backstop center
            "L " + this.xScalef(50) + " " + this.yScalef(-20) + " " + 
            "L " + this.xScalef(237) + " " + this.yScalef(222) + " " + // RF corner @ 330
            "L " + this.xScalef(145) + " " + this.yScalef(329) + " " + // stright away stretch
            "L " + this.xScalef(68) + " " + this.yScalef(370) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(390) + " " + // Dead center @ 395
            "L " + this.xScalef(-68) + " " + this.yScalef(370) + " " +
            "L " + this.xScalef(-145) + " " + this.yScalef(329) + " " + //straignt away stretch
            "L " + this.xScalef(-237) + " " + this.yScalef(222) + " " + // LF corner @ 330
            "L " + this.xScalef(-50) + " " + this.yScalef(-20) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(-40) + " " + //backstop center
            "Z";

        let infield_dirt = 
            "M " + this.xScalef(85) + " " + this.yScalef(80) + " " + //move to first base
            "L " + this.xScalef(0) + " " + this.yScalef(170) + " " +
            "L " + this.xScalef(-85) + " " + this.yScalef(80) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef( -5) + " " + 
            "L " + this.xScalef(85) + " " + this.yScalef(80) + " " +
            "C " + this.xScalef(85) + " " + this.yScalef(200) + " " + this.xScalef(-85) + " " + this.yScalef(200) + " " + this.xScalef(-85) + " " + this.yScalef(80) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(-5) + " " + 
            "Z";
        
        let infield_grass = 
            "M " + this.xScalef(0) + " " + this.yScalef(5) + " " + 
            "L " + this.xScalef(60) + " " + this.yScalef(60) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(120) + " " +
            "L " + this.xScalef(-60) + " " + this.yScalef(60) + " " +
            "Z";


        let foul_lines = 
            "M " + this.xScalef(-239) + " " + this.yScalef(239) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(0) + " " + 
            "L " + this.xScalef(239) + " " + this.yScalef(239) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(0) + " " + 
            "Z";

        


        this.g.append("path")
            .attr("id", "field-outline")
            .attr("d", field_outline_path)
            .style('stroke', 'black')
            .style("fill", "rgb(233, 152, 30)")
            .style('stroke-width', 1);
        this.g.append("path")
            .attr("id", "field-inner-outline")
            .attr("d", field_inner_outline_path)
            .style("fill", "rgb(25, 151, 49)");
        this.g.append("path")
            .attr("id", "field-infield-dirt")
            .attr("d", infield_dirt)
            .style("fill", "rgb(233, 152, 30)");
        this.g.append("path")
            .attr("id", "field-infield-grass")
            .attr("d", infield_grass)
            .style("fill", "rgb(25, 151, 49)");
        this.g.append("path")
            .attr("id", "field-foul-line")
            .attr("d", foul_lines)
            .style("stroke", "white")
            .style('stroke-width', 2);

    }

    /**
     * Function to draw a circle representing a hit on the field svg. 
     * The circle will be drawn at (x, y)
     * 
     * @param {Number} x x coord of circle to draw
     * @param {Number} y y coord of circle to draw
     * @param {String} traj traj of circle(FB, LD, GB)
     * @param {boolean} hard_hit bool for hard hit star
     */
    drawCircle(x, y, traj="", hard_hit=false, pitch_tracker=false){
        this.field_svg.append('circle')
            .attr('class', 'field-circle')
            .attr('cx', this.xScalef(x))
            .attr('cy', this.yScalef(y))
            .attr('r', field_circle_size)
            .style('fill', traj_colors[traj])
            .style("stroke", "black")
            .style("stroke-width", 1);
        
        //add hard hit star if needed
        if (!pitch_tracker) {
            if(hard_hit){
                this.field_svg.append("path")
                    .attr("d", star)
                    .attr("transform", "translate("+this.xScalef(x)+","+this.yScalef(y)+")")
                    .attr("fill", "black");
            }
        }
    }

    removeCircles(){
        this.field_svg.selectAll('.field-circle').remove();
        this.field_svg.selectAll('.field-star').remove();
    }

    getLeftyZoneDivision(){
        //done from left to right
        const off = [-2, -1.01];
        const outside = [-1, -0.27];
        const middle = [-0.26, 0.26];
        const inside = [0.25, 2];

        return {inside:inside, middle:middle, outside:outside, off:off};
    }

    getRightyZoneDivision(){

        //done from left to right
        const inside = [-2, -0.28];
        const middle = [-0.27, 0.27];
        const outside = [0.26, 1];
        const off = [1.01, 2];

        return {inside:inside, middle:middle, outside:outside, off:off};
    }
}

/**
 * Class containing the field sprays legend as an object. 
 */
class field_legend {
    /**
     * Creates the legend for the spray chart in the div of div_id, of height, and width.
     * 
     * @param {String} div_id String id of div to place svg into
     * @param {Number} height Height of legend. best left as it
     * @param {Number} width width of legend. leave as is
     */
    constructor(div_id, height=50, width=457){
        //select div and add svg
        if(height < 50){
            height = 50;
        }

        this.legend_svg = d3.select("#"+div_id)
            .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("id", "field-legend")
                .attr("class", "chart")

        //create graphic object
        this.g = this.legend_svg
            .append("g")
            .attr("transform", null);

        //add base text to legend
        this.g.append("text")
            .attr('class', 'legend-text')
            .attr('font-size', '12pt')
            .attr('fill', 'black')
            .attr('x', 10)
            .attr('y', 12)
            .text("Hit Types:");

        //add labels for dots
        var x_index = 5;
        for(var type in traj_colors){

            //setup legend text
            if (type == "") {
                this.g.append("circle")
                    .attr("class", "legend-circle")
                    .attr("r", "8")
                    .attr("cy", 24)
                    .attr("cx", 40 + x_index)
                    .attr("fill", traj_colors[type]);
                this.g.append('text')
                    .attr('class', 'legend-text')
                    .attr('font-size', "8pt")
                    .attr('fill', 'black')
                    .attr('y', 24)
                    .attr('x', 10 + x_index)
                    .attr('text-anchor', 'middle')
                    .attr('alignment-baseline', 'middle')
                    .text("Other:");
            } else {
                this.g.append("circle")
                    .attr("class", "legend-circle")
                    .attr("r", "8")
                    .attr("cy", 24)
                    .attr("cx", 10 + x_index)
                    .attr("fill", traj_colors[type]);
                this.g.append('text')
                    .attr('class', 'legend-text')
                    .attr('font-size', "8pt")
                    .attr('fill', 'black')
                    .attr('y', 24)
                    .attr('x', 10 + x_index)
                    .attr('text-anchor', 'middle')
                    .attr('alignment-baseline', 'middle')
                    .text(type);
            }

            //incrment location
            x_index += 30;
        }

        //append the hard hit star to legend
        this.g.append("text")
            .attr('class', 'legend-text')
            .attr('font-size', "9pt")
            .attr('fill', 'black')
            .attr('y', 43)
            .attr('x', 10)
            .attr('text-anchor', 'left')
            .attr('alignment-baseline', 'middle')
            .text("Hard Hit:");
        this.legend_svg.append("path")
            .attr("d", legend_star)
            .attr("transform", "translate(65, 43)")
            .attr("fill", "black");

    }
}

class field_density{
    /**
     * Creates a field density map svg in the div of div_id provided. it will be of height, width
     * 
     * @param {*} div_id ID of div to create svg in
     * @param {*} width width of svg
     * @param {*} height height of svg
     */
    constructor(div_id, width=457, height=457){

        //scale variables for field
        this.xScalef = d3.scaleLinear().range([width, 0]).domain([250, -250]);
        this.yScalef = d3.scaleLinear().range([height, 0]).domain([-100, 400]);

        //path to create field outline
        let field_outline_path =
            "M " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(230) + " " + this.yScalef(155) + " " + 
            "L " + this.xScalef(75) + " " + this.yScalef(300) + " " +
            "L " + this.xScalef(-75) + " " + this.yScalef(300) + " " +
            "L " + this.xScalef(-230) + " " + this.yScalef(155) + " " +
            //"Q " + this.xScalef(0) + " " + this.yScalef(400) + " " + this.xScalef(-230) + " " + this.yScalef(155) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "Z";

        // draw infield lines
        let infield_outline_path = 
            "M " + this.xScalef(100) + " " + this.yScalef(25) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(125) + " " +
            "L " + this.xScalef(-100) + " " + this.yScalef(25) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(100) + " " + this.yScalef(25) + " " + 
            "Z";

        // draw infield position diamonds
        let position_3b = 
            "M " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(-100) + " " + this.yScalef(25) + " " + 
            "L " + this.xScalef(-50) + " " + this.yScalef(75) + " " + 
            "Z";
        let position_ss = 
            "M " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(-50) + " " + this.yScalef(75) + " " + 
            "L " + this.xScalef(-0) + " " + this.yScalef(125) + " " + 
            "Z";
        let position_2b = 
            "M " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(125) + " " + 
            "L " + this.xScalef(50) + " " + this.yScalef(75) + " " + 
            "Z";
        let position_1b = 
            "M " + this.xScalef(0) + " " + this.yScalef(-75) + " " + 
            "L " + this.xScalef(50) + " " + this.yScalef(75) + " " + 
            "L " + this.xScalef(100) + " " + this.yScalef(25) + " " + 
            "Z";

        //draw outfield position shapes
        let position_lf = 
            "M " + this.xScalef(-100) + " " + this.yScalef(25) + " " + 
            "L " + this.xScalef(-230) + " " + this.yScalef(155) + " " + 
            "L " + this.xScalef(-75) + " " + this.yScalef(300) + " " + 
            "L " + this.xScalef(-25) + " " + this.yScalef(100) + " " + 
            "Z";
        let position_cf = 
            "M " + this.xScalef(-25) + " " + this.yScalef(100) + " " + 
            "L " + this.xScalef(-75) + " " + this.yScalef(300) + " " + 
            "L " + this.xScalef(75) + " " + this.yScalef(300) + " " + 
            "L " + this.xScalef(25) + " " + this.yScalef(100) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(125) + " " + 
            "Z";
        let position_rf = 
            "M " + this.xScalef(25) + " " + this.yScalef(100) + " " + 
            "L " + this.xScalef(75) + " " + this.yScalef(300) + " " + 
            "L " + this.xScalef(230) + " " + this.yScalef(155) + " " + 
            "L " + this.xScalef(100) + " " + this.yScalef(25) + " " + 
            "Z";

        //Add the svg to the div
        this.field_svg = d3.select("#"+div_id)
            .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("id", "field-sprays");

        //add graphics object
        this.g = this.field_svg.append("g")
            .attr("transform", null);

        //draw field outline
        this.g.append("path")
            .attr("id", "field-density-field-outline")
            .attr("d", field_outline_path)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", infield_outline_path)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        
        //draw infield outline
        this.pos_3b = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_3b)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.pos_2b = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_2b)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.pos_ss = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_ss)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.pos_1b = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_1b)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);

        //draw outfield elements
        this.pos_lf = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_lf)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.pos_cf = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_cf)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
        this.pos_rf = this.g.append("path")
            .attr("id", "field-density-infield-outline")
            .attr("d", position_rf)
            .style('stroke', 'black')
            .style("fill", "none")
            .style('stroke-width', 2);
    }

    /**
     * Sets the color gradient value of the position asked to 
     * the grey value associated.
     * 
     * @param {Number} position number of position
     * @param {Number} shade percentage val between 0 and 1
     */
    set_position_shade(position, shade){
        let gradient_val = Math.round(255 - shade * 255);
        let rgb_val = "rgb(" + gradient_val + ", " + gradient_val + ", " + gradient_val + ")";

        if(position == 3){
            this.pos_1b.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(10))
                .attr('dy', 5)
                .attr('x', this.xScalef(55))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
        if(position == 4){
            this.pos_2b.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(60))
                .attr('dy', 5)
                .attr('x', this.xScalef(22))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
        if(position == 5){
            this.pos_3b.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(10))
                .attr('dy', 5)
                .attr('x', this.xScalef(-55))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");

        }
        if(position == 6){
            this.pos_ss.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(60))
                .attr('dy', 5)
                .attr('x', this.xScalef(-22))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
        if(position == 7){
            this.pos_lf.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(160))
                .attr('dy', 5)
                .attr('x', this.xScalef(-115))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
        if(position == 8){
            this.pos_cf.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(190))
                .attr('dy', 5)
                .attr('x', this.xScalef(0))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
        if(position == 9){
            this.pos_rf.style("fill", rgb_val);
            this.g.append("text")
                .attr('class', 'density-text')
                .attr('font-size', "12pt")
                .attr('fill', 'black')
                .attr('y', this.yScalef(160))
                .attr('dy', 5)
                .attr('x', this.xScalef(115))
                .attr('text-anchor', 'middle')
                .text(Math.round(shade*100)+"%");
        }
    }
}