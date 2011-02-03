/*global console, YUI

*/

YUI.add('mor-form', function (Y) {

    Y.MorForm = (function () {
        var forms_formatted, that;

        // private property to track the forms we've processed
        forms_formatted = {};

        that = {};
        that.init = function () {
            that.fieldset_prep();
            that.maxlabels();
            that.adderrortext();
        };

        /**
         * Some basic starter operations to perform first
         *
         */
        that.fieldset_prep = function () {
            Y.all("li input[type='hidden']").each(function (n) {
                var input_name, my_parent;
                // if this is a hidden element, then mark the li as hidden so it
                // doesn't count towards zebra/etc
                // checkboxes mess this up since we have a hidden input for each
                // checkbox. Check the parent for a checkbox elemement with the same
                // name first
                input_name = n.get('name');
                my_parent = n.get('parentNode');

                // @todo this needs to be tested on a form with some hidden
                // checkboxes
                if (my_parent.one('input:not([type=hidden])')) {
                    // don't hide this parent, something is visible inside of it
                    return;
                } else {
                    my_parent.setStyle('display', 'none');
                }
            });

            Y.all('fieldset').addClass('mor-fieldset');
        };

        /**
         * Set the width of the labels on the html form to proper size based on the
         * largest element. Makes things nice and justified
         *
         * Note: needs to be run when a tab or items that is hidden is shown
         */
        that.maxlabels = function () {
            var submit_label, nodes;

            // the one off button we need to fix is the submit button which has no label
            // go ahead and add it in just for show
            submit_label = '<label for="submit">&nbsp;</label>';

            // first make sure we don't already have a label
            nodes = Y.all('input[type=submit]');
            nodes.each(function (n) {
                var p = n.get('parentNode');
                if (p.one('label') == null) {
                    p.prepend(submit_label);
                }
            });

            nodes = Y.all('input.submit_continue');
            nodes.each(function (n) {
                var p = n.get('parentNode');
                if (p.one('label') == null) {
                    p.prepend(submit_label);
                }
            });

            Y.all('form').each(function (n) {
                // first check out if we have already formatted this form
                if (forms_formatted[n.get('id')] == undefined) {
                    // only do it if the form is visible

                    if (n.getComputedStyle('display') !== 'none') {
                        // we're formatting this one time only
                        forms_formatted[n.get('id')] = true;

                        var max, id, label_ids, label_list;
                        max = 100;
                        label_ids = Y.Lang.sub("form#{id} label", {'id': n.get('id')});
                        label_list = Y.all(label_ids);

                        label_list.each(function (n) {
                            var my_width = parseInt(n.getStyle('width'), 10);
                            if (my_width > max) {
                                max = my_width;
                            }
                        });

                        // add 20px for any potential admin fields padlock
                        max = max + 20 + 'px';
                        if (label_list != null) {
                            label_list.each(function (n) {
                                n.setStyle('width', max);
                            });
                        }
                    }

                } else {
                    // don't format, we already messed with it
                    return;
                }
            });
        };

        /**
         * Show any fields with errors with a nice error text
         *
         */
        that.adderrortext = function () {
            Y.all('span.error').each(function (n) {
                console.log(n.get('innerHTML'));

                if (n.get('innerHTML').match(/[^\s]/)) {
                    // we have to move this to get around formencode not outputting
                    // error text 'after' the input for file inputs
                    n.setStyle('display', 'block');
                }
            });
        };

        return that;

    }());
}, '0.0.1', { requires: ['node'] });



