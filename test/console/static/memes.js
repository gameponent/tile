window.onload = function () {

    var canvas = require('canvas');
    var tile = require('tile');

    var screen = new canvas.Canvas({width: 500, height: 500});
    var layer = new canvas.Layer();
    screen.root.addLayer({layer: layer});

    tile.load({url: '/static/assets/tilesets', success: function (options) {
        var tilesets = options.tilesets;
        var rages = tilesets.rages;

        rages.load({success: function () {
            layer.addView({view : new canvas.ImageView({
                image: rages.group({group: 'no'}).tile(),
                x: 100,
                y: 100
            })});

            layer.addView({view : new canvas.ImageView({
                image: rages.group({group: 'scared-yao'}).tile(),
                x: 200,
                y: 100
            })});

            screen.draw();
        }});
        
    }});

};