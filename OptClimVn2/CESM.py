"""
Class to support CESM

"""
# TODO use pathlib.
import collections
import copy
import json
#M need all 3 above?
import stat
import tempfile

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
import numpy as np
import stat # needed to change file permission bits.
import ModelSimulation
from ModelSimulation import _namedTupClass
import subprocess



class CESM(ModelSimulation.ModelSimulation):
    """
    CESM class. Sub-class of ModelSimulation.
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
    

        Create an instance of CESM class. Default behaviour is to read from dirPath and prohibit updates.
        :param dirPath -- path to directory where model simulation exists or is to be created
        :param create (optional with default False). If True create new directory and populate it.
            Afterwards the ModelSimulation will be readOnly.
            These options should be specified when creating a new study otherwise they are optional and ignored
            :param refDirPath -- reference directory. Copy all files from here into dirPath
            :param name -- name of the model simulation. If not provided will be taken from dirPath
            :param ppExePath --  path to post processing executable
            :param ppOutputFile -- File name of output of post processing executable. Default is observations.json
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
        super(CESM, self).__init__(dirPath,
                                     obsNames=obsNames, create=create, 
                                     refDirPath=refDirPath, name=name,
                                     ppExePath=ppExePath,
                                     ppOutputFile="observations.json", parameters=parameters,  # options for creating new study
                                     update=update,  # options for updating existing study
                                     verbose=verbose)
        # overwrite superclass values for start and continue scripts.
        self.SubmitFiles['start'] = 'optclim_submit_cesm.sh'
        #TODO - do we need the continue script - Mike thinks not the concern of OptClim.
        # but not changing the code in case I'm wrong.
        self.SubmitFiles['continue'] = 'nonexistent.sh' #null # 'SUBMIT.cont'
        self.postProcessFile = 'optclim_finished' # name of post-processing file

        if create:  # want to create model instance so do creation.
            #self.fixClimFCG()  # fix the ClimFGC namelist
#            self.modifySubmit(runTime=runTime, runCode=runCode)  # modify the Submit script
         #M   self.modifyScript()  # modify Script
          #M  self.createWorkDir(refDirPath)  # create the work dirctory (and fill it in)
#            self.genContSUBMIT()  # generate the continuation script.
            self.createPostProcessFile("# No job to release")
            # this means that the model can run without post-processing
            # as this bit of code also allows the model to resubmit from an NRUN

        ## Set up namelist mappings. #TODO add documentation to parameters and have way of model instance reporting on known params.
        self.cesmNames('dust_emis_fact',  "user_nl_cam")
        self.cesmNames('dtlimit','user_nl_docn')

        # got some parameters and either creating or updating -- update namelist.
        if len(parameters) > 0 and (create or update):
            self.setReadOnly(False)  # allow modification
            self.setParams(parameters, verbose=verbose, fail=True)  # apply namelist etc
        self.setReadOnly(True)  # make it read only


    def cesmNames(self, var, nlFile='user_nl_cam'):
        """
        CESM replacement for simpleNameList
        set up single variable with name var.lower() in namelist nl in file nlFile
        :param var: Name of variable
        :param (optional) nlFile -- name of file for namelist. 
        :return: none
        """
        nl="cesm_dummy"
        self.genVarToNameList(var, nameListVar=var, nameListName=nl, nameListFile=nlFile)

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

    def createModelSimulation(self, parameters, ppExePath=None, obsNames=None, name=None,
                              ppOutputFile=None, refDirPath=None, verbose=False):
        """
        Create (in filesystem) a model simulation. After creation the simulation will be read only.
        :param parameters -- dict of parameter names and values OR pandas series.
        :param ppExePath --  path to post processing executable -- Default None
        :param obsNames -- list of observations being used. -- Default None
        :param  name ((optional)) -- name of the model simulation. If not provided will be taken from dirPath
        :param  ppOutputFile (optional)  -- name of output file where output from postprcessing is (default comes from config)
        :param refDirPath (optional) -- reference directory. Copy all files from here into dirPath
        :param  verbose (optional) -- if true be verbose. Default is False
        """
        # general setup
        self._readOnly = False  # can write if wanted.

        if refDirPath is not None:
            refDirPath = os.path.expandvars(os.path.expanduser(refDirPath))
        #  fill out configuration information.
        config = collections.OrderedDict()
        if name is None:
            config['name'] = os.path.basename(self.dirPath)
        else:
            config['name'] = name
#        import pdb;pdb.set_trace()

        obs = collections.OrderedDict()
        try:
            for k in obsNames: obs[k] = None
        except TypeError:
            pass

        config['ppExePath'] = ppExePath
        config['ppOutputFile'] = ppOutputFile
        if refDirPath is not None: config['refDirPath'] = refDirPath

        config['observations'] = obs
        config['parameters'] = parameters

        config['newSubmit'] = True  # default is that run starts normally.
        config['history'] = dict()  # where we store history information. Stores info on resubmit, continue information.

        if verbose:   print("Config is ", config)

        if os.path.exists(self.dirPath):  # delete the directory (if it currently exists)
            shutil.rmtree(self.dirPath, onerror=optClimLib.errorRemoveReadonly)

        if refDirPath is not None:  # copy all files and directories from refDir

            # use CESD/CIME to clone 
            # command line for now - maybe use CIME python classes later...?
            clonecmd=os.path.expandvars('$OPTCLIMTOP/CESM/optclim_clone_cesm.sh')
            clonecmd+=" %s %s " %(refDirPath, self.dirPath)
            if verbose: print("clonecmd is ", clonecmd)
            procStdOut = subprocess.check_output(clonecmd, shell=True)
             # expect error of error msg env_mach_specific.xml already exists, delete to replace
            if verbose:   print("Clone output  is ", procStdOut)

        self.set(config)  # set (and write) configuration
        # TODO add setParams call here..
        # and no longer able to write to it.
        self._readOnly = True


    def writeNameList(self, verbose=False, fail=False, **params):
        # TODO make parameters a simple dict rather than kwargs
        """
        Modify existing namelist files using information generated via genConversion
        Existing files will be copied to .bak
        :param verbose (optional -- default is False). If True provide more information on what is going on.
        :param fail (optional default is False). If True fail if a parameter not found.
        :keyword arguments are parameters and values.
        :return:  ordered dict of parameters and values used.
        """
#        import pdb; pdb.set_trace() 

        if self._readOnly:
            raise IOError("Model is read only")

        params_used = collections.OrderedDict()  #
        files = collections.OrderedDict()  # list of files to be modified.
        for param, value in params.items():  # extract data from conversion indexed by file --
            # could this code be moved into genVarToNameList as really a different view of the same data.
            # NO as we would need to do this only once we've finished generating namelist translate tables.
            # potential optimisation might be to cache this and trigger error in writeNameList if called after genNameList
            # search functions first
            if param in self._metaFn:  # got a meta function.
                #not supporting these yet.... 
                if verbose: print(f"Running function {self._metaFn[param].__name__}")
                metaFnValues = self._metaFn[param](value)  # call the meta param function which returns a dict
                params_used[param] = metaFnValues  # and update return var
                for conv, v in metaFnValues.items():  # iterate over result of fn.
                    if conv.file not in files:
                        files[conv.file] = []  # if not come across the file set it to empty list
                    files[conv.file].append((v, conv))  # append the  value  & conversion info.
            elif param in self._convNameList:  # got it in convNameList ?
                for conv in self._convNameList[param]:
                    if conv.file not in files:
                        files[conv.file] = []  # if not come across the file set it to empty list
                    files[conv.file].append((value, conv))  # append the value  & conversion
                    params_used[param] = value  # and update return var
            elif fail:

                       raise KeyError("Failed to find %s in metaFn or convNameList " % param)
            else:
                pass
        print(" CESM writeNameList done sorting\n")
             # make aloose-coupling file - to allow easy model-specifci code to 
             # kn ow what is going on. Really expecting to want this with UKESM
             # to hold parameter values, here  enabling a crude test also
             # for ukesm drop the tst and Tst
             # so FOR TESTING -make obs that are the parameters!
        lcPath = os.path.join(self.dirPath, "observations.json")
        looseDict={} # in CESM for test case only use!

        # now have conversion tuples ordered by file so let's process the files
        for file in files.keys():  # iterate over files
            # need to create backup? Only do if no back up exists. This allows generateNameList to be run multiple times
            # doing updates. First time it runs we assume we have a directory ready to be modified.
            filePath = os.path.join(self.dirPath, file)  # full path to namelist file
            # check file exists if not raise exception
            if not os.path.isfile(filePath):
                # raise IOError("file %s does not exist"%(filePath))
                continue  # skip this file.
            backup_file = filePath + "_nl.bak"  # and full path to backup fie.
            if not os.path.isfile(backup_file):
                shutil.copyfile(filePath, backup_file)
            # now append to the file ujsed for CESM
            fcesmfile=open(filePath,mode='a')
                # Now write to appropriate file each param
                # format is just parname = value.
                # CESM in building the model run takes this into namelists.
            for (value, conv) in files[file]:
                    if type(value) is np.ndarray:  # convert numpy array to list for writing.
                        value = value.tolist()
                    elif isinstance(value, str):  # may not be needed at python 3
                        value = str(value)  # f90nml can't cope with unicode so convert it to string.
                    fcesmfile.write("%s = %s\n"%(conv.var, value))
                    if verbose:
                        print("Setting %s,%s to %s in %s" % (conv.namelist, conv.var, value, filePath))
                    looseDict[conv.var+"_tst"]=value
                    
            fcesmfile.close()

                # wite json file into the simulation directory

        floose=open(lcPath,mode='w')
        json.dump(looseDict, floose,indent=4)
        floose.close()
        return params_used

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

        super(CESM, self).setParams(params, addParam=addParam, write=write,
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
           

    def remove_submit(self, runStatus=None):
        """
        Provides full path to submit script.
        :param runStatus (default None)-- If 'start' return path to new submit script (defined in self.SubmitFile)
                                      If 'continue' return path to continuation submit script (defined in self.SubmitFile)
                            If None then use value from runStatus method to chose.
        :return: path to appropriate submit script that should be ran to submit the model
        """

        if runStatus is None:
            newSubmit = self.runStatus()
        else:
            newSubmit = runStatus
        script=os.path.expandvars('$OPTCLIMTOP/CESM/optclim_submit_cesm.sh')
# in CESM only start?       script = pathlib.Path(self.dirPath)/self.SubmitFiles[newSubmit]

        return script


    def createPostProcessFile(self, postProcessCmd):

        """
            Used by the submission system to allow the post-run job to be submitted when the simulation
            has completed. This code also modifies the UM so that when a NRUN is fnished it automatically runs the continuation case.

        """
        import pathlib
        outFile = pathlib.Path(
            self.dirPath) / self.postProcessFile  # needs to be same as used in SCRIPT which actually calls it
        with open(outFile, 'w') as fp:
            print(
                    f"""#  script to be run in from tail end of the CESM slurm script.
# it releases the post-processing script when the whole simulation has finished.
         {postProcessCmd} ## code inserted
                """, file=fp)
            return outFile

