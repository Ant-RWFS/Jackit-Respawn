from abc import ABC
from Script.Globals import *


class AbstractUI(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._page = page()
        self._config = config()
        self._file_op = file_op()
        self._cmd = cmd()
        self._evt = evt()
        self._evt_bcst = evt_bcst()
        self._db_op = db_op()
        self._data_ft = data_ft()
        if not all([self._page, self._config]):
            raise RuntimeError(
                "Global dependencies not initialized. "
                "Ensure AppRegistry.register() is called before UI instantiation."
            )

    @property
    def page(self):
        return self._page

    @property
    def config(self):
        return self._config

    @property
    def file_op(self):
        return self._file_op

    @property
    def cmd(self):
        return self._cmd

    @property
    def evt(self):
        return self._evt

    @property
    def evt_bcst(self):
        return self._evt_bcst

    @property
    def db_op(self):
        return self._db_op

    @property
    def data_ft(self):
        return self._data_ft


class AbstractMapReader(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config()

    @property
    def config(self):
        return self._config
