"""
Class to support Demo1 in optimisation (and other approaches) work.




"""
# TODO use pathlib.

import fileinput
# TODO -- now have version 1.0X of f90nml may not need to patch here.
import functools  # std functools.
import glob
import math
import os
import re
import shutil
import pathlib
import datetime # needed to parse strings
import f90nml
# NEEDED because f90nml.patch (as used in ModelSimulation) fails with RECONA. For the moment dealing with this here.
import numpy as np
import stat # needed to change file permission bits.
import ModelSimulation
from ModelSimulation import _namedTupClass

# derived from Demo1.py

class Demo1(ModelSimulation.ModelSimulation):
    """
    Demo1 class. Sub-class of ModelSimulation.
    """

    def __init__(self, dirPath, obsNames=None,
                 create=False, refDirPath=None, name=None, ppExePath=None,
                 ppOutputFile=None, runTime=None, runCode=None,  # options for creating new study
                 update=False,  # options for updating existing study
                 verbose=False, parameters={}):
        """
        TODO remove runCode and runTime -- they are really properties of the submission rather than the model itself.
         However, how they are done depends on the model... So a bit tricky!
         ...can be captured in teh script sthat run them and the config file for the study ?
    

        Create an instance of Demo1 class. Default behaviour is to read from dirPath and prohibit updates.
        :param dirPath -- path to directory where model simulation exists or is to be created
        :param create (optional with default False). If True create new directory and populate it.
            Afterwards the ModelSimulation will be readOnly.
            These options should be specified when creating a new study otherwise they are optional and ignored
            :param refDirPath -- reference directory. Copy all files from here into dirPath
            :param name -- name of the model simulation. If not provided will be taken from dirPath
            :param ppExePath --  path to post processing executable
            :param ppOutputFile -- File name of output of post processing executable. Default is observations.nc
            :param obsNames -- list of observations to be readin. (see readObs())
            :param runTime -- run time in seconds for UM job. If set to None nothing is changed.
            :param runCode -- code to be used by Job.
        :param update -- allow updates to the simulation information.
        :param verbose -- provide  verbose output. (See individual methods). Default is False.
        : kwargs -- these are parameter and values.
        :returns initialised object.
        """

        # no parameters should be provided unless create or update provided
        if (len(parameters) > 0) and not (create or update):
            raise ValueError("Provided parameters but not specified create or update")
        # do Demo1 specific cross checks if I can invent any..

                # call superclass init
        super(Demo1, self).__init__(dirPath,
                                     obsNames=obsNames, create=create, refDirPath=refDirPath, name=name,
                                     ppExePath=ppExePath,
                                     ppOutputFile=ppOutputFile, parameters=parameters,  # options for creating new study
                                     update=update,  # options for updating existing study
                                     verbose=verbose)
        # overwrite superclass values for start and continue scripts.
        self.SubmitFiles['start'] = 'SUBMIT'
        self.SubmitFiles['continue'] = 'SUBMIT.cont'
        self.postProcessFile = 'optclim_finished' # name of post-processing file

        if create:  # want to create model instance so do creation.
            #self.fixClimFCG()  # fix the ClimFGC namelist
#            self.modifySubmit(runTime=runTime, runCode=runCode)  # modify the Submit script
            self.modifyScript()  # modify Script
            self.createWorkDir(refDirPath)  # create the work dirctory (and fill it in)
