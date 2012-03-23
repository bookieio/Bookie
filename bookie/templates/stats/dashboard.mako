<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookie Dashboard</%def>

<h2>Number of items in the system</h2>
<div id="count_chart" style="height: 250px; width: 600px"></div>

<h2>Average import queue depth</h2>
<div id="import_queue" style="height: 125px; width: 1200px"></div>
<%def name="add_js()">
    <script type="text/javascript">
        YUI().use('charts', 'charts-legend', function (Y) {
            var count_stats = ${count_summary|n};
            var queue_summary = ${queue_summary|n};

            var count_chart = new Y.Chart({
                dataProvider: count_stats,
                render:'#count_chart',
                categoryKey:'date',
                styles: {
                    axes:{
                        values:{
                            label:{
                                rotation: 0,
                                color:"#ff0000"
                            }
                        },
                        date:{
                            label:{
                                rotation:-90,
                                color: "#ff0000"
                            }
                        }
                    },
                },
                horizontalGridlines: true,
                verticalGridlines: true,
                legend: {
                    position: "right",
                    width: 300,
                    height: 400,
                    styles: {
                        hAlign: "center",
                        hSpacing: 4
                    }
                },
                type: 'line'
            });

            var import_queue = new Y.Chart({
                dataProvider: queue_summary,
                render:'#import_queue',
                horizontalGridlines: true,
                verticalGridlines: true,
                styles: {
                    axes:{
                        values:{
                            label:{
                                rotation: 0,
                                color: "#ff0000"
                            }
                        },
                       category:{
                            label:{
                                rotation: -90,
                                color: "#ff0000"
                            }
                        }
                    }
                },
                type: 'line'
            });
        });
    </script>
</%def>
