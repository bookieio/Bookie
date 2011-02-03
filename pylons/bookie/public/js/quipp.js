/*global console, YUI

*/

YUI.add('qadmin', function (Y) {
    var QAdmin,
        QADMIN = 'qadmin',
        sub = Y.Lang.sub,
        Y2 = Y.YUI2;

    QAdmin = function (config) {
        QAdmin.superclass.constructor.apply(this, arguments);
    };

    /** Static **/
    QAdmin.NAME = QAdmin;
    QAdmin.ATTRS = {


    };

    Y.extend(QAdmin, Y.Base, {
        initializer: function (config) { },

        destructor: function () {},

        /**
         * /login
         *
         */
        login: function () {
            YUI().use('node', 'mor-form', 'yui2-button', function (Y) {
                var Y2, button;

                Y2 = Y.YUI2;

                //YUI 2 implementation code
                button = new Y2.widget.Button("submit");

                // init the form ui tweaks
                Y.MorForm.init();
            });
        },

        /**
         *  /accounts/list
         *
         */
        account_list: {
            'init': function () {
                YUI().use("mor-ui", function (Y) {
                    Y.MorUI.init_buttons();
                    Y.MorUI.zebra();
                });
            }
        },

        /**
         *  /account/new
         *
         */
        account_new: {

            'init': function () {
                var ldap_button, submit_button;
                Y.MorForm.init();

                submit_button = new Y2.widget.Button('submit');
                ldap_button = new Y2.widget.Button('qp_ldap_search');

                // the id moved to qp_ldap_search-button now
                Y.one('#qp_ldap_search-button').on('click', this.lookup_ldap);
            },

            /**
             * check with the system if the username provided can be found in the
             * ldap database for work.
             *
             * If so we need to mark them as a special case user in the system
             *
             */
            'lookup_ldap': function (ev) {
                YUI().use("node", "mor-io", "io", function (Y) {
                    var username, my_call, request;

                    username = Y.one('#user_name').get('value');
                    if (username === "") {
                        Y.MorUI.show_message("Please supply a user name or email address", 'error');
                        return false;
                    }

                    // perform the actual ajax request
                    my_call = Y.MorIO.ajax_call();
                    my_call.url = "/accounts/fetch_ldap_user/{username}";

                    my_call.cfg.on.complete = function (id, o, args) {
                        var resp, user;

                        // the response should be a JSON message of normal body
                        resp = Y.MorIO.parse_json_response(o.responseText);

                        if (resp.success) {
                            // set the user name to the returned fullname
                            user = resp.payload.user;
                            Y.one('#user_name').set('value', user.fullName);
                            Y.one('#is_ldap').set('checked', 'checked').removeAttribute('disabled');
                            Y.MorUI.show_message(resp.message, 'note');
                        } else {
                            // if there's nothing found the message will be displayed by the
                            // default ajax content object
                            Y.MorUI.show_message(resp.message, 'error');
                        }
                    };

                    request = Y.io(Y.Lang.sub(my_call.url, {'username': username}), my_call.cfg);
                    ev.preventDefault();
                });
            }
        },

        /**
         * /accounts/$user/edit
         *
         */
        account_edit: {
            'init': function () {
                // init the form ui tweaks
                YUI().use("node", "yui2-button", "mor-form", function (Y) {
                    var Y2, ldap_button, submit_button;
                    Y2 = Y.YUI2;

                    Y.MorForm.init();

                    submit_button = new Y2.widget.Button('submit');
                });
            }
        }

    });


    Y.namespace('QAdmin');
    Y.QAdmin.Window = QAdmin;


}, '0.1', { requires: ['base', 'node', 'event', 'mor-ui', 'mor-form', 'yui2-datatable', 'yui2-button', 'yui2-connection'] });
