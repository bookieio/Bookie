/*jslint eqeqeq: false, browser: true, debug: true, onevar: true
, plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false*/

mor.ui = {};

mor.ui.zebra = function (params) {
    var k, hoverid, $hover, evenid, oddid;

    this.config = {
        id : '.zebra',
        hoverclass : 'hover',
        evenclass : 'even',
        oddclass : 'odd',
        rowtarget: 'tr'
    };

    // now apply any params to that
    if (params) {
        for (k in this.config) {
            if (params.hasOwnProperty(k)) {
                this.config[k] = params[k];
            }
        }
    }

    // add hovering css rules
    // @todo find a way to figure out if we should use tr/div here so we can
    // zebra a div of divs
    hoverid = sprintf("%s %s", this.config.id, 'tr');
    
    $hover = $(hoverid);
    $hover.bind('mouseover', {cssclass: this.config.hoverclass}, function (e) {
        $(this).addClass(e.data.cssclass);
    });

    $hover.bind('mouseout', {cssclass: this.config.hoverclass}, function (e) {
        $(this).removeClass(e.data.cssclass);
    });

    // we remove any background colors in case it conflicts with the row highlighting
    // big culprit to this is the highlighting function when we add in a new row
    hoverid = sprintf("%s %s %s", this.config.id, this.config.rowtarget, 'td');
    evenid = sprintf("%s %s:%s", this.config.id, this.config.rowtarget, 'visible:even');
    oddid = sprintf("%s %s:%s", this.config.id, this.config.rowtarget, 'visible:odd');

    $(hoverid).css("background-color", "");
    $(evenid).removeClass(this.config.oddclass).addClass(this.config.evenclass);    
    $(oddid).removeClass(this.config.evenclass).addClass(this.config.oddclass);  
};


// this is just an untested wrapper, maybe we can get some unit tests around
// this at some point
mor.ui.datagrid = function (params) {
    var that, k, custom_draw_callback, sort; 

    that = {
        id : false,
        source_url : false,
        default_displaycount : 25,
        draw_callback : function (nRow, aaData, iStart, iEnd, aiDisplay) {
            mor.ui.zebra();
            mor.form.init();

            if (that.custom_draw_callback !== false) {
                that.custom_draw_callback();
            }
		},
        custom_draw_callback : false,
        default_sort_col: 0,
        default_sort_order: 'asc',
        full_sort_order: false,
        default_loading_msg: 'Loading...',
        column_data: undefined,
        data : {}
    };

    // now apply any params to that
    for (k in params) {
        if (that.hasOwnProperty(k)) {
            that[k] = params[k];
        }
    }

    // sanity check
    if (that.id === false || that.source_url === false) {
        console.log('Hey, we need some default settings here in the datagrid man');
        return false;
    }

    if (that.full_sort_order === false) {
        sort = [[ that.default_sort_col, that.default_sort_order ]];
    } else {
        sort = that.full_sort_order;
    }

    that.instance = $(that.id).dataTable({
        "bProcessing": true,
        "bPaginate" : true,
        "bServerSide": true,
        "bAutoWidth" : false,
        "sAjaxSource" : that.source_url,
        "oAjaxBaseData" : that.data,
        "iDisplayLength": that.default_displaycount,
        "fnDrawCallback": that.draw_callback,
        "oLanguage": { "sProcessing": that.default_loading_msg }, 
        "aaSorting": sort,
        "aoColumns": that.column_data
    }).fnSetFilteringDelay(350);

    that.refresh = function (data) {
        that.instance.fnDraw(data);
    };

    return that;
};

/**
 * This is for defining a tab, but the tab doesn't actually need to fetch
 * content via an ajax call. Honestly, it just gives us a place to track
 * loaded/not and to define the callback we need to run when the tab is
 * activated. The big use case is if a datagrid is defined on a tab, we don't
 * want to keep loading it over and over on each tab click
 *
 * @param params.post_success();
 */
mor.ui.tab = function (params) {
    var that;
    that = {};
    that.loaded = false;
    that.post_success = params.post_success;
    that.busy_message = params.busy_message;

    that.run = function (data) {
        // if it's not loaded go ahead
        if (that.loaded) {
            return false;
        } else {
            // show a message that we're loading
            mor.notice.showMessage(that.busy_message);
            
            if (typeof(that.post_success) == 'function') {
                that.post_success(data);
            }

            that.loaded = true;
            mor.notice.hideMessage();
        }
    };

    return that;

};

mor.ui.highlight = function (id) {
    var highlight_color, highlight_speed, start, original_color;
    highlight_color = "#FFFACD";
    highlight_speed = 5000;

    // if the id starts with a . or a # don't add it
    // else add it
    start = id.substr(0, 1);
    if (start != '.' && start != '#') {
        id = '#' + id;
    }

    original_color = $(id).css('backgroundColor');
    if (original_color == 'transparent') {
        original_color = 'white';
    }

    $(id).animate({backgroundColor: highlight_color}, 0);
    $(id).animate({backgroundColor: original_color}, highlight_speed);
};

