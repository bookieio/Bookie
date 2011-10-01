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
        this.set({'dateinfo': this._dateinfo()});
        this.set({'prettystored': this._prettystored()});
    },

    allowedToEdit: function(account) {
        return true;
    },

    _dateinfo: function() {
        var t = new Date(this.get('stored'));
        return t.getMonth() + "/" + t.getDate();
    },

    /**
     * Builda date string of a pretty format
     * %m/%d/%Y %H:%M
     *
     */
    _prettystored: function () {
        var t = new Date(this.get('stored'));
        return t.getMonth() + "/" + t.getDate() + "/" + t.getFullYear() + " " +
               t.getHours() + ":" + t.getMinutes();
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

    tagName: 'div',
    className: 'bmark',
    parent: '.data_list',

    initialize: function(model) {
        this.render();
    },

    events: {
      // "click .icon":          "open",
      // "click .button.edit":   "openEditDialog",
      // "click .button.delete": "destroy"
    },

    render: function() {
        // Compile the template using underscore
        var template = _.template($("#bmark_row").html(), this.model.toJSON());

        // Load the compiled HTML into the Backbone "el"
        //     var template = $("#category_tpl").tmpl(this.model.toJSON());
        $(this.el).html(template).attr('id', this.model.get('hash_id'));
        $(this.parent).append(this.el);
    }

});


init = function () {
    // do the api call to get the most recent bookmarks
    bookie.api.recent({}, {
        'success': function (data) {
            model_list = [];
            _.each(data.bmarks, function (d) {
                var m = new Bmark(d);
                model_list.push(m);
                var view = new BmarkRow({'model': m});
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
