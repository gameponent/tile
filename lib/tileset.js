var TileGroup = require('./tilegroup');

function TileSet(options) {
    this.url = options.url;
    this.groups = options.groups;
}

TileSet.prototype.load = function(options) {
    options = options || {};
    var noop = function () {};
    var success = options.success || noop;
    var error = options.error || noop;
    var that = this;

    this.image = new Image();
    this.image.addEventListener('load', function () {
        that.loadGroups();
        success({tileset: that});
    });

    this.image.setAttribute('src', this.url);
};

TileSet.prototype.loadGroups = function() {
    var groups = {};
    var that = this;

    this.groups.forEach(function (group) {
        var options = group;
        options.image = that.image;

        groups[group.name] = new TileGroup(group);
        groups[group.name].load();
    });

    this.groups = groups;
};

module.exports = TileSet;