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
 * Handle keeping tabs on where we are as far as paging, results, etc
 *
 */
var Paging = Backbone.Model.extend({

    // we'll set some defaults for the fields, 50 per page and starting on page
    // 0
    defaults: {
        "count":  50,
        "page":   0,
        "tags":   []
    },

    /**
     * Read in the values for the default page/counts/tags from the url in case
     * someone sends/bookmarks a url. Should tie into our use of history.js
     * somehow
     *
     */
    url_load: function() {

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


/**
 * Control the events and updates from paging and such
 *
 */
var PagingView = Backbone.View.extend({


});


init = function () {
    // do the api call to get the most recent bookmarks
    bookie.api.recent({'page': 0, 'count': 50}, {
        'success': function (data) {
            model_list = [];
            _.each(data.bmarks, function (d) {
                var m = new Bmark(d);
                model_list.push(m);
                var view = new BmarkRow({'model': m});
            });

            // @todo update this to a proper view for controlling/updating the
            // count with the pagination info we want to display
            $('.count').html(data.count);
            $('.bmark').bind('mouseover', function (ev) {
                $(this).find('.item').css('display', 'block');
            }).bind('mouseout', function (ev) {
                $(this).find('.item').css('display', 'none');
            });
        },
        'error': function (data, error_str) {
            alert('error');
        }
    });
};

$(document).ready(function () {
    init();
});
