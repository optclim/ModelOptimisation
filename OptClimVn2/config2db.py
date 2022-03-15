__all__ = ['config2db']

import ObjectiveFunction


def config2db(config, rootDir):
    """setup ObjectiveFunction database from config object"""

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
            opt = config.Config['Parameters']['optimumParams'][p]
            parameters[p] = ObjectiveFunction.ParameterFloat(opt, val[0], val[1])

    targets = {}
    for t in config.Config['targets']:
        try:
            v = float(config.Config['targets'][t])
        except:
            continue
        if t in config.Config['study']['ObsList'] \
           or t == config.Config['study']['constraintName']:                 
            targets[t] = v

    objfun = ObjectiveFunction.ObjectiveFunctionSimObs(
        study, rootDir, parameters, list(targets.keys()),
        scenario=scenario, db=db, prelim=False)

    return objfun


if __name__ == '__main__':
    import sys
    from pathlib import Path
    from StudyConfig import readConfig
    from pprint import pprint
    cfg = readConfig(filename=sys.argv[1], ordered=True)

    pprint(cfg.Config["Parameters"])

    objfun = config2db(cfg, Path('/tmp'))

    pprint(objfun)
