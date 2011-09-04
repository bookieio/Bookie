/**
 * Provide tools to do a backbone driven ui
 *
 */

/**
 * MODELS
 *
 */
var Bmark = Backbone.Model.extend({

    initialize: function() {

    },

    allowedToEdit: function(account) {
        return true;
    }

});

/**
 * COLLECTIONS
 *
 */
var BmarkList = Backbone.Collection.extend({
    model: Bmark
});

/**
 * VIEW
 *
 */
var BmarkRow = Backbone.View.extend({

    el: '.data_list',

    initialize: function(model) {
        console.log('created row');

        this.model = model;
        console.log(this.model);
        this.render();
    },

    events: {
      // "click .icon":          "open",
      // "click .button.edit":   "openEditDialog",
      // "click .button.delete": "destroy"
    },

    render: function() {
        console.log("render");

        // Compile the template using underscore
        console.log(this.model.toJSON());
   		var template = _.template($("#bmark_row").html(), this.model.toJSON());

   		// Load the compiled HTML into the Backbone "el"
        $(this.el).append(template);

    }

});




init = function () {
    // do the api call to get the most recent bookmarks
    bookie.api.recent({}, {
        'success': function (data) {
            model_list = [];
            _.each(data.bmarks, function (d) {
                var m = new Bmark();
                model_list.push(m.set(d));

                var view = new BmarkRow(m);
            });

            console.log(model_list);
        },
        'error': function (data, error_str) {
            alert('error');
        }
    });
};

$(document).ready(function () {
    init();
});
