__all__ = ['NMLValue', 'BaseNamelistValue', 'SimpleNamelistValue',
           'NamelistModel']

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence, Dict
from pathlib import Path
import logging
import f90nml


@dataclass
class NMLValue:
    nmlfile: Path
    nmlgroup: str
    nmlkey: str
    value: Any


class BaseNamelistValue:
    @abstractmethod
    def __call__(self, value) -> Sequence[NMLValue]:
        pass


class SimpleNamelistValue(BaseNamelistValue):
    def __init__(self, nmlfile: Path, nmlgroup: str, nmlkey: str):
        self._nmlfile = nmlfile
        self._nmlgroup = nmlgroup
        self._nmlkey = nmlkey

    def __call__(self, value: any) -> Sequence[NMLValue]:
        return [NMLValue(nmlfile=self._nmlfile,
                         nmlgroup=self._nmlgroup,
                         nmlkey=self._nmlkey,
                         value=value)]


class NamelistModel:
    NAMELIST_MAP = {}

    def __init__(self, directory: Path):
        self._directory = directory

    @property
    def directory(self) -> Path:
        return self._directory

    def process_params(self, params: Dict[str, Any]) -> \
            Dict[Path, Dict[str, Dict[str, Any]]]:
        output = {}
        # map input parameters to output namelist files
        for key in params:
            if key not in self.NAMELIST_MAP:
                raise LookupError(f'parameter {key} not mapped to namelist')
            for nml in self.NAMELIST_MAP[key](params[key]):
                if nml.nmlfile not in output:
                    output[nml.nmlfile] = {}
                if nml.nmlgroup not in output[nml.nmlfile]:
                    output[nml.nmlfile][nml.nmlgroup] = {}
                output[nml.nmlfile][nml.nmlgroup][nml.nmlkey] = nml.value
        return output

    def write_params(self, params: Dict[str, Any]) -> None:
        output = self.process_params(params)

        # write output namelist files
        for nml in output:
            nmlname = self.directory / nml
            if nmlname.exists():
                old = nmlname.with_suffix('.nml~')
                nmlname.replace(old)
                f90nml.patch(old, output[nml], nmlname)
            else:
                logging.warning(f'no namelist file {nmlname}')
