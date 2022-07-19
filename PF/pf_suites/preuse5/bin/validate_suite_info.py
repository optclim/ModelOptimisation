#!/usr/bin/env python2.7
# (C) British Crown Copyright 2017-18, Met Office.
"""
A tool to check CMIP6 meta data in rose-suite.info against the
CMIP6 controlled vocabulary
"""

import json
import subprocess
import os
import sys

ROSE_HOME = os.environ.get('ROSE_HOME', 'ROSE_HOME is not available')
sys.path.append(os.path.join(ROSE_HOME, 'lib', 'python'))
import rose.config

CV_URL_TEMPLATE = ('https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs'
                   '/{0}/CMIP6_{1}.json')


# simple functions used for comparisons
def _default(i, j):
    """
    Return True if i == j.
    """
    return i == j


def _start_year_check(received, expected):
    """
    Return True if either is blank or they are the same.
    """
    if '' in [received, expected]:
        return True
    else:
        return received == expected


def _end_year_check(received, expected):
    """
    Return True if either is blank or the received value is
    exactly one year after than the expected. This is to ensure that
    the whole of the final year is included.
    """
    if '' in [received, expected]:
        return True
    elif 'or' in expected:
        end_years = [int(i) for i in expected.split(' ')[::2]]
        return int(received) - 1 in end_years
    else:
        return int(received) - 1 == int(expected)


def _default0(i, j):
    """
    Return True if i is the same as the first element of list j.
    """
    return i == j[0]


def _all_i_in_j(i, j):
    """
    Return True if all elements in csv list in i are in the list j.
    """
    return all([k in i.split(",") for k in j])


def _i_in_j(i, j):
    """
    Return True if i is in list j.
    """
    return i in j


def _year_from_date(date):
    """
    Extract year from a date string.
    """
    return date[:4]


def _dummy(i):
    """
    Dummy function that does nothing.
    """
    return i


def _no_parent(i):
    """
    Replace None in suite metadata with "no parent"
    """
    if i == 'None':
        return 'no parent'
    else:
        return i


def check_experiment(suite_info, cv_experiment_id):
    """
    Check through the experiment suite_info supplied and compare to the
    controlled vocabulary.

    Parameters
    ----------
    suite_info : rose.config.ConfigNode
        Suite information loaded from rose-suite.info.
    cv_experiment_id : dict
        Controlled Vocabulary dictionary for experiment_ids.

    Returns
    -------
    list
        list of errors
    """
    #              (suite key, preprocessing function):
    #              (CV key, comparison_function)
    key_mapping = {('MIP', _dummy):
                   ('activity_id', _i_in_j),
                   ('start-date', _year_from_date):
                   ('start_year', _start_year_check),
                   ('end-date', _year_from_date):
                   ('end_year', _end_year_check),
                   ('parent-experiment-mip', _no_parent):
                   ('parent_activity_id', _default0),
                   ('parent-experiment-id', _no_parent):
                   ('parent_experiment_id', _default0),
                   ('source-type', _dummy):
                   ('required_model_components', _all_i_in_j),
                   ('sub-experiment-id', _dummy):
                   ('sub_experiment_id', _all_i_in_j)}
    # Make suite config a little easier to deal with
    suite_config = {}
    for key, value in suite_info.value.items():
        if value.state == '':
            suite_config[key] = value.value

    error_list = []
    warnings_list = []
    # check experiment_id
    experiment_id = suite_config['experiment-id']
    if experiment_id not in cv_experiment_id:
        msg = 'Experiment "{0}" not found'.format(experiment_id)
        error_list.append(msg)
        return error_list
    cv_experiment = cv_experiment_id[experiment_id]

    # go through each test as defined in key_mapping)
    for (key, preprocessor), (cv_key, checker) in key_mapping.items():
        if key == 'parent-experiment-id' and \
           suite_config['parent-experiment-mip'] == 'None':
            print ('No parent-experiment-mip for this experiment. Skipping '
                   'parent-experiment-id')
            continue
        suite_value = preprocessor(suite_config[key])
        cv_value = cv_experiment[cv_key]
        if cv_value == '':
            msg = ('{}: Empty value in CV for "{}". Cannot validate.'
                   '').format(key, cv_key)
            warnings_list.append(msg)
        if not checker(suite_value, cv_value):
            msg = '{0} : {1} mismatch\n'.format(key, cv_key)
            if isinstance(cv_value, list):
                msg += ('    received "{0}", expected one of: "{1}"'
                        '').format(suite_value, cv_value)
            else:
                msg += ('    received "{0}", expected: "{1}"'
                        '').format(suite_value, cv_value)
            error_list.append(msg)

    # Check the suite components against the required and allowed components
    # lists in the CV
    suite_components = suite_config['source-type'].split(",")
    invalid_components = []
    allowed_components = (cv_experiment['required_model_components'] +
                          cv_experiment['additional_allowed_model_components'])

    for i in suite_components:
        if i not in allowed_components:
            invalid_components.append(i)
    if invalid_components:
        msg = ('source-type failure: {} not found in CV for experiment "{}"'
               '\n').format(repr(invalid_components), experiment_id)
        msg += ('    Allowed components are: {}'
                '\n').format(repr([str(i) for i in allowed_components]))
        error_list.append(msg)
    return warnings_list, error_list


