"""Item types.

This module makes it easier for individual plugins and
parts of Hashmal to use consistent metadata.
"""
from collections import namedtuple, defaultdict

from bitcoin.core import x, lx, b2x, b2lx

from hashmal_lib.core import Transaction, BlockHeader, Block
from base import Plugin, BasePluginUI

RAW_BLOCK_HEADER = 'Raw Block Header'
RAW_BLOCK = 'Raw Block'
RAW_TX = 'Raw Transaction'

class Item(object):
    """A value and metadata."""
    name = ''
    @classmethod
    def is_item(cls, data):
        """Returns whether data is of this item type."""
        pass

    @classmethod
    def coerce_item(cls, data):
        """Attempt to coerce data into an item of this type."""
        return None

    def __init__(self, value):
        self.value = value

    def raw(self):
        """Returns the raw representation of this item, if applicable."""
        pass

# This named tuple should be used by plugins when augmenting item actions.
ItemAction = namedtuple('ItemAction', ('plugin_name', 'item_type', 'label', 'func'))

# List of Item subclasses.
item_types = []
# List of ItemAction instances.
item_actions = []

def instantiate_item(data):
    """Attempt to instantiate an item with the value of data."""
    for i in item_types:
        instance = i.coerce_item(data)
        if instance is not None:
            return instance

def get_actions(name):
    """Get actions for an item type.

    Returns:
        A list of dicts of the form:
            {plugin_name: [(action_label, action_function), ...]}
    """
    actions = defaultdict(list)
    for i in item_actions:
        if i.item_type == name:
            actions[i.plugin_name].append( (i.label, i.func) )

    return actions

class TxItem(Item):
    name = 'Transaction'
    @classmethod
    def coerce_item(cls, data):
        # Coerce binary string.
        def coerce_string(v):
            return Transaction.deserialize(v)

        # Coerce hex string.
        def coerce_hex_string(v):
            return Transaction.deserialize(x(v))

        # Coerce transaction instance.
        def coerce_tx(v):
            return Transaction.from_tx(v)

        for i in [coerce_string, coerce_hex_string, coerce_tx]:
            try:
                value = i(data)
            except Exception:
                continue
            else:
                if value:
                    return cls(value)

    def raw(self):
        return b2x(self.value.serialize())
item_types.append(TxItem)

class BlockItem(Item):
    name = 'Block'
    @classmethod
    def coerce_item(cls, data):
        # Coerce binary string.
        def coerce_string(v):
            return Block.deserialize(v)

        # Coerce hex string.
        def coerce_hex_string(v):
            return Block.deserialize(x(v))

        # Coerce block instance.
        def coerce_block(v):
            return Block.from_block(v)

        for i in [coerce_string, coerce_hex_string, coerce_block]:
            try:
                value = i(data)
            except Exception:
                continue
            else:
                if value:
                    return cls(value)

    def raw(self):
        return b2x(self.value.serialize())
item_types.append(BlockItem)

class BlockHeaderItem(Item):
    name = 'Block Header'
    @classmethod
    def coerce_item(cls, data):
        # Coerce binary string.
        def coerce_string(v):
            return BlockHeader.deserialize(v)

        # Coerce hex string.
        def coerce_hex_string(v):
            return BlockHeader.deserialize(x(v))

        # Coerce block header instance.
        def coerce_header(v):
            return BlockHeader.from_header(v)

        for i in [coerce_string, coerce_hex_string, coerce_header]:
            try:
                value = i(data)
            except Exception:
                continue
            else:
                if value:
                    return cls(value)

    def raw(self):
        return b2x(self.value.serialize())
item_types.append(BlockHeaderItem)


def make_plugin():
    p = Plugin(ItemsPlugin)
    p.has_gui = False
    p.instantiate_item = instantiate_item
    p.get_item_actions = get_actions
    return p

class ItemsPlugin(BasePluginUI):
    """For augmentation purposes, we use a plugin to help with item types."""
    tool_name = 'Item Types'
    description = 'Helps handle data that is of a certain type.'

    def __init__(self, *args):
        super(ItemsPlugin, self).__init__(*args)
        self.augment('item_types', None, callback=self.on_item_types_augmented)
        self.augment('item_actions', None, callback=self.on_item_actions_augmented)

    def on_item_types_augmented(self, data):
        try:
            for i in data:
                if issubclass(i, Item):
                    item_types.append(i)
        except Exception:
            # data is not an iterable.
            if issubclass(data, Item):
                item_types.append(data)

    def on_item_actions_augmented(self, data):
        if isinstance(data, ItemAction):
            item_actions.append(data)
            return
        # If iterable, iterate.
        for i in data:
            if isinstance(i, ItemAction):
                item_actions.append(i)