YUI.add('mor-ui', function (Y) {

    Y.MorUI = (function () {
        var that = {};
        that.container = 'table';
        that.row = 'tr';

        /**
         * Enable zebra striping of table rows
         *
         * effects: table.zebra
         * css: tr and td .odd / .even
         *
         */
        that.zebra = function (params) {
            var container, row, node_id;

            if (params == undefined) {
                params = {};
            }

            container = params.container ? params.container : that.container;
            row = params.row ? params.row : that.row;

            node_id = Y.Lang.sub('{container}.zebra {row}', {container: container, row: row});
            Y.all(node_id).odd().each(function (node) {
                node.addClass('odd');
                node.get('children').addClass('odd');
            });

            Y.all(node_id).even().each(function (node) {
                node.addClass('even');
                node.get('children').addClass('even');
            });

        };

        /**
         * Create YUI2 buttons for items on the page
         *
         * effects: a.qp_button
         *
         * Note: will create generated ids for those links without one
         *
         */
        that.init_buttons = function () {
            var Y2, button_list, button, anchor_id;

            Y2 = Y.YUI2;
            button_list = Y.all('a.qp_button');
            button_list.each(function (node) {
                anchor_id = node.get('id');
                if (anchor_id == undefined || anchor_id == "") {
                    node.set('id', Y.guid(node));
                }
                button = new Y2.widget.Button(node.get('id'));
            });
        };

        /**
         * UI for displaying a global application message to the user
         *
         */
        that.app_message = {
            // constants
            'html_id': '#mor_message',
            'global_css': 'mor_message',
            'default_msg': 'Loading ...',
            'types': {
                error: { 'css' : 'mor_message_error' },
                note: { 'css' : 'mor_message_note' },
                loading: { 'css' : 'mor_message_loading' }
            },

            /**
             * Fill in the message container content and display to the user
             *
             * @param message string of the message
             * @param type error, note, loading
             *
             */
            'show_message' : function (message, type) {
                var message_string, type_class, type_title, message_html;

                // if there is no message/type hit the defaults
                if (message === undefined) {
                    message = this.default_msg;
                }

                // if there's not type default to loading
                if (type === undefined) {
                    type = this.types.loading;
                } else if (this.types[type]) {
                    type = this.types[type];
                } else {
                    type = this.loading;
                }

                message_string = Y.Lang.sub('<div class="{css} {type_css}"><div>&nbsp;{message}</div></div>',
                    { 'css': this.global_css,
                      'type_css': type.css,
                      'message': message
                    }
                );

                message_html = Y.one(this.html_id);
                message_html.setContent(message_string).on('click', function (ev) {
                    that.app_message.hide_message();
                    ev.preventDefault();
                });

                message_html.setStyle('display', 'block');
            },

            /**
             * Just hide the message container
             *
             */
            'hide_message' : function () {
                Y.one(this.html_id).setStyle('display', 'none');
            }

        };

        /**
         * Shortcut method to display an app_message
         *
         * @param message string of the message
         * @param type error, note, loading
         *
         */
        that.show_message = function (message, type) {
            that.app_message.show_message(message, type);
        };

        that.hide_message = function () {
            that.app_message.hide_message();
        };

        return that;
    }());
}, '0.0.1', { requires: ['node', 'yui2-button'] });


YUI.add('mor-io', function (Y) {

    Y.MorIO = (function () {
        var that = {};

        /**
         * Parses a standard jsonresponse object into a JS object
         *
         * @param resp the json response
         * @return parsed object
         *
         */
        that.parse_json_response = function (resp) {
            var parsed = Y.JSON.parse(resp);
            return parsed;
        };


        /**
         * Base model for an ajax call used globally throughout the system
         *
         * Usage:
         *
         *
         */
        that.ajax_call = function () {
            var that = {};

            that.url = "";
            that.cfg = {
                method: 'GET',          // default is get
                headers: {
                    'Accept': 'application/json'
                },
                on: {
                    'start': function (id, args) {
                        // start the ui to display loading
                        Y.MorUI.show_message();
                    },

                    'complete': function (id, o, args) {

                    },

                    'failure': that.ajax_failure
                }
            };

            return that;
        };

        /**
         * Global ajax failure catcher
         *
         */
        that.ajax_failure = function (id, o, args) {
            var error_msg = "We're sorry, but there was an issue with your ajax request.";

            console.log('Big Ajax Failure');
            console.log(id);
            console.log(o);
            console.log(args);

            YUI().use("mor-ui", function (Y) {
                Y.MorUI.show_message(error_msg, 'error');
            });
        };

        return that;
    }());
}, '0.0.1', { requires: ['mor-ui', 'io', 'json'] });

