__all__ = ['config2db']

import OptClim2


def config2db(config, rootDir):
    """setup OptClim2 database from config object"""

    study = config.Config['Name']
    if 'Scenario' not in config.Config:
        raise RuntimeError('Scenario name is not specified in configuration')
    scenario = config.Config['Scenario']
    if 'database' in config.Config:
        db = config.Config['database']
    else:
        db = None

    parameters = {}
    for p in config.Config['Parameters']['minmax']:
        val = config.Config['Parameters']['minmax'][p]
        if not isinstance(val, str):
            parameters[p] = OptClim2.ParameterFloat(val[0], val[1])

    objfun = OptClim2.ObjectiveFunctionResidual(
        study, rootDir, parameters, scenario=scenario, db=db)

    return objfun


if __name__ == '__main__':
    import sys
    from pathlib import Path
    from StudyConfig import readConfig
    from pprint import pprint
    cfg = readConfig(filename=sys.argv[1], ordered=True)

    pprint(cfg.Config["Parameters"])

    parameters = config2db(cfg, Path('/tmp'))

    pprint(parameters)
