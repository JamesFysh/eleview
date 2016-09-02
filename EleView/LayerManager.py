from processing import getVectorLayers
from processing.core.parameters import ParameterVector


class LayerManager(object):
    def __init__(self):
        self.curr_layer = None
        self.layer_map = {}
        self.layer_attr_map = {}

    def initialize(self):
        # Build layer list
        self.layer_map = {
            str(layer.name()): layer
            for layer in getVectorLayers([ParameterVector.VECTOR_TYPE_LINE])
        }

        # Build layer-attribute list
        for layer_name, layer in self.layer_map.iteritems():
            self.layer_attr_map[layer_name] = {
                field.name(): field
                for field in layer.pendingFields()
            }

    def get_layer_names(self):
        return sorted(self.layer_map.keys())

    def get_layer_by_name(self, layer_name):
        return self.layer_map[layer_name]

    def get_attrs_for_layer(self, layer_name):
        return sorted(self.layer_attr_map[layer_name].keys())