def get_cv(section, revision='master'):
    """
    Retrieve the controlled vocabulary dictionary at a given version
    and return it as a dictionary.

    Parameters
    ----------
    section : str
        determines section of the CVs that is required (e.g.
        "experiment_id", "source_id")
    revision : str, optional
        revision id/branch name/tag name to retrieve

    Returns
    -------
    dict
        dictionary with controlled vocabulary data
    """
    cmd = ['curl', '-s', '-f',
           CV_URL_TEMPLATE.format(revision, section)]
    curlproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    text = curlproc.communicate()[0]
    if curlproc.returncode != 0:
        msg = ('Retrieval of controlled vocabulary failed. Please check '
               'carefully that the section ("{}") and revision ("{}") are '
               'both valid.\n'
               'command: {}\n'
               'return code: {}').format(section, revision, " ".join(cmd),
                                         curlproc.returncode)
        raise Exception(msg)
    cv_section = json.loads(text)[section]

    return cv_section


def main():
    """
    Main routine.
    """
    # Get location of rose-suite.info file either from environment
    # or the sole argument.
    if 'ROSE_SUITE_DIR' in os.environ:
        suite_info_file = os.path.join(os.environ['ROSE_SUITE_DIR'],
                                       'rose-suite.info')
    else:
        if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
            suite_info_file = sys.argv[1]
        else:
            print ('Please supply location of rose-suite.info file '
                   'as an argument if not running this script from the suite')
            sys.exit(1)
    # Load the config information and get the corresponding Controlled
    # Vocabulary file
    suite_info = rose.config.load(suite_info_file)
    if 'project' not in suite_info:
        raise Exception('Validation can only proceed where the project field'
                        ' is set to u-cmip6')
    if 'controlled-vocabulary' not in suite_info:
        raise Exception('Validation can only proceed where the '
                        'controlled-vocabulary field is set')
    cv_revision = suite_info.value['controlled-vocabulary'].value
    cv_experiment_id = get_cv('experiment_id', revision=cv_revision)
    experiment_id = suite_info['experiment-id'].value
    cv_tag = suite_info['controlled-vocabulary'].value
    # Check the suite_info.
    warnings, errors = check_experiment(suite_info, cv_experiment_id)
    # Report results and exit with return code 1 if there is an error.
    if warnings:
        print 'Warnings:'
        print '  ' + '\n  '.join(warnings)
    if errors:
        print 'Errors found:'
        print '  ' + '\n  '.join(errors)
        print '\n'
        print ('CV information on experiment "{}" at branch/tag "{}":'
               '').format(experiment_id, cv_tag)
        print json.dumps(cv_experiment_id[experiment_id], indent=2,
                         sort_keys=True)
        sys.exit(1)
    else:
        print "No errors found."
        sys.exit(0)


if __name__ == '__main__':
    main()
