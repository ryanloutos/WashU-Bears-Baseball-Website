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
            "M " + this.xScalef(0) + " " + this.yScalef(-85) + " " + 
            "L " + this.xScalef(55) + " " + this.yScalef(-65) + " " + 
            "L " + this.xScalef(190) + " " + this.yScalef(105) + " " + 
            "L " + this.xScalef(240) + " " + this.yScalef(155) + " " + 
            "L " + this.xScalef(138) + " " + this.yScalef(250) + " " +
            "L " + this.xScalef(46) + " " + this.yScalef(300) + " " +
            "L " + this.xScalef(-46) + " " + this.yScalef(300) + " " +
            "L " + this.xScalef(-138) + " " + this.yScalef(250) + " " +
            "L " + this.xScalef(-240) + " " + this.yScalef(155) + " " +
            "L " + this.xScalef(-190) + " " + this.yScalef(105) + " " +
            "L " + this.xScalef(-55) + " " + this.yScalef(-65) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(-85) + " " + 
            "Z";

        let field_inner_outline_path =
            "M " + this.xScalef(0) + " " + this.yScalef(-80) + " " + 
            "L " + this.xScalef(50) + " " + this.yScalef(-60) + " " + 
            "L " + this.xScalef(180) + " " + this.yScalef(100) + " " + 
            "L " + this.xScalef(232) + " " + this.yScalef(153) + " " + 
            "L " + this.xScalef(133) + " " + this.yScalef(245) + " " +
            "L " + this.xScalef(41) + " " + this.yScalef(295) + " " +
            "L " + this.xScalef(-41) + " " + this.yScalef(295) + " " +
            "L " + this.xScalef(-133) + " " + this.yScalef(245) + " " +
            "L " + this.xScalef(-232) + " " + this.yScalef(153) + " " +
            "L " + this.xScalef(-180) + " " + this.yScalef(100) + " " +
            "L " + this.xScalef(-50) + " " + this.yScalef(-60) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(-80) + " " + 
            "Z";

        let infield_dirt = 
            "M " + this.xScalef(60) + " " + this.yScalef(-5) + " " + //move to first base
            "L " + this.xScalef(0) + " " + this.yScalef(55) + " " +
            "L " + this.xScalef(-60) + " " + this.yScalef(-5) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef( -65) + " " + 
            "L " + this.xScalef(75) + " " + this.yScalef(10) + " " +
            "C " + this.xScalef(65) + " " + this.yScalef(90) + " " + this.xScalef(-65) + " " + this.yScalef(90) + " " + this.xScalef(-75) + " " + this.yScalef(10) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(-65) + " " + 
            "Z";
        
        let infield_grass = 
            "M " + this.xScalef(0) + " " + this.yScalef(-55) + " " + 
            "L " + this.xScalef(50) + " " + this.yScalef(-5) + " " +
            "L " + this.xScalef(0) + " " + this.yScalef(45) + " " +
            "L " + this.xScalef(-50) + " " + this.yScalef(-5) + " " +
            "Z";


        let foul_lines = 
            "M " + this.xScalef(-230) + " " + this.yScalef(170) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(-60) + " " + 
            "L " + this.xScalef(230) + " " + this.yScalef(170) + " " + 
            "L " + this.xScalef(0) + " " + this.yScalef(-60) + " " + 
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
    drawCircle(x, y, traj="", hard_hit=false){
        this.field_svg.append('circle')
            .attr('class', 'field-circle')
            .attr('cx', this.xScalef(x))
            .attr('cy', this.yScalef(y))
            .attr('r', field_circle_size)
            .style('fill', traj_colors[traj]);
        
        //add hard hit star if needed
        if(hard_hit != false){
            this.field_svg.append("path")
                .attr("d", star)
                .attr("transform", "translate("+this.xScalef(x)+","+this.yScalef(y)+")")
                .attr("fill", "black");
        }
    }

    drawEncodedCircle(x, y, data){
        this.field_svg.append('circle')
            .attr('class', 'field-circle')
            .attr('cx', this.xScalef(x))
            .attr('cy', this.yScalef(y))
            .attr('r', field_circle_size)
            .style('fill', traj_colors[traj]);

        
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
    constructor(div_id, height=70, width=457){
        //select div and add svg
        this.legend_svg = d3.select("#"+div_id)
            .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("id", "field-legend")
                .attr("class", "chart")
                .attr("align", "center");

        //create graphic object
        this.g = this.legend_svg.append("g")
            .attr("transform", null);

        //add base text to legend
        this.g.append("text")
            .attr('class', 'legend-text')
            .attr('font-size', '14pt')
            .attr('fill', 'black')
            .attr('x', 10)
            .attr('y', 20)
            .text("Hit Types:");

        //add labels for dots
        var x_index = 0;
        for(var type in traj_colors){
            
            //add legend circle
            this.g.append("circle")
                .attr("class", "legend-circle")
                .attr("r", "8")
                .attr("cy", 20)
                .attr("cx", 175+x_index)
                .attr("fill", traj_colors[type]);

            //setup legend text
            if (type == "") {
                this.g.append('text')
                    .attr('class', 'legend-text')
                    .attr('font-size', "9pt")
                    .attr('fill', 'black')
                    .attr('y', 20)
                    .attr('dy', 5)
                    .attr('x', 145 + x_index)
                    .attr('text-anchor', 'middle')
                    .text("Other:");
            } else {
                this.g.append('text')
                    .attr('class', 'legend-text')
                    .attr('font-size', "9pt")
                    .attr('fill', 'black')
                    .attr('y', 20)
                    .attr('dy', 5)
                    .attr('x', 145 + x_index)
                    .attr('text-anchor', 'middle')
                    .text(type + ":");
            }

            //incrment location
            x_index += 60;
        }

        //append the hard hit star to legend
        this.g.append("text")
            .attr('class', 'legend-text')
            .attr('font-size', "9pt")
            .attr('fill', 'black')
            .attr('y', 40)
            .attr('dy', 5)
            .attr('x', 145)
            .attr('text-anchor', 'middle')
            .text("Hard Hit:");
        this.legend_svg.append("path")
            .attr("d", legend_star)
            .attr("transform", "translate(185, 40)")
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