#            self.genContSUBMIT()  # generate the continuation script.
            self.createPostProcessFile("# No job to release")
            # this means that the model can run without post-processing
            # as this bit of code also allows the model to resubmit from an NRUN

        ## Set up namelist mappings. #TODO add documentation to parameters and have way of model instance reporting on known params.
        # easy case all variables in SLBC21 and which just set the values.
        for var in ['VF1', 'ICE_SIZE', 'ENTCOEF', 'CT', 'ASYM_LAMBDA', 'CHARNOCK', 'G0', 'Z0FSEA',  # atmos stuff
                    'N_DROP_MIN', 'IA_AERO_POWER', 'IA_AERO_SCALE',  # indirect aerosol stuff
                    # model here is n_drop = IA_AERO_SCALE*(1-exp(IA_AERO_POWER*N_AERO)) where N_AERO is no of aerosol drops and n_drop is no of cld drolets.
                    # default values are 'N_DROP_MIN': 3.5E7, 'IA_AERO_POWER': -2.5e-9, 'IA_AERO_SCALE': 3.75E8
                    'CLOUDTAU', 'NUM_STAR', 'L0', 'L1', 'OHSCA', 'VOLSCA', 'ANTHSCA', 'RAD_AIT', 'RAD_ACC'
                    # sulphate params.  CLOUDTAU (1.08E4)  air parcel lifetime in cloud, NUM_STAR (1.0E6) threshold concn of accu mode particles
                    # L0=6.5E-5, Scavenging parameter when S < S_threshold
                    # L1=2.955E-5, Scavenging parameter when S > S_threshold
                    # OHSCA=1.0, -- scaling parameter for the OH field.
                    # VOLSCA=1.0, -- scaling parameter for volcanic SO2 emissions
                    # ANTHSCA=1.0, -- scaling parameter for anthropogenic emissions
                    # RAD_AIT -- radius of aitkin mode droplets -- 24e-9
                    # RAD_ACC -- radius of accum mode doplets -- 95E-9
                    ]:
            self.simpleNamelist(var)


    def createWorkDir(self, refDirPath, verbose=False):
        """
        Create the workdir and if refDirPath has .astart & .ostart copy those into created workDir
        :param refDirPath -- name of reference directory
        :param (optional) verbobse -- default False. If True be verbose.
        :return: nada
        """

        workDir = os.path.join(self.dirPath, 'W')
        if not os.path.isdir(workDir): os.makedirs(workDir)  # create the directory
        for f in ['*.astart', '*.ostart']:  # possible start files
            p = glob.glob(os.path.join(refDirPath, f))  # glob them
            if p is not None and len(p) == 1:  # got one
                p = p[0]  # copy it.
                try:
                    shutil.copy(p, workDir)
                    if verbose: print("Copied %s to %s" % (p, workDir))
                except IOError:
                    pass

    def modifyScript(self):
        """
        modify script.
        set EXPTID to runid  --  first ^EXPTID=xhdi
         set JOBID to jobid  -- first ^JOBID
         . $JOBDIR/optclim_finished ## run the check for job release and resubmission.
            This will be modifed by the submission system

        :param name -- the name of the run.
        :return:
        """
        runid = self.getParams().get('RUNID',
                                     self.name())  # TODO fix this so that if params passed a string it does sensible thing with it...
        experID = runid[0:4]
        jobID = runid[4]
        modifystr = '## modified'


        with fileinput.input(os.path.join(self.dirPath, 'SCRIPT'), inplace=1, backup='.bak') as f:
            for line in f:
                if re.search(modifystr, line):
                    raise Exception("Already modified Script")
                elif re.match('^EXPTID=', line):
                    print("EXPTID=%s %s" % (experID, modifystr))
                elif re.match('^JOBID=', line):
                    print("JOBID=%s %s" % (jobID, modifystr))
                else:  # default line
                    print(line[0:-1])  # remove newline
 
    def setParams(self, params, addParam=True, write=True, verbose=False, fail=True):
        """
        Set the parameter values and write them to the configuration file
        and modify the parameters in the current directory. Calls the superclass to do standard stuff first then
         uses existing code to modify parameters in Demo1 namelists 
        :param params -- dictionary (or ordered dict or pd.Series) of the parameter values
        :param addParam (default True) -- if True add to existing parameters
        :param write (default True) -- if True update configuration file.
        :param verbose (default False) -- if True provide more verbose output
        :param fail (default True) -- if True fail if parameter not defined.
        :return:
        """

        if addParam == False:
            # need to find a way of resetting namelist files.
            # one option would be to copy the namelist files from the refdir. That would require working out all the files
            # that is moderately tricky and not yet needed. So raise anNotImplementedError if tried.
            raise NotImplementedError("Not yet implemented addParam")

        super(Demo1, self).setParams(params, addParam=addParam, write=write,
                                      verbose=verbose)  # use super classs setParams
        # remove ensembleMember from the params -- we have no
        #  namelist for it. writeNameList complains if parameter provided
        # and no translation function.
        # TODO implement ensembleMember
        try:
            eM = params.pop('ensembleMember')
        except KeyError:
            pass

        self.writeNameList(verbose=verbose, fail=fail, **params)  # generate/update namelists.

    def createPostProcessFile(self, postProcessCmd):

        """
            Used by the submission system to allow the post-processing job to be submitted when the simulation
            has completed. This code also modifies the UM so that when a NRUN is fnished it automatically runs the continuation case.
            This Demo1 implementation generates a file call optclim_finished which is sourced by SCRIPT.
            SCRIPT needs to be modified to actually do this. (See modifySCRIPT).



        """
        import pathlib
        outFile = pathlib.Path(
            self.dirPath) / self.postProcessFile  # needs to be same as used in SCRIPT which actually calls it
        with open(outFile, 'w') as fp:
            print(
                "#  script to be run in ksh ",
                 file=fp)
            return outFile

