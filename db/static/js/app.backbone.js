// Models

var Telemetry = Backbone.Model.extend({});

/*** To deal with uri 
var TelemetryAppendix = Backbone.Model.extend({
        idAttribute: "list_id",
        urlRoot: '/api/telem',    
        initialize: function() {
            this.items = new app.ListItem;
            this.items.url = '/lists/' + this.id + '/items';
        }
    });
***/

var TelemetryCollection = Backbone.Collection.extend({
    url:"/api/telemetry/?satellite=99999"
});
 
var TelemetryDescriptors = TelemetryCollection.extend({
    parse: function(response){
        return response[0].appendix;
    }
 });

var TelemetryData = TelemetryCollection.extend({
    parse: function(response){
        return response.telemetry;
    },
    toJSON : function() {
      return this.map(function(model){ return model.toJSON(); });
    }
 });

// Views 
var TelemetryDescriptorsView = Backbone.View.extend({
    el: "#telemetry-descriptors",
    template: _.template($('#telemetryDescriptorsTemplate').html()),
    initialize: function(){
        this.listenTo(this.collection, 'add reset change remove', this.renderItem);
        this.collection.fetch();
    },
    render: function () {
        this.collection.each(function(model){
            this.$el.append(this.template(model.toJSON()));
        }, this);        
        return this;
    },
    renderItem: function (model) {
        this.$el.append(this.template(model.toJSON()));
    }
});

var telemetryDescriptorsView = new TelemetryDescriptorsView({ collection: new TelemetryDescriptors() });

////////// Telemetry D3 Viz

d3.custom = {};

d3.custom.barChart = function module(telemetry_key) {
    var config = {
        margin: {top: 20, right: 20, bottom: 40, left: 40},
        width: 700,
        height: 500
    };
    var svg;

    var dispatch = d3.dispatch('customHover');

    function exports(_selection) {
        _selection.each(function(_data) {
            var chartW = config.width - config.margin.left - config.margin.right,
                chartH = config.height - config.margin.top - config.margin.bottom;

            var x1 = d3.scale.ordinal()
                .domain(_data.map(function(d, i){ return d.telemetry.observation_datetime ; }))
                .rangeRoundBands([0, chartW], .1);

            var y1 = d3.scale.linear()
                .domain([0, d3.max(_data, function(d, i){ return +d.telemetry.damod_data[telemetry_key]; })])
                .range([chartH, 0]);

            var xAxis = d3.svg.axis()
                .scale(x1)
                .orient('bottom');

            var yAxis = d3.svg.axis()
                .scale(y1)
                .orient('left');

            var xInterval = chartW / _data.length;

            if(!svg) {
                svg = d3.select(this)
                    .append('svg')
                    .classed('chart', true);
                var container = svg.append('g').classed('container-group', true);
                container.append('g').classed('chart-group', true);
                container.append('g').classed('x-axis-group axis', true);
                container.append('g').classed('y-axis-group axis', true);
            }

            svg.transition().attr({width: config.width, height: config.height})
            svg.select('.container-group')
                .attr({transform: 'translate(' + config.margin.left + ',' + config.margin.top + ')'});

            svg.select('.x-axis-group.axis')
                .attr({transform: 'translate(0,' + (chartH) + ')'})
                .transition()
                .call(xAxis);

            svg.select('.y-axis-group.axis')
                .transition()
                .call(yAxis);

            // Define the line
            var valueline = d3.svg.line()
                .x(function(d,i) { return (xInterval*i + config.margin.left); })
                .y(function(d) { return y1(d.telemetry.damod_data[telemetry_key]) + config.margin.top; });

            // Add the valueline path.
            svg.append("path")
                .attr("class", "line")
                .attr("d", valueline(_data));

                // Add the scatterplot
            svg.selectAll("dot")
                .data(_data)
              .enter().append("circle")
                .attr("r", 3.5)
                .attr("cx", function(d, i) { return xInterval*i + config.margin.left })
                .attr("cy", function(d) { return y1(d.telemetry.damod_data[telemetry_key]) + config.margin.top; });

        });
    }
    exports.config = function(_newConfig) {
        if (!arguments.length) return width;
        for(var x in _newConfig) if(x in config) config[x] = _newConfig[x];
        return this;
    };
    d3.rebind(exports, dispatch, 'on');
    return exports;
};


// Telemetry Viz View
/////////////////////////////////////

var TelemetryVizView = Backbone.View.extend({
    el: ".chart",
    chart: null,
    chartSelection: null,
    initialize: function() {
        var that = this;
        this.model.fetch();
        _.bindAll(this, 'render', 'update');
        this.model.bind('change:data', this.render);
        this.model.bind('change:config', this.update);
        chart = d3.custom.barChart();
        chart.config(this.model.get('config'));
        chart.on('customHover', function(d, i){ console.log('hover', d, i); });
        this.renderPlaceholder();
    },
    events: {
        "click .telemetry-key": "update",
    },
    renderPlaceholder: function() {
        this.chartSelection = d3.select(this.el)
            .datum([{key: '', value: 0}])
            .call(d3.custom.barChart(this.model.get('data')[0].appendix[1].key));
    },
    render: function() {
        console.log(this.model.get('data')[0].appendix[1]);
        this.chartSelection = d3.select(this.el)
            .datum(this.model.get('data'))
            .call(d3.custom.barChart(this.model.get('data')[0].appendix[1].key));
    },
    update: function(e){
        var telemetry_key = $(e.currentTarget).attr('id').substring(1);
        this.chartSelection.call(d3.custom.barChart(telemetry_key));
    },
});

// Telemetry Data
/////////////////////////////////////

var TelemetryData = Backbone.Model.extend({
    url:"/api/telemetry/?satellite=99999",
    defaults: {
        data: [],
        dimension: {},
        config: {height: 500, width: 700}
    },
    parse: function(_json) {
        var data = _json;
        this.set({data: data});
    },
});

// Rendering
/////////////////////////////////////

var telemetryDataModel = new TelemetryData();
var telemetryVizView = new TelemetryVizView({model: telemetryDataModel})


// Buttons view
/////////////////////////////////////

var ControlView = Backbone.View.extend({
    el: ".control",
    events: {
        "click .update-data": "updateData",
        "click .update-config": "updateConfig",
    },
    updateData: function() {
        var that = this
        var newData = d3.range(this._randomInt(10)).map(function(d, i){ return that._randomInt(100); });
        this.model.set({data: newData});
    },
    updateConfig: function() {
        var newConfig = {width: this._randomInt(600, 100)};
        this.model.set({config: newConfig});
    },
    _randomInt: function(_maxSize, _minSize){ 
        var minSize = _minSize || 1;
        return ~~(Math.random() * (_maxSize - minSize)) + minSize; 
    }
});

var controlView = new ControlView({model: telemetryDataModel});
