/*jslint eqeqeq: false, browser: true, debug: true, onevar: true , plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, HoverDiv: false, jslog: false */

/**
 * JS Functions and Wrappers used for the mor Framework
 * 
 * Tests should be written in the /javascript/tests directory
 *
*/

// if there's no firebug turned on then catch and stop errors from 
// console.log
if (! ('console' in window)) {  
    var names, def, name_len;

    names = ['log', 'debug', 'info', 'warn', 'error', 'assert', 'dir', 'dirxml', 'group', 'groupEnd', 'time', 'timeEnd', 'count', 'trace', 'profile', 'profileEnd'];  
    window.console = {};  

    def = function () {};
    name_len = names.length;
    for (var i = 0; i < name_len; ++i) {
        window.console[names[i]] = def;
    }
}



/*
 *
 *  Javascript sprintf
 *  http://www.webtoolkit.info/
 */
var sprintfWrapper = {


    init : function () {
        var string, exp, matches, strings, convCount, stringPosStart, stringPosEnd, matchPosEnd, newString, match, code, i, substitution;

        if (typeof arguments == "undefined") { 
            return null; 
        }
        if (arguments.length < 1) { 
            return null; 
        }
        if (typeof arguments[0] != "string") { 
            return null; 
        }
        if (typeof RegExp == "undefined") { 
            return null; 
        }

        string = arguments[0];
        exp = new RegExp(/(%([%]|(\-)?(\+|\x20)?(0)?(\d+)?(\.(\d)?)?([bcdfosxX])))/g);
        matches = [];
        strings = [];
        convCount = 0;
        stringPosStart = 0;
        stringPosEnd = 0;
        matchPosEnd = 0;
        newString = '';
        match = null;

        while ((match = exp.exec(string))) {
            if (match[9] !== undefined) { 
                convCount += 1; 
            }

            stringPosStart = matchPosEnd;
            stringPosEnd = exp.lastIndex - match[0].length;
            strings[strings.length] = string.substring(stringPosStart, stringPosEnd);

            matchPosEnd = exp.lastIndex;
            matches[matches.length] = {
                match: match[0],
                left: match[3] ? true : false,
                sign: match[4] || '',
                pad: match[5] || ' ',
                min: match[6] || 0,
                precision: match[8],
                code: match[9] || '%',
                negative: parseInt(arguments[convCount], 10) < 0 ? true : false,
                argument: String(arguments[convCount])
            };
        }
        strings[strings.length] = string.substring(matchPosEnd);

        if (matches.length === 0) { 
            return string; 
        }
        if ((arguments.length - 1) < convCount) { 
            return null; 
        }

        code = null;
        match = null;
        i = null;

        for (i = 0; i < matches.length; i++) {

            if (matches[i].code == '%') { 
                substitution = '%'; 
            }
            else if (matches[i].code == 'b') {
                matches[i].argument = String(Math.abs(parseInt(matches[i].argument, 10)).toString(2));
                substitution = sprintfWrapper.converts(matches[i], true);
            }
            else if (matches[i].code == 'c') {
                matches[i].argument = String(String.fromCharCode(parseInt(Math.abs(parseInt(matches[i].argument, 10)), 10)));
                substitution = sprintfWrapper.converts(matches[i], true);
            }
            else if (matches[i].code == 'd') {
                matches[i].argument = String(Math.abs(parseInt(matches[i].argument, 10)));
                substitution = sprintfWrapper.converts(matches[i], false);
            }
            else if (matches[i].code == 'f') {
                matches[i].argument = String(Math.abs(parseFloat(matches[i].argument)).toFixed(matches[i].precision ? matches[i].precision : 6));
                substitution = sprintfWrapper.converts(matches[i], false);
            }
            else if (matches[i].code == 'o') {
                matches[i].argument = String(Math.abs(parseInt(matches[i].argument, 10)).toString(8));
                substitution = sprintfWrapper.converts(matches[i], false);
            }
            else if (matches[i].code == 's') {
                matches[i].argument = matches[i].argument.substring(0, matches[i].precision ? matches[i].precision : matches[i].argument.length);
                substitution = sprintfWrapper.converts(matches[i], true);
            }
            else if (matches[i].code == 'x') {
                matches[i].argument = String(Math.abs(parseInt(matches[i].argument, 10)).toString(16));
                substitution = sprintfWrapper.converts(matches[i], false);
            }
            else if (matches[i].code == 'X') {
                matches[i].argument = String(Math.abs(parseInt(matches[i].argument, 10)).toString(16));
                substitution = sprintfWrapper.converts(matches[i], false).toUpperCase();
            }
            else {
                substitution = matches[i].match;
            }

            newString += strings[i];
            newString += substitution;

        }
        newString += strings[i];

        return newString;

    },

    converts : function (match, nosign) {
        var l, pad;
        if (nosign) {
            match.sign = '';
        } else {
            match.sign = match.negative ? '-' : match.sign;
        }
        l = match.min - match.argument.length + 1 - match.sign.length;
        pad = new Array(l < 0 ? 0 : l).join(match.pad);
        if (!match.left) {
            if (match.pad == "0" || nosign) {
                return match.sign + pad + match.argument;
            } else {
                return pad + match.sign + match.argument;
            }
        } else {
            if (match.pad == "0" || nosign) {
                return match.sign + match.argument + pad.replace(/0/g, ' ');
            } else {
                return match.sign + match.argument + pad;
            }
        }
    }
};

