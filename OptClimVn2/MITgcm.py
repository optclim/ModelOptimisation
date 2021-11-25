"""
Class to support MITgcm in optimisation (and other approaches) work.

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


class MITgcm(ModelSimulation.ModelSimulation):
    """
    MITgcm class. Sub-class of ModelSimulation.
    """

    def __init__(self, dirPath, obsNames=None,
                 create=False, refDirPath=None, name=None, ppExePath=None,
                 ppOutputFile=None,
                 runTime=None, runCode=None,  # options for creating new study
                 update=False,  # options for updating existing study
                 verbose=False, parameters={}):
        """
        TODO remove runCode and runTime -- they are really properties of the submission rather than the model itself.
         However, how they are done depends on the model... So a bit tricky!
         ...can be captured in teh script sthat run them and the config file for the study ?
    

        Create an instance of MITgcm class. Default behaviour is to read from dirPath and prohibit updates.
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
        super(MITgcm, self).__init__(dirPath,
                                     obsNames=obsNames, create=create, refDirPath=refDirPath, name=name,
                                     ppExePath=ppExePath,
                                     ppOutputFile="observations.json", parameters=parameters,  # options for creating new study
                                     update=update,  # options for updating existing study
                                     verbose=verbose)
        # overwrite superclass values for start and continue scripts.
        self.SubmitFiles['start'] = 'run_sbatch.sh'
        self.SubmitFiles['continue'] = 'run_sbatch.sh' #null # 'SUBMIT.cont'
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
        self.simpleNamelist('gravity')
        self.simpleNamelist('SEAICE_STRENGTH','SEAICE_PARM01','data.seaice')

    def simpleNamelist(self, var, nl='PARM01', nlFile='data'):
        """
        set up single variable with name var.lower() in namelist nl in file nlFile
        :param var: Name of variable
        :param (optional) nl -- name of namelist. 
        :param (optional) nlFile -- name of file for namelist. 
        :return: none
        """
        self.genVarToNameList(var, nameListVar=var.upper(), nameListName=nl, nameListFile=nlFile)


    def createWorkDir(self, refDirPath, verbose=False):
        """
        Create the workdir and if refDirPath has .astart & .ostart copy those into created workDir
        :param refDirPath -- name of reference directory
        :param (optional) verbobse -- default False. If True be verbose.
        :return: nada
        """

        workDir = os.path.join(self.dirPath, 'W')
        if not os.path.isdir(workDir): os.makedirs(workDir)  # create the directory

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
        return 
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

        super(MITgcm, self).setParams(params, addParam=addParam, write=write,
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
                    f"""#  script to be run in from tail end of the MITgcm slurm script.
# it releases the post-processing script when the whole simulation has finished.
         {postProcessCmd} ## code inserted
                """, file=fp)
            return outFile

