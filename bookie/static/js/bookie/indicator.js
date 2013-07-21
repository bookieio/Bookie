/**
 * Hacked up from a stolen version from launchpad. Leaving their copyright.
 * Copyright 2011 Canonical Ltd.  This software is licensed under the
 * GNU Affero General Public License version 3 (see the file LICENSE).
 *
 * Large indicator of pending operations.
 *
 * @namespace bookie
 * @module indicator
 *
 * @example Usage:
 *
 *     Y.bookie.Indicator({
 *         target: Y.one('#id')
 *     });
 *
 */
YUI.add('bookie-indicator', function (Y) {
    var ns = Y.namespace('bookie');

    /**
     * Indicator widget class
     *
     * @class Indicator
     * @extends Y.Widget
     *
     */
    ns.Indicator = Y.Base.create( 'bookie-indicator', Y.Widget, [], {
        initializer: function(cfg) {
            this.hide();
        },

        /**
         * Wire up our event listeners.
         *
         * @method _addListeners
         * @private
         */
        _addListeners: function() {
            this.on('visibleChange', function(e) {
                if (e.newVal === true) {
                    this.resizeAndReposition();
                }
            }, this);
        },

        /**
         * To prevent having to force call sites to pass in
         * parentNode, we must override YUI's built-in _renderUI
         * method.
         *
         * This is a copy of the YUI method, except for using our
         * own parentNode.  This is needed so the spinner overlays
         * correctly.
         *
         * @method _renderUI
         * @private
         */
         _renderUI: function() {
             var local_parent = this.get('target').get('parentNode');
             this._renderBoxClassNames();
             this._renderBox(local_parent);
         },

        /**
         * Build the indicator overlay itself.
         *
         * @method renderUI
         */
        renderUI: function () {
            var node_html = '<img/>';
            var img = Y.Node.create(node_html);
            img.set('src', '/static/images/spinner-big.gif');
            this.get('contentBox').append(img);
        },

        /**
         * Bind the ui events needed to operate this widget.
         *
         * @method bindUI
         *
         */
        bindUI: function() {
            this._addListeners();
        },

        /**
         * Resize and reposition before we show the overlay,
         * to ensure the overlay always matches its target's size/pos.
         *
         * @method resizeAndReposition
         */
        resizeAndReposition: function () {
            var boundingBox = this.get('boundingBox');
            var target = this.get('target');
            var width = target.get('offsetWidth');
            var height = target.get('offsetHeight');
            boundingBox.set('offsetWidth', width);
            boundingBox.set('offsetHeight', height);
            // Now do position too.
            boundingBox.setXY(target.getXY());
        }
    }, {
        ATTRS: {
            /**
             * A reference to the node that we're going to overlay.
             *
             * @attribute target
             * @type Y.Node
             * @default null
             */
            target: {
                value: null
            }
        }
    });

}, '0.1', {
    requires: [
        'base',
        'node-screen',
        'widget'
    ]
});
