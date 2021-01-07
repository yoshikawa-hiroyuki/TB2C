
function hideAllLayers(view) {
    var layers = view.getLayers();
    for (var i = 0; i < layers.length; ++i) {
        layers[i].visible = false;
    }
}

function loadGSIColor(view, callback) {
    itowns.Fetcher.json('./gsi.json').then(function (config) {
        var mapSource = new itowns.TMSSource(config.source);
        var layer = new itowns.ColorLayer(config.id, {
            source: mapSource,
            updateStrategy: {
                type: 3
            },
        });
        view.addLayer(layer);
        if (callback) { callback(); }
    });
}

window.onload = function() {
    /* global itowns,document,GuiTools*/
    var placement = {
        coord: new itowns.Coordinates('EPSG:4326', 0.0, 0.0, 0),
        range: 100,
        //tilt: 89.5,
        //heading: 0.0
    }
    // iTowns namespace defined here
    var viewerDiv = document.getElementById('viewerDiv');

    var view = new itowns.GlobeView(viewerDiv, placement, {
        noControls : true
    });
    view.camera.camera3D.near = 5;
    //setupLoadingScreen(viewerDiv, view);
    view.camera.resize(viewerDiv.clientWidth, viewerDiv.clientHeight);
    view.mainLoop.gfxEngine.renderer.outputEncoding = itowns.THREE.sRGBEncoding;

    loadGSIColor(view, function () {
        hideAllLayers(view);
        view.notifyChange();
    });

    // Create a new Layer 3d-tiles
    // -------------------------------------------
    var $3dTilesLayerTB2C = new itowns.C3DTilesLayer('3dtiles_tb2c', {
        name: 'TB2C',
        source: new itowns.C3DTilesSource({
            url: 'tileset.json',
        }),
        sseThreshold: 0.05,
    }, view);
    itowns.View.prototype.addLayer.call(view, $3dTilesLayerTB2C);

    injectChOWDER(view, viewerDiv);
};
