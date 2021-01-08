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
    // iTowns namespace defined here
    var viewerDiv = document.getElementById('viewerDiv');

    // iTowns GlobeView
    var placement = {
        coord: new itowns.Coordinates('EPSG:4326', 0.0, 0.0),
        range: 25e6
    }
    var view = new itowns.GlobeView(viewerDiv, placement, {
	noControls : true
    });
    view.camera.camera3D.far = itowns.ellipsoidSizes.x * 30;
    view.camera.resize(viewerDiv.clientWidth, viewerDiv.clientHeight);
    view.mainLoop.gfxEngine.renderer.outputEncoding = itowns.THREE.sRGBEncoding;

    loadGSIColor(view, function () {
        hideAllLayers(view);
        view.notifyChange();
    });

    var grid = new itowns.THREE.GridHelper( 10000000, 10);
    grid.geometry.rotateX(Math.PI / 2);
    view.scene.add(grid);

    var axes = new itowns.THREE.AxesHelper(10000000 * 2);
    view.scene.add(axes);

    const light = new itowns.THREE.HemisphereLight(0xFFFFFF, 0x00000, 1.0);
    view.scene.add(light);

    var controls = new itowns.OrbitControls(view, { focusOnClick: true});

    var done = false;
    view.addFrameRequester(itowns.MAIN_LOOP_EVENTS.AFTER_RENDER, (evt) => {
        if (!done && window.chowder_itowns_view_type === "itowns") {
            var wrap = document.createElement('span');
            wrap.style.position = "absolute";
            wrap.style.left = "30px";
            wrap.style.bottom = "30px";
            wrap.style.zIndex = 1;
            var gridOnOff = document.createElement('input');
            gridOnOff.type = "checkbox"
            gridOnOff.style.width = "20px";
            gridOnOff.style.height = "20px";
            gridOnOff.checked = true;
            wrap.appendChild(gridOnOff)
            var gridText = document.createElement('span');
            gridText.style.fontSize = "16px";
            gridText.style.color = "white"
            gridText.textContent = "Grid On/Off";
            wrap.appendChild(gridText)
            gridOnOff.onchange = function () {
                axes.visible = gridOnOff.checked;
                grid.visible = gridOnOff.checked;
                view.notifyChange();
            };

            document.body.appendChild(wrap)
            done = true;
        }
    });

    injectChOWDER(view, viewerDiv);
};