var sprintf = sprintfWrapper.init;

var mor = {

    // Use this for if( a in array_values(somearray) ) {}
    array_values : function (a) {
        var o, i;
        o = {};

        for (i = 0; i < a.length; i++) {
            o[a[i]] = '';
        }
        return o;
    },

    /**
     * mor.generate_password
     * a password generation script used to create a password for the 
     * user and affiliate creation
     *
     */
    generate_password : function () {
        var chars, chars_len, pass, pass_len, x, i;

        chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789";
        chars_len = chars.length;
        pass_len = 8;
        
        pass = "";
        for (x = 0; x < pass_len; x++) {
            i = Math.floor(Math.random() * chars_len);
            pass += chars.charAt(i);
        }

        return pass;

    }

};

$(document).ajaxError(function (event, XMLHttpRequest, ajaxOptions, thrownError) {
    var url, responseText, response, error_data, log;

    url = arguments[2].url;
    responseText = arguments[1].responseText;

    String.prototype.cleanMessage = function () {
        var newlines, newline, crap, start, matchTag;

        // first get me some newlines
        newlines = /(<br>|<br\/>|<br \/>)/g;
        newline = this.replace(newlines, "\n");

        // some initial matches
        crap = /(&lt;|&gt;|&nbsp;)/g;
        start = newline.replace(crap, "");

        // What a tag looks like
        matchTag = /<(?:.|\s)*?>/g;
        // Replace the tag
        return start.replace(matchTag, "");
    };

    response = responseText.cleanMessage();
   
    // we don't want to be logging our logging
    if (url.indexOf('jslog') == -1) {

        if (window.console && window.console.error) {
            console.log(url);
            console.log(response);

        }

        error_data = {
            'message': 'Ajax Error!',
            'payload': {
                'url': url,
                'response' : response
            }
        };

        log = mor.jslog();
        log.logAjaxError(error_data);
        return false;
    } else {
        return false;
    }
});

/**
 * Page inits we need on page loads
 */
$(document).ready(function () {

    // setup any tabs in the current ui
    mor.ui.tabs();

    // setup the ui buttons
    mor.ui.button();

    mor.ui.datepickers();

    // set the form elements
    //mor.form.init();

    // make all admin links have a lock by them
    // $('li.admin a').append('<img class="adminlock" src="/images/lock_10px.png" />');
    // $('a.admin').append('<img class="adminlock" src="/images/lock_10px.png" />');
    // $('tr.admin th.admin').append('<img class="adminlock" src="/images/lock_10px.png" />');
    // $('span.admin').append('<img class="adminlock" src="/images/lock_10px.png" />');

    // // if the flash message is set then hide it
    // $("#flash_message").animate({opacity: 1.0}, 4000).fadeOut('slow', function () {
    //     $(this).remove();
    // });
});
