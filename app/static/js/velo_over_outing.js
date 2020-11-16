class velo_over_time {
    constructor(element, height, width, colors){
        var self = this;

        self.element_id = element;
        self.margin = {top: 25, bottom: 25, left: 25, right: 8}
        self.width = width - self.margin.right - self.margin.left
        self.height = height - self.margin.top - self.margin.bottom

        self.colors = colors;

        self.svg = d3.select(`#${element}`)
            .append("svg")
                .attr("height", height)
                .attr("width", width)
        
        self.legend_canvas = self.svg.append("g")
            .attr("transform", `translate(${self.margin.left}, 0)`)

        self.canvas = self.svg.append("g")
            .attr("transform", `translate(${self.margin.left}, ${self.margin.top})`)

        self.data = null

    }

    set_data(data){
        var self = this;
        data = data.filter(function(pitch){return pitch.velocity != null})
        self.data = data

        self.x_scale = d3.scaleLinear()
            .domain(d3.extent(self.data, (d) => +d.pitch_num))
            .range([self.margin.left, self.width])

        self.y_scale = d3.scaleLinear()
            .domain(d3.extent(self.data, (d) => (d.velocity != "" ? +d.velocity : 0)))
            .range([self.height - self.margin.top, self.margin.bottom])

        self.path_function = d3.line()
            .x(d => self.x_scale(+d.pitch_num))
            .y(d => self.y_scale(+d.velocity))
    }
    
    draw(){
        var self = this;

        var circle_radius = 4;

        var all_pitches = d3.map(self.data, (d) => d.pitch_type).keys();
        // console.log(`All pitches: ${all_pitches}`)
        
        self.legend = self.legend_canvas.selectAll("g")
            .data(all_pitches)
            .enter()
            .append("g")

        self.legend.append("circle")
            .attr("cx", (d, i) => i * 60)
            .attr("cy", 10)
            .attr("r", circle_radius * 2)
            .attr("fill", (d) => `${self.colors[d].color}`)
        
        self.legend.append("text")
            .attr("x", (d, i) => i * 60 + 12)
            .attr("y", 10)
            .attr("alignment-baseline", "middle")
            .text((d) => self.colors[d].type)

        // Draw Grid Lines
        // self.canvas.append("g")
        //     .attr("transform", `translate(0, ${self.height})`)
        //     .attr("class", "grid")
        //     .call(d3.axisBottom(self.x_scale).tickSize(-self.height).tickFormat(""))
        // self.canvas.append("g")
        //     .attr("transform", `translate(0, 0)`)
        //     .attr("class", "grid")
        //     .call(d3.axisLeft(self.y_scale).tickSize(-self.width).tickFormat(""))

        // Draw Axis'
        self.xAxis = self.canvas.append("g")
            .attr("transform", `translate(0, ${self.height})`)
            .call(d3.axisBottom(self.x_scale))
        self.yAxis = self.canvas.append("g")
            .attr("transform", `translate(0, 0)`)
            .call(d3.axisLeft(self.y_scale))

        // Draw the line for the right pitches
        all_pitches.forEach(p => {
            self.canvas.append("path")
                .attr("d", self.path_function(self.data.filter((d) => d.pitch_type == p)))
                .attr("stroke", self.colors[p].color)
                .attr("stroke-width", 2)
                .attr("fill", "none");
        });

        // Draw dot indicators
        self.canvas.append("g")
            .selectAll("circle")
            .data(self.data)
            .enter()
            .append("circle")
                .attr("cx", (d) => self.x_scale(+d.pitch_num))
                .attr("cy", (d) => self.y_scale(+d.velocity))
                .attr("r", circle_radius)
                .attr("fill", (d) => self.colors[d.pitch_type].color)
    }
}