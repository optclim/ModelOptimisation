"""
test_MITgcm: test cases for MITgcm methods.
This test routine needs OPTCLIMTOP specified sensibly. (ideally so that $OPTCLIMTOP/um45 corresponds to
  where this routine lives..
  Beware - some methods are in the ModelOptimsation code
  THis module is a tailoring of test_HadCM3.py.
"""
import collections
import filecmp
import os
import re
import shutil
import tempfile
import unittest
import pathlib  # TODO move towards using pathlib away from os.path.xxxx

import numpy as np
import pandas as pd

import MITgcm
import optClimLib

OBS_LIST= [ "dynstat_theta_mean", "dynstat_salt_mean", "seaice_area_mean" ]
PAR_LIST= ["gravity", "SEAICE_STRENGTH"]
PPEXE="optclim_finished"

def cmp_lines(path_1, path_2, ignore=None, verbose=False):
    """
    From Stack exchange --
       http://stackoverflow.com/questions/23036576/python-compare-two-files-with-different-line-endings
    :param path_1: path to file 1 
    :param path_2: path to file 2
    :param ignore -- list of regep patterns to ignore
    :param verbose: default False -- if True print out lines that don't match.
    :return: True if files the same, False if not.
    """

    if ignore is None: ignore = []  # make ignore an empty list if None is provided.
    l1 = l2 = ' '
    with open(path_1, 'r') as f1, open(path_2, 'r') as f2:
        while l1 != '' and l2 != '':
            l1 = f1.readline()
            l2 = f2.readline()
            skip = False  # skip when set true and set so if ignore pattern found
            for p in ignore:
                if re.search(p, l1) or re.search(p, l2):
                    skip = True
                    continue
            if skip: continue  # go to next while bit of of looping over files.
            if l1 != l2:
                if verbose:
                    print(">>", l1)
                    print("<<", l2)
                return False
    return True


