from hamcrest.library.text.substringmatcher import SubstringMatcher
from hamcrest.core.helpers.hasmethod import hasmethod

class StringContainsInsensitive(SubstringMatcher):

    def __init__(self, substring):
        super(StringContainsInsensitive, self).__init__(substring)

    def _matches(self, item):
        if not hasmethod(item, 'lower'):
            return False
        low = item.lower()
        if not hasmethod(low, 'find'):
            return False
        return low.find(self.substring.lower()) >= 0

    def relationship(self):
        return 'containing (case-insensitively)'

def contains_insensitive_string(substring):
    return StringContainsInsensitive(substring)
