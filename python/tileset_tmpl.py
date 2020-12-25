from collections import OrderedDict as OD
import copy

_tmpl = OD({
    'asset':OD({
        'version': '0.0',
        'tilesetVersion': '1.0.0-obj23dtiles',
        'gltfUpAxis': 'Z'
    }),
    'geometricError': 500,
    'root': OD({
        'transform': [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            6378137.0, 0.0, 0.0, 1
        ],
        'boundingVolume': {
            'box': [
                0.0, 0.0, 0.0,
                0.5, 0.0, 0.0,
                0.0, 0.5, 0.0,
                0.0, 0.0, 0.5
            ]
        },
        'geometricError': 1,
        'refine': 'ADD',
        'children': []
    })
})

_tmpl_node = OD({
    'boundingVolume': {
        'box': [
            0.0, 0.0, 0.0,
            0.5, 0.0, 0.0,
            0.0, 0.5, 0.0,
            0.0, 0.0, 0.5
        ]
    },
    'geometricError': 0,
    'content': {
        'uri': ''
    }
})

def get_node():
    return copy.deepcopy(_tmpl_node)
