/*jslint eqeqeq: false, browser: true, debug: true, onevar: true
, plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, mor: false */

/**
 * Help objects that load/edit the help in the system
 */
mor.help =  {
    helphtml: '<span class="help_target"><img src="/images/help.png" alt="help"</span>',

    /**
     * find the help objects and mark them with the help icon
     */
    highlight : function () {
        var $helps, node;

        // if we have the images already showing, just remove them to hide
        // them all
        $helps = $(".help_target");
        if ($helps.length > 0) {
            $helps.remove();
            return false;
        }

        // first get a list of all of the items on the page with the help
        // css
        $helps = $('[morhelp]');
        $helps.each(function () {
            var $help = $(this);
            $help.after(mor.help.helphtml);

            $par = $help.parent();

            node = mor.help.node();
            $('span.help_target img', $par).bind('click', {node: $help, helpnode: node }, function (e) {
                e.data.helpnode.show(e);
                e.stopPropagation();
            });
        });
    },

    /**
     * Object for the help nodes
     *
     */
    node : function (params) {
        var that, k, target;

        that = {
            attrid : 'morhelp',
            loadurl: '/help/loadhelp',
            saveurl: '/help/save',
            target: ''
        };
        
        // now apply any params to that
        for (k in params) {
            if (params.hasOwnProperty(k)) {
                that[k] = params[k];
            }
        }

        /**
         * Given a node, show the help div for this node
         */
        that.show = function (e) {
            // store the target so we can click it later on after save()
            that.target = e.target;

            var data, params, call, helpid;
            
            helpid = $(e.data.node).attr(that.attrid);

            // first grab the helpid from the attrid
            // then load up the ajax request to create the hoverdiv for this
            data = {helpid : helpid};

            // after saving the data, refresh the widget
            params = {
                url: that.loadurl,
                busy_message: 'Loading Help...',
                data: data,
                post_success: function () {
                    // add the edit hook
                    $('div#helptoggle a').bind('click', function (e) {
                        that.toggleedit();
                    });

                    $('form#helpedit_form').submit(that.save);
                }
            };

            call = mor.ajax.hoverdiv(params);
            call.run();
        };

        that.toggleedit = function () {
            var main_id, config_id, link_id, main_is_visible;

            main_id   = "#helpmain";
            config_id = "#helpedit";
            link_id = "#helptoggle a";

            // check which one is visible
            main_is_visible = $(main_id).is(':visible');

            if (main_is_visible) {
                $(main_id).hide();
                $(config_id).show();
                $(link_id).html("Back");
            } else {
                $(main_id).show();
                $(config_id).hide();
                $(link_id).html("Edit");
            }
        };

        /**
         * make an ajax call to save the config for this widget
         * show the fact that it's saved via the notice dialog
         * maybe down the road auto run the show_main() function
        */
        that.save = function () {
            var form_id, serial, call, form_data, params;

            form_id = "div#helpedit form ";
            serial = $(form_id).serializeArray();
            form_data = JSON.stringify(serial);

            // after saving the data, refresh the widget
            params = {
                url: that.saveurl,
                type: 'post',
                data: {'help_data' : form_data},
                busy_message: 'Saving Help Information',
                post_success: function () {
                    // we stored the target node so we can reclick it for
                    // the show(e) method to work
                    $(that.target).click();
                }
            };

            call = mor.ajax.content(params);
            call.run();

            // make sure the default submit does not happen
            return false;
        };

        return that;
    }
};

