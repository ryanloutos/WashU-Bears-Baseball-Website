
var colors_default = {
    1: {color: 'rgb(230, 25, 75)', type: "FB"},
    2: {color: 'rgb(0, 130, 200)', type: "CB"},
    3: {color: 'rgb(0, 200, 0)' , type: "SL"},
    4: {color: 'rgb(200, 200, 0)', type: "CH"},
    5: {color: 'rgb(0, 200, 200)', type: "CT"},
    7: {color: 'rgb(255, 128, 0)', type: "SM"}
}

/**
 * Draw a plinko depicting the pitch utilization in each count. 
 * 
 * Hopefully its size dynamically changes based on what you provide
 * it so it may possibly react to page changes.
 * 
 * Created: 11/16/20
 * 
 * Author: Mitchell Black
 */
class count_pitch_utilization{
    
    /**
     * Initialize things necessary to create the plinko
     * 
     * @param  {String} element element to draw the plinko in
     * @param  {Number} width Width of drawing
     * @param  {Number} height Height of drawing
     * @param  {Object} colors Colors of pitches in plinko. Default null
     */
    constructor(element, width, height, colors=null){
        var self = this;

        if(colors == null){
            self.colors = colors_default;
        } else {
            self.colors = colors
        }

        self.margin = {top: 10, bottom: 10, left: 10, right: 10}

        self.svg = d3.select(`#${element}`)
            .append("svg")

        self.canvas = self.svg.append("g")
            .attr("transform", `translate(${self.margin.left}, ${self.margin.top})`)

        self.data = null;

        self.xScale = d3.scaleLinear()
        self.yScale = d3.scaleLinear()

        self.update_dimensions(width, height);
    }

    /**
     * Updates the dimensions of the drawing to whatever is passed in .Done 
     * this way in the hopes of making its size dynamic
     * 
     * @param  {Number} width Current width of drawing
     * @param  {Number} height Current height of drawing
     */
    update_dimensions(width, height){
        
        var self = this;

        self.height = height - margin.top - margin.bottom;
        self.width = width - margin.right - margin.left;

        self.svg
            .attr("width", width)
            .attr("height", height);

        self.xScale
            .range([self.margin.left, self.width])
            .domain([0, 100]);

        self.yScale
            .range([self.margin.top, self.height])
            .domain([0, 100]);

    }

    
    /** 
     * Set the data for the plinko
     * 
     * @param  {Array} data The data for the plinko. Should be a list of pitch objects corresponding to pitches in an outing
     */
    set_data(data){
        self.data = data;
    }

    /**
     * Draw the Plinko!
     */
    draw(){
        
    }
}