class testMITgcm(unittest.TestCase):
    """
    Test cases for MITgcm. There should be one for every method in MITgcm.

    """

    def setUp(self):
        """
        Setup case
        :return:
        """
        parameters = {"gravity": 10.0, "SEAICE_STRENGTH": 0.5}
                      

        tmpDir = tempfile.TemporaryDirectory()
        testDir = pathlib.Path(tmpDir.name)  # used throughout.
        refDir="/work/n02/shared/mjmn02/OptClim/optclim2A/ModelOptimisation/ECCOv4"
        #"/work/n02/shared/mjmn02/OptClim/optclim3/base/ecco/base1"
        #refDir = pathlib.Path('Configurations') / 'xnmea'  # need a coupled model.
        simObsDir = 'pytesting'
        self.dirPath = testDir
        self.refPath = refDir
        self.tmpDir = tmpDir  # really a way of keeping in context
        self.testDir = testDir
        # refDir = os.path.expandvars(os.path.expanduser(refDir))
        # simObsDir = os.path.expandvars(os.path.expanduser(simObsDir))
        shutil.rmtree(testDir, onerror=optClimLib.errorRemoveReadonly)

        self.model = MITgcm.MITgcm(testDir, name='a0101', create=True, refDirPath=refDir,
                                   ppExePath=PPEXE,
                                   ppOutputFile='observations.json', runTime=1200, runCode='test',
                                   obsNames=OBS_LIST,
                                   verbose=False, parameters=parameters)

    def tearDown(self):
        """
        Clean up by removing the temp directory contents
        :return:
        """
        # self.tmpDir.cleanup() # sadly fails because not all files in are writable.
       # optClimLib.delDirContents(self.tmpDir.name)
        print("Remove by hand ",self.testDir)

    def test_init(self):
        """
        Test init
        :return:
        """
        # possible tests
        # 1) Test that changed name and directory has been changed.
        #  Note name and directory don't need to be the same.
        """
        Test init methods works.
        Probably over-kill and could be a pain if internal details change.
        But idea is that public methods all get a work out when modelSimulation initialised.
        :return:
        """
        # using implicit run of setup.
        expectObs = collections.OrderedDict()
        for k in OBS_LIST: expectObs[k] = None
        expectParam = {"gravity": 10.0, "SEAICE_STRENGTH": 0.5}
        self.assertEqual(self.model.get(['name']), 'a0101')
        self.assertEqual(self.model.get(['ppExePath']),PPEXE)
        self.assertEqual(self.model.get(['observations']), expectObs)
        self.assertDictEqual(self.model.get(['parameters']), expectParam)
        self.assertEqual(self.model.get(['ppOutputFile']), 'observations.json')
        self.assertListEqual(list(self.model.get(['observations']).keys()), list(expectObs.keys()))
        # test that read works. Works means no failures and have observations..

        m = MITgcm.MITgcm(self.dirPath, verbose=True)
        # Nothing should have changed except observations have been read in
        self.assertEqual(m.get(['name']), 'a0101')
        self.assertEqual(m.get(['ppExePath']), PPEXE)
        self.assertDictEqual(m.get(['parameters']), expectParam)

        # self.assertEqual(self.model.config['refDir'], None)
        self.assertEqual(m.get(['ppOutputFile']), 'observations.json')
        self.assertListEqual(list(m.getObs().keys()), list(expectObs.keys()))
        self.assertNotEqual(m.getObs(), expectObs)
          # reduced tests here because purpose is not clear to me!

    def test_readMetaParams(self):
        """
        Test that MITgcm specific meta functions all work..by running the inverse function and checking we got
          what we put in.
        :return:
        """
        pass;  # not got any yet in MITgcm-ECCO 

    def test_setParams(self):
        """
        Test setParams
        :return:
        """
        # will test that can set namelist variables, that setting something that doesn't exist fails.
        self.model.setReadOnly(False)  # want to modify model.
        # param is dict of parmaetrs that map directly to namelist variables.
        param = {"gravity": 10.0, "SEAICE_STRENGTH": 0.5}
        metaParam = {}
        un = collections.OrderedDict()
        for k, v in param.items():
            un[k] = v
        expect = un.copy()
        # got problem here.
        for k, v in metaParam.items():
            un[k] = v
            if type(v) == np.ndarray: v = v.round(3)
            expect[k] = v

        self.model.setParams(un, fail=True, verbose=True)
        # verify namelists are as expected.
        vars = self.model.readNameList(expect.keys(), verbose=True, fail=True)

        for k in expect.keys():
            msg = 'Key is %s' % (k)
            print("vars[%s]=%s got %s" % (k, vars[k], expect[k]))
            if type(expect[k]) == list:
                self.assertEqual(vars[k], expect[k], msg=msg)
            else:
                self.assertAlmostEqual(expect[k], vars[k], msg=msg)

        # check pd.Series works
        series = pd.Series(un)
        series['gravity'] = 10.0
        expect['gravity'] = 10.0
        self.model.setReadOnly(False)  # want to modify model
        self.model.setParams(series, fail=True, verbose=True)
        # verify namelists are as expected.
        vars = self.model.readNameList(expect.keys(), verbose=True, fail=True)

        for k in expect.keys():
            print("vars[%s]=%s got %s" % (k, vars[k], expect[k]))
            if type(expect[k]) == list:
                self.assertEqual(vars[k], expect[k], msg=msg)
            else:
                self.assertAlmostEqual(expect[k], vars[k], msg=msg)

    def test_modifyScript(self):
        """
        Test modifyScript produces expected result
        and fails if it tries to modify something already modifies
        :return: 
        """

        print ("modify_script not used")


    def test_modifySubmit(self):
        """
        Test modifySubmit - but what should it be doing?
        :return: 
        """

        print ("modify_script not used")
    ## couple of methods  to allow checking of submit and script

    def check_Submit(self, print_output=False, runType='CRUN', expect=None, expectMod=None):
        """
        Simple way of checking script OK!
        :param self:
        :return:
        """
        print (" MITgcm script is not changed - not testing")


    def check_script(self, print_output=False, runType='CRUN', expect=None, expectMod=None):
        print (" MITgcm script is not changed - not testing")

    def test_genContSUBMIT(self):
        """
        test that contSUBMIT works.
        Tests are that it only had two modification marks in the continuation SUBMIT script
        """
        print (" not used - HadAM3 only genContSUBMIT")

    def test_createWorkDir(self):
        """
        Test that createWorkDir worked as expected
        :return: 
        """
        # no need to run createWorkDIr as already ran by init
        # just check it exists and is a dir
        self.assertTrue(os.path.isdir(os.path.join(self.model.dirPath, 'W')))

    def test_fixClimFCG(self):
        """
        Test that fixClimFCG works as expects 
         
         converting all CLIM_FCG_YEARS(1,..) to CLIM_FCG_YEARS(:,...)
        :return: 
        """
        print (" fixClimFCG not used - HadAM3 only genContSUBMIT") 

    def test_submit(self):
        """
        Test the submit method works -- returns sensible path.
        Rather trivial test.. 
        :return: 
        """
        dir = pathlib.Path(self.model.dirPath)
        p = pathlib.Path(self.model.submit())
        self.assertEqual(p, dir / 'run_sbatch.sh')

    def test_perturb(self):
        """
        Test that perturbation works.
          Need to look at namelists so a bit tricky...
        :return:
        """
        print (" perturb not used - HadAM3 only genContSUBMIT") 

    def test_createPostProcessFile(self):
        """
        Test that creation of post processing script works.

        :return:
        """
        release_cmd = 'ssh login qrls 999999.1'
        file = self.model.createPostProcessFile(release_cmd)
        # expect file to exist
        self.assertTrue(file.exists())
        # and that it is as expected.
        self.assertEqual(file, pathlib.Path(self.dirPath) / self.model.postProcessFile)
        # need to check its contents...
        # will check two things. 1) that SUBCONT is as expected 2) that the qrls cmd is in the file
        submit_script = self.model.submit('continue')
        cntSUBCONT = 0
        cntqrls = 0
        with open(file, 'r') as f:
            for line in f:
                if line.find(release_cmd) != -1:
                    cntqrls += 1
                elif line.find(f'SUBCONT={submit_script}') != -1:
                    cntSUBCONT += 1

        self.assertEqual(cntqrls, 1, 'Expected only 1 qrls cmd')
        self.assertEqual(cntSUBCONT, 1, 'expected only 1 SUBMITCMD')


if __name__ == "__main__":
    print("Running Test Cases")
    unittest.main()  ## actually run the test cases
