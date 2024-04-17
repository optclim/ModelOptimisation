__all__ = ['UKESM']

import logging
from typing import Any, Dict
import re

from .model import SimpleNamelistValue, NamelistModel


def _process_config(config, parameters):
    # process configuration by replacing parameters in selected
    # sections
    for sct in parameters:
        # find the start of the section
        section_start = config.find(f'[namelist:{sct}]')
        if section_start > -1:
            # found the section
            section_end = config.find('[', section_start + 1)
            if section_end == -1:
                section_end = None

            section = config[section_start:section_end]
            # only deal with the single section
            for key in parameters[sct]:
                param = re.search(f'^{key}=(.*)$', section, flags=re.M)
                if param is not None:
                    # found the parameter
                    if isinstance(parameters[sct][key], bool):
                        if parameters[sct][key]:
                            newval = '.true.'
                        else:
                            newval = '.false.'
                    elif isinstance(parameters[sct][key], (int, float)):
                        newval = str(parameters[sct][key])
                    else:
                        raise TypeError(
                            f'cannot handle value for {sct}[{key}]')
                    section = section[:param.start(1)]\
                        + newval\
                        + section[param.end(1):]

            # reassemble configuration string
            if section_end is not None:
                config = config[:section_start] + section\
                    + config[section_end:]
            else:
                config = config[:section_start] + section

    return config


class UKESM(NamelistModel):
    NAMELIST_MAP = {
        'iau_nontrop_max_p': SimpleNamelistValue(
            'app/um/rose-app.conf', 'iau_nl', 'iau_nontrop_max_p'),
        'diagcloud_qn_compregimelimit': SimpleNamelistValue(
            'app/um/rose-app.conf', 'iau_nl', 'diagcloud_qn_compregimelimit'),
        'DP_CORR_STRAT':SimpleNamelistValue( 
            'app/um/rose-app.conf', 'run_radiation','dp_corr_strat'),
        'TWO_D_FSD_FACTOR':SimpleNamelistValue(
            'app/um/rose-app.conf','run_radiation','two_d_fsd_factor'),
        'ENT_FAC_DP':SimpleNamelistValue(
            'app/um/rose-app.conf','run_convection','ent_fac_dp'),
        'AI':SimpleNamelistValue(
            'app/um/rose-app.conf','run_precip','ai') }

    def write_params(self, params: Dict[str, Any]) -> None:
        output = self.process_params(params)

        # write output files
        for cfg in output:
            cfgname = self.directory / cfg
            if cfgname.exists():
                config = _process_config(cfgname.read_text(), output[cfg])
                # create a backup
                old = cfgname.with_suffix('.conf~')
                cfgname.replace(old)
                # and write the new configuration
                cfgname.write_text(config)
            else:
                logging.warning(f'no configuration file {cfgname}')
