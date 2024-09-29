"""Class implementing an id generator."""
import itertools

class IdGenerator:
    """
    Class which generates an id when requested and keeps track of issued
    ids.
    """

    id_iter = itertools.count()

    def __init__(self):
        self.__id = next(IdGenerator.id_iter)

    @property
    def get_id(self):
        return self.__id
