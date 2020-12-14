
window.onload = function() {
    /* global itowns,document,GuiTools*/
    var placement = {
        coord: new itowns.Coordinates('EPSG:4326', 0.0, 0.0, 0),
        range: 200,
        tilt: 89.9,
        heading: 0.0
    }
    // iTowns namespace defined here
    var viewerDiv = document.getElementById('viewerDiv');

    var view = new itowns.GlobeView(viewerDiv, placement);
    view.camera.camera3D.near = 1;
    setupLoadingScreen(viewerDiv, view);

    // Create a new Layer 3d-tiles
    // -------------------------------------------
    var $3dTilesLayerTB2C = new itowns.C3DTilesLayer('3d-tiles-tb2c', {
        name: 'TB2C',
        source: new itowns.C3DTilesSource({
            url: 'tileset.json',
        }),
        sseThreshold: 0.05,
    }, view);
    itowns.View.prototype.addLayer.call(view, $3dTilesLayerTB2C);

    injectChOWDER(view, viewerDiv);
};
