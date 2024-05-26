class BiDict:
    def __init__(self, values: dict):
        self.forward = {}
        self.backward = {}

        for k, v in values.items():
            self.forward[k] = v
            self.backward[v] = k

    def __setitem__(self, key, value):
        # Remove existing reverse mappings if necessary
        if key in self.forward:
            old_value = self.forward[key]
            del self.backward[old_value]
        if value in self.backward:
            old_key = self.backward[value]
            del self.forward[old_key]

        self.forward[key] = value
        self.backward[value] = key

    def __getitem__(self, key):
        return self.forward[key]

    def value(self, key, default=None):
        """Returns the value, mapped by the given key."""
        return self.forward.get(key, default)

    def key(self, value, default=None):
        """Returns the key, mapped by the given value."""
        return self.backward.get(value, default)

    def __delitem__(self, key):
        value = self.forward[key]
        del self.forward[key]
        del self.backward[value]

    def __contains__(self, key):
        return key in self.forward

    def __repr__(self):
        return f'{self.__class__.__name__}({self.forward})'
