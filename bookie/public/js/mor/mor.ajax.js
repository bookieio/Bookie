/*jslint eqeqeq: false, browser: true, debug: true, onevar: true
, plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false */

mor.ajax = {};
/**
 * ajax.content
 * Basic ajax framework to perform an ajax request
 * if target is specified then check for a html in the payload and put that into
 *  the target
 * if no target, just perform the ajax action and handle success/failure
 *
 */
mor.ajax.content = function (params) {
    var that, escape_data, response, k, required_params, sanitycheck;

    that = { url: '',
                 target: '',            // can be a jquery id or a callback function
                 target_append: false,  // bool value
                 data: '',
                 skip_escape: false,
                 type: 'GET',
                 busy_message: 'loading...',
                 error_message: 'Sorry, there was an error.',
                 success_message: null,
                 pre_ajax: null,
                 post_success: null,
                 post_error: null
    };

    // now apply any params to that
    for (k in params) {
        if (params.hasOwnProperty(k)) {
            that[k] = params[k];
        }
    }

    escape_data = function (data) {
        var clean, index;
        clean = {};

        for (index in data) {
            if (data.hasOwnProperty(index)) {
                clean[index] = escape(data[index]);
            }
        }

        return clean;
    };

    required_params = ['url'];
    sanitycheck = function (params) {
        var i, field;
        // check for required parameters
        for (i = 0; i < required_params.length; i++) {
            field = required_params[i];
            if (!params[field]) {
                throw ('Required parameter ' + field + ' not available in this ajax request');
            }
        }
    };

    that.run = function ()  {
        var clean_data;

        // sanity check the params we have available
        sanitycheck(that);
        
        mor.notice.showMessage(that.busy_message);

        // make any pre_ajax callbacks
        if (that.pre_ajax !== null) {
            that.pre_ajax();
        }
        
        if (that.skip_escape) {
            clean_data = that.data;
        } else {
            clean_data = escape_data(that.data);
        }

        $.ajax({
            type: that.type,
            url: that.url,
            data: clean_data,
            dataType: 'json',
            success: response
        });

        return false;
    };

    // handle an ajax failure response
    that.handle_fail = function (data) {
        // if there is no message, then make sure we set a default one
        var message;
        if (data.message === "") {
            message = that.error_message;
        } else {
            message = data.message;
        }

        mor.notice.showMessage(message, mor.notice.types.error);

        if (that.post_error !== null) {
            that.post_error(data);
        }
    };

    // handle an ajax success repsonse
    that.handle_success = function (data) {
        // if there is a target, then look for a data.payload.html and apply
        // it
        if (that.target) {
            that.handle_target(data.payload.html);
        }

        // if there's a success message then show it as a notice
        if (data.message !== "")  {
            mor.notice.showMessage(data.message, mor.notice.types.notes);
        } else {
            mor.notice.hideMessage();
        }

    };

    that.handle_target = function (html) {
        // if the target is a function, then run it
        if (typeof that.target == 'function') {
            that.target(html);
        } else {

            var id = that.target;

            // make sure we can find the target
            if ($(id).length === 0) {
                // throw an error
                throw ('Could not locate target: ' + id);
            }

            if (that.target_append) {
                // if we're appending...then we don't need to worry about
            } else {
                $(id).html("");
                            }

            $(id).append(html);
        }

    };

    // handle the ajax response
    response = function (data) {
        var success = data.success;

        if (success === false) {
            that.handle_fail(data);
        } else {
            mor.notice.hideMessage();

            that.handle_success(data);

            if (that.post_success !== null) {
                that.post_success(data);
            }
        }
    };

    return that;
};


mor.ajax.api = function (model, method, params) {
    var base_data, base_params, that, k;

    base_data = { 
        'model' : model,
        'method' : method,
        'key' : 'xi8eiLeiuo5leiPhNeewah0GiRah1aiw' 
    };

    base_params = {
        url : '/panel/api',
        busy_message : 'Hitting API'
    };


    // add the base params to the ajax.content options
    // these include things like urls and callbacks
    for (k in base_params) {
        if (true) {
            params[k] = base_params[k];
        }
    }

    // now add the actual data parts of the params 
    // this is stuff sent to the url in the request
    if (params.data === undefined) {
        params.data = base_data; 
    } else {
        for (k in base_data) {
            if (true) {
                params.data[k] = base_data[k];
            }
        }
    }

    that = mor.ajax.content(params);
    return that;
};

/**
 * The only thing mor.ui.tab offers is that it tracks the loaded state so that
 * we only load the time once unless somehow cleared otherwise
 */
mor.ajax.tab = function (params) {
    var that;
    that = mor.ajax.content(params);
    that.loaded = false;
    that.required_params = ['url', 'target'];

    that.do_call = that.run;

    /**
     * mor.ajax.tab
     * Override the default run method
     * we need to track/test the loaded value to see if we should perform the
     * request or not
     *
     * We also need to accept data from the tab call for information
     * required to load up the tab properly such as object id/etc
     *
     */
    that.run = function (data) {
        // if it's not loaded go ahead
        if (that.loaded) {
            return false;
        } else {
            that.data = data;
            that.do_call();
            that.loaded = true;
        }
    };

    return that;

};


/**
 * an ajax modal dialog will be displayed upon completion of this ajax request
 *
 */
mor.ajax.modal = function (params) {
    var that;
    
    that = mor.ajax.content(params);

    that.post_show = function () {};
    if (typeof(params.post_show) == 'function') {
        that.post_show = params.post_show;
    }

    that.modal_config = {
        id : 'mor_modal',
        title : 'Modal Ajax Request'
    }

    if (params.modal_config) {
        that.modal_config = params.modal_config;
    }

    // we want to override the handling of the successful request
    that.handle_success = function (data) {
        var modal;
        // create a modal div
        // if this is final, else it's normal

        // if the payload doens't have html in it, error
        if (!data.payload.html) {
            mor.notice.showMessage('No html response. Cannot create modal dialog', mor.notice.types.error);
        } else {
            modal = mor.ui.modal({'modal_config' : that.modal_config});

            modal.create(that.modal_config.id, that.modal_config.title, data.payload.html);
            modal.set_opencallback(that.post_show);
            modal.show();
        }
    };

    return that;
};
