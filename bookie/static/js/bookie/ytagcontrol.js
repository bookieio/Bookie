/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */

/**
 * ripped off from https://github.com/yui/yui3-gallery/blob/master/src/gallery-taglist/js/taglist.js
 *
 * Hope to submit to the gallery either as a giant patch or something. For
 * now, will hack it directly into Bookie .
 */

YUI.add('bookie-tagcontrol', function (Y) {
    ns = Y.namespace('bookie');

    var keymap = {
        downArrow:40,
        upArrow:38,
        enter:13,
        space:32,
        tab:9,
        backspace:8
    };

    function Tag(config) {
        Tag.superclass.constructor.apply(this, arguments);
    }

    Tag.NAME = 'TagControllerTag';
    Tag.ATTRS = {
        'text': {},
        'cssClass': {},
        'parent': {}
    };

    Y.extend(Tag, Y.Base, {
        _bind: function () {
            // if clicked on, remove it
            this.ui.on('click', this.destroy, this);
        },

        _buildui: function () {
            var ui = Y.Node.create('<li/>');

            ui.addClass(this.get('cssClass'));
            ui.setContent(this.get('text'));

            return ui;
        },

        destructor: function () {
            Y.fire('tag:removed', {
                target: this
            });
            // remove this node
            this.ui.remove();
        },

        initializer: function (cfg) {
            this.ui = this._buildui();
            this._bind();
        }
    });

    ns.TagControl = Y.Base.create('bookie-tagcontrol', Y.Widget, [], {
        tpl: {
            main: '<div><ul><li><input/></li></ul></div>',
        },

        _add_tag: function () {
            var input = this.ui.one('input'),
                current_text = input.get('value'),
                new_tag = new Tag({
                    text: current_text,
                    cssClass: this.getClassName('item'),
                    parent: this.ui
                });

            // keep this up
            this.get('tags').push(new_tag);

            // add a new li element before the input one
            var parent = input.get('parentNode');
            parent.get('parentNode').insertBefore(new_tag.ui, parent);

            // clear the input
            input.set('value', '');

            // focus on the input
            input.focus();

            this._sync_tags();
        },

        _bind_events: function () {
            // events to watch out for from our little control
            // tag:added
            // tag:removed
            // keyup (is it a space, fire autocomplete...)
            // focus out (make last word a tag)
            this.ui.delegate(
                'keyup',
                this._parse_input,
                'input',
                this
            );

            Y.on('tag:removed', this._remove_tag, this);
        },

        _buildui: function () {
            this.ui = Y.Node.create(this.tpl.main);
            this.ui.one('ul').addClass(this.getClassName('tags'));
            this.ui.one('li').addClass(this.getClassName('item'));
            this.ui.one('input').addClass(this.getClassName('input'));
        },

        _parse_input: function (e) {
            if (e.keyCode == keymap.space || e.keyCode == keymap.enter) {
                // then handle the current input as a tag and clear for a new
                // one
                this._add_tag();
            }
        },

        _remove_tag: function (e) {
            var t = e.target
                tag = t.get('text');
            Y.Array.find(this.get('tags'), function (item, index, list) {
                if (item.get('text') == tag) {
                    var tlist = this.get('tags');
                    tlist.splice(index, 1);
                    this.set('tags', tlist);
                }

                return true;
            }, this);
        },

        _sync_tags: function () {
            // make sure we keep the tags in our list up to date with the
            // input box
            var tag_list = Y.Array.reduce(this.get('tags'), '', function (prev, cur, index, array) {
                if (prev.length > 0) {
                    return [prev, cur.get('text')].join(' ');
                } else {
                    return cur.get('text');
                }
            }, this);

            this.get('srcNode').set('value', tag_list);
        },

        bindUI: function () {
            this._bind_events();
        },

        renderUI: function () {
            // first start out by hiding the initial input and placing our own
            // in it's place
            var target = this.get('srcNode')
            // make the target a hidden field so it still gets passed to forms
            // submitted
            target.set('type', 'hidden');

            this._buildui();
            target.get('parentNode').insertBefore(this.ui);
        },

        syncUI: function () {

        }
    }, {
        ATTRS: {
            tags: {
                value: []
            }
        },
    });


// YUI.add('gallery-tagcontrol', function (Y) {
//     var
//     //function alias'
//     getClassName = Y.ClassNameManager.getClassName,
//     nodeCreate = Y.Node.create,
//
//     //plugin info
//     NAME = 'tagcontrol',
//
//     //contstants
//     DELIM = ',',
//     KEY_BACKSPACE = 8,
//     KEY_ENTER = 13,
//     KEY_COMMA = 188,
//     KEY_SPACE = 32,
//     ENTRY_NAME = 'taglistentry',
//     CSS_CLEARFIX = getClassName('helper', 'clearfix'),
//     CSS_ICON = getClassName('icon'),
//     CSS_ICON_CLOSE = getClassName('icon', 'close'),
//     CSS_ICON_EDIT = getClassName('icon', 'edit'),
//     CSS_ENTRY_HOLDER = getClassName(ENTRY_NAME, 'holder'),
//     CSS_ENTRY_CLOSE = getClassName(ENTRY_NAME, 'close'),
//     CSS_ENTRY_EDIT = getClassName(ENTRY_NAME, 'edit'),
//     CSS_ENTRY_TEXT = getClassName(ENTRY_NAME, 'text'),
//     CSS_ENTRY_ITEM = getClassName(ENTRY_NAME, 'item'),
//     CSS_INPUT_CONTAINER = getClassName(NAME, 'input', 'container'),
//     TPL_ENTRY_CLOSE = '<span class="' + [CSS_ICON, CSS_ICON_CLOSE, CSS_ENTRY_CLOSE].join(' ') + '">Remove</span>',
//     TPL_ENTRY_EDIT = '<span class="' + [CSS_ICON, CSS_ICON_EDIT, CSS_ENTRY_EDIT].join(' ') + '">Edit</span>',
//     TPL_ENTRY_TEXT = '<span class="' + CSS_ENTRY_TEXT + '"></span>',
//     TPL_ENTRY_HOLDER = '<ul class="' + [CSS_CLEARFIX, CSS_ENTRY_HOLDER].join(' ') + '"></ul>',
//     TPL_INPUT_CONTAINER = '<li class="' + CSS_INPUT_CONTAINER + '"></li>';
//
//
//     Y[NAME] = Y.Base.create(NAME, Y.Plugin.Base, [], {
//
//         //the host input field wich is plugged in
//         oldInput: null,
//
//         //the container that holds the new input
//         inputContainer: nodeCreate(TPL_INPUT_CONTAINER),
//
//         //the new input
//         input: nodeCreate('<input>'),
//
//         //the ul container
//         cont: nodeCreate(TPL_ENTRY_HOLDER),
//
//         lis: [],
//
//         entries: [],
//
//         span: nodeCreate('<em></em>'),
//
//         toString: function() {
//             return '[Object ' + NAME + ']';
//         },
//
//         initializer: function() {
//             Y.log('initalizer', 'info', 'Y.' + NAME);
//             this.oldInput = this.get('host');
//             this.entries = [];
//             this.lis = [];
//
//             //start the process
//             this.renderUI();
//             this.bindUI();
//             this.syncUI();
//         },
//
//         destructor: function() {
//             Y.log('destructor', 'info', 'Y.' + NAME);
//             this.oldInput.set('type', 'text');
//             this.input.remove();
//         },
//
//         renderUI: function() {
//             Y.log('render', 'info', 'Y.' + NAME);
//             //add the input item
//             this.inputContainer.appendChild(this.input);
//             this.cont.appendChild(this.inputContainer);
//             this.cont.appendChild(this.span);
//             //make the styles of the span the same as the input, except hidden
//             this.span.setStyles({
//                 visibility: 'hidden',
//                 position: 'absolute',
//                 top: '0',
//                 left: '0'
//             });
//             //set the input values
//             this.oldInput.set('type', 'hidden');
//             this.input.set('value', this.oldInput.get('value'));
//             this.oldInput.get('parentNode').insertBefore(this.cont, this.oldInput);
//         },
//
//         bindUI: function() {
//             Y.log('bind', 'info', 'Y.' + NAME);
//             //the delegated listeners for the edit and delete spans
//             this.cont.delegate('click', this.removeClick, 'span.' + CSS_ENTRY_CLOSE, this);
//             this.cont.delegate('click', this.editClick, 'span.' + CSS_ENTRY_EDIT, this);
//             this.cont.delegate('click', this.editClick, 'span.' + CSS_ENTRY_TEXT, this);
//             //the blur event will do an add check
//             this.input.on('blur', function () {
//                         this.add(false);
//                     }, this);
//             //if the container is clicked, focus on the firld
//             this.cont.on('click', function() {
//                 this.checkWidth();
//                 this.input.focus();
//             }, this);
//             //keypress listeners
//             Y.on('key', this.keyDown, this.input, 'down:' + [KEY_ENTER, KEY_BACKSPACE, KEY_COMMA, KEY_SPACE].join(','), this);
//             //keypress listeners
//             this.input.on('keyup', this.checkWidth, this);
//         },
//
//         syncUI: function() {
//             Y.log('sync', 'info', 'Y.' + NAME);
//             //do an add when we intialise as there may have been content added before the js fired
//             this.add();
//         },
//
//         // Checks if ths string tag is already in one of the tags in the widget.
//         checkTagUnique: function(tag) {
//             var delimString = DELIM + this.oldInput.get('value') + DELIM, unique = (delimString.indexOf(DELIM + tag + DELIM) < 0);
//                     Y.log(tag + ' is ' + unique + ' unique', 'info', 'Y.' + NAME);
//                     return unique;
//         },
//
//         //the add helper method
//         //this does the add
//         _add: function(k) {
//             Y.log('Adding ' + k, 'info', 'Y.' + NAME);
//             var
//                         add = (this.entries.length) ? this.oldInput.get('value') + DELIM + k : k,
//                         li = nodeCreate('<li class="' + CSS_ENTRY_ITEM + '"></li>'),
//                         txt = nodeCreate(TPL_ENTRY_TEXT);
//
//             li.appendChild(txt.set('innerHTML', k));
//             li.appendChild(nodeCreate(TPL_ENTRY_EDIT));
//             li.appendChild(nodeCreate(TPL_ENTRY_CLOSE));
//
//             this.oldInput.set('value', add);
//             this.cont.insert(li, this.inputContainer, "before");
//             this.entries.push(k);
//             this.lis.push(li);
//         },
//
//         add: function(refocusInput) {
//             var
//                         input = this.input.get('value'),
//                         a,
//                         al,
//                         ai;
//             //first we need to clean up the inputs and remove any extra spaces
//             input = input.replace(/, /g, ',');
//             //is there anything to add?
//             if (input.length && this.checkTagUnique(input)) {
//                 a = input.split(',');
//                 for (ai = 0, al = a.length; ai < al; ai += 1) {
//                     this._add(a[ai]);
//                 }
//                 this.input.set('value', '');
//             }
//             this.cont.appendChild(this.inputContainer);
//             if (refocusInput) {
//                 this.input.focus();
//             }
//             this.checkWidth();
//         },
//
//         //get the index of a key in an array
//         _getIndex: function(a, k) {
//             var ai,
//             al = a.length;
//             //use the indexOf method if available
//             if (Array.prototype.hasOwnProperty('indexOf')) {
//                 Y.log('browser indexOf', 'info');
//                 return a.indexOf(k);
//             } else {
//                 //use the manual method
//                 Y.log('manual indexOf', 'info');
//                 for (ai = 0; ai < al; ai += 1) {
//                     if (a[ai] === k) {
//                         return ai;
//                     }
//                 }
//                 return - 1;
//             }
//         },
//
//         remove: function(i) {
//             var k = this.entries[i],
//             r = (i) ? DELIM + k: k;
//             if (k) {
//                 Y.log('removing ' + k, 'info', 'Y.' + NAME);
//                 this.oldInput.set('value', this.oldInput.get('value').replace(r, ''));
//                 this.lis[i].remove();
//                 //remove the li from the display
//                 this.entries.splice(i, 1);
//                 //removes that item from the array of entries
//                 this.lis.splice(i, 1);
//                 //removes that li from the array of lis
//             }
//             this.input.focus();
//             this.checkWidth();
//         },
//
//         removeClick: function(e) {
//             var el = e.target,
//             i = this._getIndex(this.lis, el.get('parentNode'));
//             if (i > -1) {
//                 this.remove(i);
//             }
//         },
//
//         edit: function(i) {
//             var k = this.entries[i];
//             if (k) {
//                 this.cont.insert(this.inputContainer, this.lis[i], "before");
//                 this.input.set('value', k);
//                 this.remove(i);
//             }
//         },
//
//         editClick: function(e) {
//             var el = e.target,
//             i = this._getIndex(this.lis, el.get('parentNode'));
//             if (i > -1) {
//                 this.edit(i);
//             }
//         },
//
//         checkWidth: function() {
//             var entry = this.input.get('value');
//             Y.log('Checking width of input', 'info', 'Y.' + NAME);
//             //use the span as a dummy field
//             this.span.set('innerHTML', entry);
//             //set the width of the input based on the width of the span
//             Y.log(this.span.get('offsetWidth') + 'px', 'info');
//             this.input.setStyle('width', (this.span.get('offsetWidth') + 30) + 'px');
//         },
//
//         keyDown: function(ev) {
//             var
//             keyCode = ev.keyCode,
//             entry = this.input.get('value'),
//             entriesSize = this.entries.length;
//
//             Y.log('Key Press: ' + ev, 'info', 'Y.' + NAME);
//
//             if (!entry) {
//                 //we will allow the enter key to work as per normal, if there is nothing to add
//                 if (keyCode === KEY_ENTER) {
//                     Y.log('Empty enter, do browser default', 'info', 'Y.' + NAME);
//                     return;
//                 }
//                 //dont accept spaces as the first character
//                 if (keyCode === KEY_SPACE) {
//                     Y.log('Empty space, halt event', 'info', 'Y.' + NAME);
//                     ev.halt();
//                 }
//                 //if you're pressing the backspace button, with no input, edit the last entry, if there is one
//                 if (keyCode === KEY_BACKSPACE && entriesSize) {
//                     //we dont want to delete the last character yet
//                     Y.log('Edit the last entry', 'info', 'Y.' + NAME);
//                     ev.halt();
//                     //edit the last one
//                     this.edit(entriesSize - 1);
//                 }
//             }
//
//             if (keyCode === KEY_ENTER || keyCode === KEY_COMMA) {
//                 Y.log('Full enter OR Comma, add entry', 'info', 'Y.' + NAME);
//                 //stop it from happening (that is a comma to appear, or the input to cause a form submit.)
//                 ev.halt();
//                 //we're going to treat these as an add
//                 if (entry) {
//                     this.add(true);
//                 }
//             }
//
//         }
//     },
//     {
//         NS: NAME,
//         ATTRS: {}
//     });
//
// });


}, '0.1.0', { requires: [
    'base', 'widget', 'handlebars', 'array-extras'
] });
