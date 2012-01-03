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

        _add: function (current_text) {
            var input = this.ui.one('input'),
                parent = input.get('parentNode'),
                new_tag = new Tag({
                    text: current_text,
                    cssClass: this.getClassName('item'),
                    parent: this.ui
                });

            // keep this up
            this.get('tags').push(new_tag);

            // add a new li element before the input one
            parent.get('parentNode').insertBefore(new_tag.ui, parent);
            this._sync_tags();
        },

        _added_tag: function () {
            var input = this.ui.one('input'),
                current_text = input.get('value');

            this._add(current_text);

            // clear the input
            input.set('value', '');

            // focus on the input
            input.focus();
        },

        _bind_events: function () {
            // events to watch out for from our little control
            // tag:added
            // tag:removed
            // focus out (make last word a tag)
            this.ui.delegate(
                'keyup',
                this._parse_input,
                'input',
                this
            );

            // if you click on anywhere within the ui, focus the input box
            this.ui.on('click', function (e) {
                this.ui.one('.' + this.getClassName('input')).focus();
            }, this);

            // if a tag is removed, catch that event and remove it from our
            // knowledge. This event is coming from the tag itself.
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
                this._added_tag();
            }
        },

        _process_existing: function () {
            // check the srcNode for any existing value=""
            var that = this,
                val = Y.Lang.trim(this.get('srcNode').get('value'));
                tags = [];

            if (val.length > 0) {
                tags = val.split(' ');
            }

            if (tags.length > 0) {
                Y.Array.each(tags, function (n) {
                    that._add(n);
                });
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

            // handle init'ing if there are initial values in the input box
            this._process_existing();
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

}, '0.1.0', { requires: [
    'base', 'widget', 'handlebars', 'array-extras'
] });
