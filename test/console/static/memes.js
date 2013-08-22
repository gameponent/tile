window.onload = function () {

    var canvas = require('canvas');
    var tile = require('tile');

    var screen = new canvas.Canvas({width: 500, height: 500});
    var layer = new canvas.Layer();
    screen.root.addLayer({layer: layer});

    tile.load({url: '/static/assets/tilesets', success: function (options) {
        window.tilesets = options.tilesets;
    }});

};