mor.ui.remove = function (id, callback) {
    $(id).fadeOut('normal', function () {
        $(this).remove(); 
        callback();
    });
};


/**
 * mor.notice
 * a standard ui for notifying the user on the status of ajax events
 * @todo move the notice to the ui part of mor.
 */
mor.notice = {
    // constants
    html_id: '#mor_notice',
    msg_id: '#mor_notice span',
    default_msg: 'Loading...',
    types: {
        error: { 'class' : 'mor_notice_error',
                 'title' : 'Error!',
                 'icon'  : 'ui-icon-alert'
               },
        notes: { 'class' : 'mor_notice_notes',
                 'title' : 'Please Note:',
                 'icon'  : 'ui-icon-info'
               },
        loading: { 'class' : 'mor_notice_loading',
                   'title' : 'Loading ...',
                   'icon'  : 'ui-icon-circle-check'
                 }
    }, 

    showMessage : function (message, type) {
        var message_string, type_class, type_title;

        // if there is no message/type hit the defaults
        if (message === undefined) {
            message = this.default_msg;
        }

        // if there's not type default to loading
        if (type === undefined) {
            type = this.types.loading;
        }

        message_icon = sprintf('<p class="ui-state-default ui-corner-all" title=".%s" style="float: right;"><span class="ui-icon %s"></span></p>',
                type['icon'],
                type['icon']);
        message_string = sprintf('%s<div class="%s">&nbsp;%s</div>', 
                message_icon,
                type['class'],
                message);

        $(mor.notice.html_id).html(message_string).click(function () {
            mor.notice.hideMessage(); 
        }).show();
    },

    hideMessage : function () {
        $(mor.notice.html_id).hide();
    }

};



mor.ui.modal = function (params) {
    var that, k;

    that = { modal_id : 'mor_modal',
        modal_config : { 
            buttons : {
                Close: function () {
                    $(this).dialog('close');
                }
            }
        }
    };

    // now apply any params to that
    for (k in params) {
        if (params.hasOwnProperty(k)) {
            that[k] = params[k];
        }
    }

    if (params.modal_config) {
        // now apply any params to that
        for (k in params.modal_config) {
            that.modal_config[k] = params.modal_config[k];
        }
    }

    that.set_title = function (title) {
        that.modal_config.title = title;
    };

    that.set_opencallback = function (callback) {
        that.modal_config.open = callback;
    };

    that.set_width = function (width) {
        that.modal_config.width = width;
    };

    that.show = function () {
        $("#" + that.modal_id).dialog(that.modal_config);
    };

    that.create = function (id, title, content) {
        var html;
        that.modal_id = id;
        that.set_title(title);
        html = sprintf('<div class="mor_modal" id="%s" title="%s">%s</div>', 
                id, title, content);
        $('body').append(html);
    };

    return that;

};

// we want some cool jquery themed buttons going on
//<a href="" class="mor_button" 
//           mor_button_icon="ui-icon-pause" 
//           mor_button_text="true">Pause</a>
mor.ui.button = function (params) {
    $('.mor_button').each(function () {
        var $this, settings, icon;
        // get the settings for the button
        $this = $(this);
        settings = {};
        
        if ($this.attr('mor_button_text') == 'true') {
            settings.text = true;
        } else {
            settings.text = false;
        }

        icon = $this.attr('mor_button_icon');
        if (icon) {
            settings.icons = {
                'primary': icon
            };
        }

        // now fire off the button
        $this.button(settings);

    });



    $('.mor_button').live('hover', function (e) { 
            if (e.type ==='mouseenter') {
                $(this).addClass("ui-state-hover"); 
            } else {
                $(this).removeClass("ui-state-hover"); 
            }
        }
    );
};

mor.ui.tabs = function () {

    if ($('div.tabs > ul').length) {
        $("div.tabs").bind('tabsselect', function (event, ui) {
            document.location = '#' + (ui.panel.id);
        });

        $("div.tabs").bind('tabsshow', function (event, ui) {
            // try to fire off the click even for this tab
            var id = sprintf('li.%s a', ui.panel.id);
            $(id).trigger('click');
            mor.form.init();
        });

        // we need to append the #target to each form in a tab
        $('div.tabs > ul > li').each(function () {
            var content_id = $(this).attr('class');
            // find any forms in the tab
            $('#' + content_id + ' form').each(function () {
                var current_action, new_action;
                current_action = $(this).attr('action'); 
                new_action = sprintf('%s#%s', current_action, content_id);
                $(this).attr('action', new_action);
            });
        });

        $("div.tabs").tabs();
        $("div.tabs").show();
    }

};

mor.ui.datepickers = function () {
    var picker_id;

    picker_id = '.datepicker';

    if ($(picker_id).length > 0) {
        $(picker_id).datepicker();
    }

}
