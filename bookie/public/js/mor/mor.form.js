/*jslint eqeqeq: false, browser: true, debug: true, onevar: true
, plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false */


mor.form = {};

/**
 * The init function will process a form and make it all pretty per our specs
 * We need to make sure we don't rerun parts of this on forms that we've already
 * processed
 */
mor.form.init = function () {

    var defaultvalue;

    // only run the form init if there's a form to run it on
    if ($('fieldset').length > 0) {

        mor.form.prepfieldset();

        mor.form.mark_adminfields();
        mor.form.maxlabels();
        mor.form.addhelptext();
        mor.form.adderrortext();

        mor.form.addfieldsetmin();
        mor.form.focushooks();
        mor.form.date_elements();
    }

    mor.form.default_input();
};

mor.form.prepfieldset = function () {
    $("fieldset li input[type='hidden']").each(function () {
        // if this is a hidden element, then mark the li as hidden so it
        // doesn't count towards zebra/etc
        // checkboxes mess this up since we have a hidden input for each
        // checkbox. Check the parent for a checkbox elemement with the same
        // name first
        var input_name = $(this).attr('name');

        if ($(this).parent().find('input[name=' + input_name + '][type!=hidden]').length > 0) {
            // don't hide this parent, something is visible inside of it
        } else {
            $(this).parent().hide();
        }
    });

    $('fieldset').addClass('ui-corner-all');
};

mor.form.mark_adminfields = function () {
    $('form img.adminlock').remove();

    $('label.admin').append('<img class="adminlock" src="/images/lock_10px.png" />');

    // on the ordered list the class is going on the li vs the label
    $('li.admin').find('label').append('<img class="adminlock" src="/images/lock_10px.png" />');
};

/**
 * mor.form.maxlabels
 * Set the width of the labels on the html form to proper size based on the
 * largest element. Makes things nice and justified
 *
 * Note: needs to be run when a tab or items that is hidden is shown
 */
mor.form.maxlabels = function () {
    var submit_label, $parent, forms_formatted;


    // the one off button we need to fix is the submit button which has no label
    // go ahead and add it in just for show
    submit_label = '<label for="submit">&nbsp;</label>';

    // first make sure we don't already have a label
    $parent = $('input[name="submit"]').parent();
    $parent.each(function () {

        if ($(this).find('label').length === 0) {
            $(this).prepend(submit_label);
        }
    });

    $parent = $('input[name="submit_continue"]').parent();
    $parent.each(function () {

        if ($(this).find('label').length === 0) {
            $(this).prepend(submit_label);
        }
    });


    // we want to do this for each form on the page
    $('form').each(function () {
        // first check out if we have already formatted this form
        if (mor.form.maxlabels.forms_formatted[$(this).attr('id')] == undefined) {

            // only do it if the form is visible
            if ($(this).is(':visible')) {
                // we're formatting this one time only
                mor.form.maxlabels.forms_formatted[$(this).attr('id')] = true;

                var max, id;
                max = 100;
                id = sprintf("form#%s label", $(this).attr('id'));
                $(id).each(function () {
                    if ($(this).width() > max) {
                        max = $(this).width();
                    }
                });

                // add 20px for any potential admin fields padlock
                max = max + 20;
                if ($(id).length > 0) {
                    $(id).width(max);
                }
            }
        } else {
            // short circuit and don't format
        }
    });
};
mor.form.maxlabels.forms_formatted = {};


/**
 * Bind an event to show the help text on mouse enter
 * and to remove the text on mouseout
 */
mor.form.addhelptext = function () {
    var run;

    run = function ($this) {
        var $help_obj, pos, in_event, out_event;
        in_event = 'mouseover';
        out_event = 'mouseout';

        $help_obj = $this.parent().find('span.helptext');

        // hidden elements are outside of a <li> so they trigger funny behavior,
        // just make sure we're only getting one element
        if ($help_obj.length == 1 && $help_obj.html() !== '') {

            $this.bind(in_event, {input: $this, obj: $help_obj}, function (e) {
                pos = e.data.input.position();
                e.data.obj.css('top', pos.top);
                e.data.obj.css('left', pos.left + e.data.input.width() + 20);
                e.data.obj.css('display', 'block');
            });

            $this.bind(out_event, {obj: $help_obj}, function (e) {
                e.data.obj.css('display', 'none');

            });
        } else {
            // skip it
        }

    };

    $('fieldset input').each(function () {
        run($(this));
    });

    $('fieldset div.multiplecheckbox').each(function () {
        run($(this));
    });

    $('fieldset textarea').each(function () {
        run($(this));
    });

    $('fieldset select').each(function () {
        run($(this));
    });
};

/**
 * Show any fields with errors with a nice error text
 *
 */
mor.form.adderrortext = function () {

    $('span.errortext').each(function () {

        if ($(this).html().length > 2) {
            // we have to move this to get around formencode not outputting
            // error text 'after' the input for file inputs
            $(this).parent().append($(this));
            $(this).show();
        }
    });
};

/**
 * Add a visual element to allow us to hide/show the ordered list inside the
 * fieldset of a form
 * This way we can open/close parts of the form
 * NOTICE: This is the one item so far we can't repeat as we load other forms
 * into the page via ajax calls. Check for the images first
 */
