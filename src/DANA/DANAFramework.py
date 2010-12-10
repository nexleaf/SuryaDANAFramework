'''
Created on Nov 11, 2010

@author: surya
'''

import sys
import time
import os
import traceback

from Logging.Logger import getLog
from Locking.AppLock import getLock
from DANASettings.Settings import ExitCode
from DANAExceptions.DANAException import DANAException

class DANAFramework:
    """                         Data ANAlysis Framework Specification
                                --------------------------------------
        
        The Data ANAlysis Framework crunches data in any Processing List of the following format:
        
        Processing List: 
                _______________________________________________________________________________
        Item1: | UploadData1 ->  PreProcessConfig -> CalibrationConfig(ApplicationSpecific)   |
               |______________________________________________________________________________|
                                                    |
                ______________________________________________________________________________
        Item2: | UploadData2 ->  CalibrationConfig1 - CalibrationConfig2 - CalibrationConfig3 |
               |______________________________________________________________________________|
                                                    |
                                                   ...
        The following is the DANA pipeline:
        
        For every Item in the Processing List
        
                           PROCESS STEP                                METHOD
                           ------------                                ------
        Step 0: to fetch the Items from a repository implement        | (getDataItems)
         
        Step 1: To check if the current Item is valid implement       | (isValid).
        
        Step 2: Get the name of the item                              | (getItemName).
        
        Step 3: Get the pre-processing configuration                  | (getPreProcessingConfiguration).
        
        Step 4: To preprocess the UploadData in the Item implement    | (preProcessDataItem).
        
        Step 5: To fetch any new calibration configurations implement | (getComputationConfiguration).
                
        Step 6: To compute the DANA result under the calibration      | (computeDANAResult).
                configuration implement
                                                                      
        Step 7: To save the computation result implement              | (saveDANAResult). 
        
        Other Methods: 
        Error :      To handle any error generated in the framework  | (onError). 
                     implement    
                     
        Processed? : To see if the current Item has been processed 
                     under a given CalibrationConfiguration implement| (isProcessed).
        
        
        Implementors using this framework need to define:
        preProcessingResult object -- which stores the results on pre-Processing the dataItem, and 
                                      will be used in the computation of results, and indexing into 
                                      calibration data.
        computationResult object -- which stores the results after computation of DANA results.
        
    """
    
    danatags = "DANA"
    
    def __init__(self):
        """ Constructor
        """
        pass
    
    def getDataItems(self): 
        """ Implementors must override this method to fetch data items from a 
            repository.
            
            for eg: w.r.t mongodb the fetchDataItems would do:
                    return Items.objects 
                    
                    # (essentially returns an iteratable QuerySet Manager)
            
            Returns:
            An iteratable collection of data Items.
        """
        pass
    
    def getItemName(self, dataItem):
        """ Implementors must override this method to get a string describing the
            current dataItem being processed.
            
            Keyword Arguments:
            itemname -- String representing the dataItem
            dataItem -- The Item containing the UploadData
            
            Returns:
            string, representing the dataItem
        """
        pass
    
    def preProcessDataItem(self, itemname, dataItem):
        """ Implementors must override this method to preProcess the UploadData and 
            extract features that will be used in the data analysis and in 
            fetching the calibration data.
            
            Keyword Arguments:
            itemname                   -- String representing the dataItem.
            dataItem                   -- The Item containing the UploadData.
            
            Results:
            preprocessingResult, which is an application specific object that 
            contains the results on preProcessing the data.
            
            throws PreProcessingError.
        """
        pass
    
    def computeDANAResult(self, itemname, dataItem, preProcessingResult):
        """ Implementors must override this method to compute the Analysis Results coupling
            the pre-processing result, data from the calibration configurations, and the
            preprocessing result.
            
            Keyword Arguments:
            itemname                   -- A String representing the dataItem.
            dataItem                   -- The Item containing the UploadData.
            preProcessingResult        -- The results obtained after pre-processing the 
                                          UploadData.
                                         
            Results:
            danaResult, again an application specific object that is the result of the
            Data Analysis computation.
            
            throws ResultComputationError.
        """
        pass
    
    def saveDANAResult(self, itemname, dataItem, preProcessingResult, computationResult):
        """ Implementors must override this method to save the results of a Data Analysis 
            computation.
            
            Keyword Arguments:
            itemname          -- String representing the dataItem.
            dataItem          -- The Item containing the UploadData.
            preProcessingResult  -- The Result obtained on preProcessing the dataItem.
            computationResult -- The Result obtained after computation of results for the dataItem.
            
            throws ResultSavingError. 
        """
        pass
    
    def isValid(self, dataItem):
        """ Implementors must override this method to check if the UploadData
            corresponding to an Item in the processing list is valid.
            
            for eg: in the case of temperature data, check for non-zero 
                    entries, in the case of image data check if all the
                    required information is available/
                    
            This is essentially a validation step.
        
            If the UploadData is invalid simply set the UploadData entry
            as invalid.
            
            in the following way:
            In current schemas UploadData also has a "validFlag" field if
            set to false invalidates an Upload Data. Also the reason
            corresponding to the invalidation is stores in a "invalidReason"
            field.
            
            NOTE: one needs to save any changes made to the UploadData.
            
            Keyword Arguments:
            dataItem -- a single Item in the processing list.
                  
            Returns:
            True, if the UploadData was validated successfully, False otherwise.
        
        """
        pass
    
    def onError(self, itemname, dataItem, err, phase):
        """ Implementors must override this method, which will be invoked 
            whenever an error occurs in processing the given dataItem.
            
            Keyword Arguments:
            itemname -- string representing the dataItem
            dataItem -- A single Item in the processing list.
            err      -- Error object, depending on the implementation can 
                        be a string reporting a message or a list of params 
                        to operate on. It could essentially store information 
                        about the dataItem's processing result in the list 
            phase    -- phase indicates which phase of the Data Analysis failed.
        
                        PPROCCALIB : PPROC : COMPUCALIB : COMPU : SAVIN : 
                        
                        Errors in saving results to the database must be logged i.e. raise critical error
        """
        pass
    
    def getComputationConfiguration(self, itemname, dataItem, preProcessingResult):
        """ Implementors must override this method to get any new calibration
            data derived from the preProcessingResult if the overrideFlag is True,
            otherwise, the default calibration data is used.
            
            Keyword Arguments:
            itemname            -- String representing the dataItem
            dataItem            -- A single Item in the processing list
            preProcessingResult -- The preProcessingResult obtained after
                                   preProcessing the data
                                   
            Returns:
            A computationConfiguration under which computation should occur.
            
            throws CompuCalibrationError.
        """
        pass
    
    def getPreProcessingConfiguration(self, itemname, dataItem):
        """ Implementors must override this method to get any preProcessing data
            associated with the given dataItem.uploaddata alias processEntity.
            
            Keyword Arguments:
            itemname -- String representing the dataItem.
            dataItem -- A single Item in the processing list
            
            Returns:
            A preProcessingConfiguration under which pre-processing should occur.
            
            throws PprocCalibrationError.
        """
    
    def danaJob(self, force=False):
        """ This is the DANA job that runs every time interval over
            all the Items in the process list.
            
            Keyword Arguments:
            force -- a boolean, if True re-analyze all the analyzed data in the repository, 
                                if False analyze only that ones that havent been done already.
                                
            Results:
            exitcode, str - where exitcode is a Settings.ExitCode member and str is a string
                            containing an error message if an error occurred
        """
        
        try:
            # Step 0:
            # Fetch the list of data items to be analyzed
            dataItems = self.getDataItems()
            
            # For every dataItem retrieved 
            for dataItem in dataItems:
                try:
                    
                    # Step 1:
                    # Run a validation step on the input data item
                    if not self.isValid(dataItem):
                        continue
                    
                    # Step 2:
                    # Fetch an item description to be used as a string to refer to the 
                    # current dataitem
                    itemname = self.getItemName(dataItem)
                    
                    # Step 3:
                    # Fetch preProcessing information and store it with the dataItem structure
                    self.getPreProcessingConfiguration(itemname, dataItem)
                    
                    # Step 4:
                    # Preprocess the dataItem
                    preProcessingResult = self.preProcessDataItem(itemname, dataItem)
                        
                    # Step 5:
                    # Fetch the following:
                    # a) Calibration Data relevant to information in preProcessingResult, misc field if overrideFlag is True.
                    # b) use the calibration data in the process list AS-IS if overrideFlag is False.
                    self.getComputationConfiguration(itemname, dataItem, preProcessingResult)
                        
                    # Step 6:
                    # Compute Result and store the result (along with the calibrationConfiguration)
                    computationResult = self.computeDANAResult(itemname, dataItem, preProcessingResult)
                        
                    # Step 7:
                    # The danaResult obtained here is for the given dataItem corres. to
                    # the given calibrationConfiguration.
                    self.saveDANAResult(itemname, dataItem, preProcessingResult, computationResult)
    
                except DANAException, err:
                    self.onError(itemname, dataItem, err, err.phase)
                    continue
                
        except Exception, err:
            return ExitCode.Failed, traceback.format_exc()
       
        return ExitCode.Success, ""
    
    def run(self, pidfile, programname, timeinterval):
        """ This method runs the danaJob every timeinterval subject to the 
            constraint that if force is True, we process all the images
            that were already processed.
            
            Keyword Arguments:
            pidfile      -- Ensure that only one Application specific dana runs
                            at a time.
            programname  -- Name of the application specific dana.
            timeinterval -- an integer time in seconds after which to repeat dana
        """
        
        if not getLock(pidfile, programname):
            return
        
        while True:
            self.log.info("Running Data ANAlysis", extra=self.danatags)
            
            exitcode, err = self.danaJob()
            
            self.log.info("Done Running Data ANAlysis", extra=self.danatags)
            if exitcode is not ExitCode.Success:
                self.log.critical("computation cycle failed" + err, extra=self.danatags)
            time.sleep(timeinterval) 