mor.form.addfieldsetmin = function () {
    var action_html, list, $list;

//    action_html = '&nbsp;<img src="/images/toggle_div.png" class="mor_togglefieldset" />';

    // check that we have more than one fieldset per form
    // if we do then allow us to toggle the fieldset
    $('form').each(function () {
        if ($(this).find('.fieldset_legend').length > 1) {
        //&& $(this).find('img.mor_togglefieldset').length === 0) {

            //$(this).find('.fieldset_legend').append(action_html);

            $(this).find('fieldset').each(function () {

                $(this).find('.fieldset_legend').unbind('click').bind('click', {fieldset: $(this)}, function (e) {
                    list = e.data.fieldset.find('ol');
                    $list = $(list);

                    if ($list.is(':visible')) {
                        $list.hide();
                    } else {
                        $list.show();
                        // mor.form.zebra();
                    }

                }).addClass('collapsible');
            });
        }
    });
};

mor.form.focushooks = function () {
    var defaultvalue, addfocus, addmousedown, addblur;

    addfocus = function (id, catchevent, select) {
        select = typeof(select) != 'undefined' ? select : true;

        if (id == "textarea") {
            select = false;
        }

        // by default safari and chrome will unselect so this should prevent
        // that
        $(id).mouseup(function (e) {
            e.preventDefault();
        });

        $(id).bind(catchevent, function () {
            defaultvalue = $(this).attr('defaultvalue');

            $(this).removeClass("idlefield").addClass("focusfield");
            if (defaultvalue && ($(this).val() === defaultvalue)) {
                this.value = '';
            }

            if (select && $(this).val !== defaultvalue) {
                this.select();
            }
        });
    };

    addblur = function (id, catchevent) {
        $(id).bind(catchevent, function () {
            defaultvalue = $(this).attr('defaultvalue');

            $(this).removeClass("focusfield").addClass("idlefield");
            //if ($.trim(this.value == '')){
            if (this.value === '' && $(this).attr('defaultvalue')) {
                this.value = $(this).attr('defaultvalue');
            }
        });
    };

    addfocus('input[type="text"]', 'focus');
    addblur('input[type="text"]', 'blur');
    $('input[type="text"]').addClass("idlefield");

    addfocus('input[type="password"]', 'focus');
    addblur('input[type="password"]', 'blur');
    $('input[type="password"]').addClass("idlefield");

    addfocus('input[type="checkbox"]', 'mouseover');
    addblur('input[type="checkbox"]', 'mouseout');
    $('input[type="checkbox"]').addClass("idlefield");

    addfocus('textarea', 'focus');
    addblur('textarea', 'blur');
    $('textarea').addClass("idlefield");

    addfocus('select', 'mousedown', false);
    addblur('select', 'blur');
    $('select').addClass("idlefield");
};

mor.form.date_elements = function () {
    var width, $cal;
    if ($('.mor_date_input').length) {
        $('.mor_date_input').each(function () {

            // first add the span for the icon
            // only append if it's not already there
            $cal = $(this).parent().find('.ui-icon-calendar');

            if ($cal.isDateBound !== true) {
                width = $(this).width();
                $(this).width(width - 20);

                // now make this a datepicker
                $(this).datepicker();

                $cal.bind('click', {datepicker : $(this)}, function (e) {
                    e.data.datepicker.datepicker('show');
                });

                $($cal).parent().hover(
                    function () {
                        $(this).addClass("ui-state-hover").css('cursor', 'pointer');
                    },
                    function () {
                        $(this).removeClass("ui-state-hover").css('cursor', '');
                    }
                );

                $cal.isDateBound = true;

            }
        });
    }
};

/**
 * Find all input elements with an attrib of mor_default
 * and if there's no value, set it to that default. If the user clicks in there,
 * remove the default
 * if empty when leaving, replace it
 *
 * target: attr = mor_default
 * class: mor_default
 */
mor.form.default_input = function () {

    $('[mor_default]').each(function () {
        var default_value, current_value, $this;

        $this = $(this);

        // first, get the default value
        default_value = $this.attr('mor_default');

        // check for current value in the input
        if ($this.val() === "" || $this.val() == default_value) {
            // set the default
            $this.addClass('mor_default').val(default_value);
        } else {
            // leave the current value
            $this.removeClass('mor_default');
        }

        $this.unbind('focus');

        // bind a function to clear the value once the field is clicked on
        $this.bind('focus', { 'default_value' : default_value }, function (e) {
            $this = $(this);

            if ($this.val() == e.data.default_value) {
                // if the default, blank it
                $this.val("").removeClass('mor_default');
            } else {
                // leave the current value
                $this.removeClass('mor_default');
            }
        });


        $this.unbind('blur');
        // now bind a onblur to check if we should restore the value or not
        $this.bind('blur', { 'default_value' : default_value }, function (e) {
            $this = $(this);
            if ($this.val() === "" || $this.val() == e.data.default_value) {
                // set the default
                $this.addClass('mor_default').val(e.data.default_value);
            } else {
                // leave the current value
                $this.removeClass('mor_default');
            }
        });


    });
};



// mor.form.zebra = function () {
//     mor.ui.zebra({ rowtarget : 'li' });
// };
