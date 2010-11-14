'''
Created on Nov 11, 2010

@author: surya
'''

import sys
import time

from Logging.Logger import getLog
from Locking.AppLock import getLock
from DANASettings.Settings import ExitCode
from DANAExceptions.DANAException import DANAException

class DANAFramework:
    """                         Data ANAlysis Framework Specification
                                --------------------------------------
        
        The Data ANAlysis Framework crunches data in any Processing List of the following format:
        
        Processing List:
                ______________________________________________________________________________
        Item1: | UploadData1 ->  CalibrationConfig1 - CalibrationConfig2 - CalibrationConfig3 |
               |                         |                    |                    |          |
               |                      Result1              Result1              Result1       |
               |                         |                   ...                  ...         |
               |                      Result2                                                 |
               |                        ...                                                   |
               |______________________________________________________________________________|
                                                    |
                ______________________________________________________________________________
        Item2: | UploadData2 ->  CalibrationConfig1 - CalibrationConfig2 - CalibrationConfig3 |
               |   ...                   |                    |                    |          |
               |                      Result1              Result1              Result1       |
               |                         |                   ...                  ...         |
               |                      Result2                                                 |
               |                        ...                                                   |
               |______________________________________________________________________________|
                                                    |
                                                   ...
        The following is the DANA pipeline:
        
        For every Item in the Processing List
        
                           PROCESS STEP                                METHOD
                           ------------                                ------
        Step 0: to fetch the Items from a repository implement       | (getDataItems)
         
        Step 1: To check if the current Item is valid implement      | (isValid).
        
        Step 2: To preprocess the UploadData in the Item implement   | (preProcessDataItem).
        
        Step 3: To fetch any new calibration configurations implement| (getCalibrationConfiguration).
        
        Step 4: The framework iterates through the calibration       |
                configurations for analysis.                         
                
        Step 5: To DANA the pre-processed UploadData under a given   | (computeDANAResult).
                Calibration COnfiguration implement                  
                                                                      
        Step 6: To save the computation result implement             | (saveDANAResult). 
        
        Other Methods: 
        Error :      To handle any error generated in the framework  | (onError). 
                     implement    
                     
        Processed? : To see if the current Item has been processed 
                     under a given CalibrationConfiguration implement| (isProcessed).
                     
        Epoch :      Where (Epoch - 1) represents the number of times| (getCurrentEpoch)
                     the Item was processed already.
        
        getItemName : Gets a string representing the current Item    | (getItemName) 
        
        Implementors using this framework need to define:
        preProcessingResult object -- which will be used in the computation of results, and
                                      indexing into calibration data.
        danaResult object -- which is the final result that will be saved to a repository.
        
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
    
    def preProcessDataItem(self, itemname, dataItem, epoch):
        """ Implementors must override this method to preProcess the UploadData and 
            extract features that will be used in the data analysis and in 
            fetching the calibration data.
            
            Keyword Arguments:
            itemname -- String representing the dataItem
            dataItem -- The Item containing the UploadData
            epoch    -- The current epoch
            
            Results:
            preprocessingResult, which is an application specific object that 
            contains the results on preProcessing the data.
        """
        pass
    
    def computeDANAResult(self, itemname, dataItem, epoch, calibrationConfiguration, preProcessingResult):
        """ Implementors must override this method to compute the Analysis Results coupling
            the pre-processing result, data from the calibration configurations, and the
            preprocessing result.
            
            Keyword Arguments:
            itemname                  -- A String representing the dataItem.
            dataItem                  -- The Item containing the UploadData.
            epoch                     -- The current epoch.
            calibrationConfigurations -- The Calibration Data.
            preProcessingResult       -- The results obtained after pre-processing the 
                                         UploadData.
                                         
            Results:
            danaResult, again an application specific object that is the result of the
            Data Analysis computation.
        """
        pass
    
    def saveDANAResult(self, itemname, dataItem, epoch):
        """ Implementors must override this method to save the results of a Data Analysis 
            computation.
            
            Keyword Arguments:
            itemname -- String representing the dataItem.
            dataItem -- The Item containing the UploadData.
            epoch    -- The current epoch
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
    
    def isProcessed(self, dataItem):
        """ Implementors must override this method to indicate if a dataItem has been
            processed already.
            
            Keyword Arguments:
            dataItem -- a single Item in the processing list.
            
            Returns:
            True, if processed, false otherwise.
        """
        pass
    
    def onError(self, itemname, dataItem, err, phase):
        """ Implementors must override this method, which will be invoked 
            whenever an error occurs in processing the given dataItem.
            
            Keyword Arguments:
            itemname -- string representing the dataItem
            dataItem -- A single Item in the processing list.
            epoch    -- An integer representing the current Epoch
            err      -- Error object, depending on the implementation can 
                        be a string reporting a message or a list of params 
                        to operate on. It could essentially store information 
                        about the dataItem's processing result in the list 
            phase    -- phase indicates which phase of the Data Analysis failed.
        
                        PPROC : data_item flag invalid, state invalid reason
                        CALIB : data_item flag invalid, state invalid reason
                        COMPU : for a data_item->calib_conf->state result as pre-processed but status is failed
                        SAVIN : data_item flag invalid, state invalid reason
                        
                        Errors in saving results to the database must be logged i.e. raise critical error
        """
        pass
    
    def getCalibrationConfigurations(self, itemname, dataItem, preProcessingResult):
        """ Implementors must override this method to fetch any new calibration
            data and add it to the list of known calibration configurations
            for a dataItem.
            
            Keyword Arguments:
            itemname            -- String representing the dataItem
            dataItem            -- A single Item in the processing list
            preProcessingResult -- The preProcessingResult obtained after
                                   preProcessing the data
                                   
            Returns:
            An iteratable object containing a list of calibration configs
            corresponding to the given dataItem
        """
        pass
    
    def getCurrentEpoch(self, dataItem):
        """ Implementors must override this method to fetch the current epoch
            NOTE: each time an item is processed its epoch increases.
            
            Keyword Arguments:
            dataItem -- A single Item in the processing list
            
            Returns:
            epoch number
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
                    if force or (not self.isProcessed(dataItem)):
                        
                        # Step 1:
                        # Run a validation step on the input data item
                        if not self.isValid(dataItem):
                            continue
                        
                        # Fetch an item description to be used as a string to refer to the 
                        # current dataitem
                        itemname = self.getItemName(dataItem)
                        
                        # Fetch the current epoch number
                        epoch = self.getCurrentEpoch(dataItem)
                        
                        # Step 2:
                        # Preprocess the dataItem
                        preProcessingResult = self.preProcessDataItem(itemname, dataItem, epoch)
                            
                        # Step 3:
                        # Fetch the following:
                        # a) Calibration Data relevant to information in preProcessingResult
                        # b) Any new Calibration Data that was not previously in the list of
                        #    calibration configurations.
                        calibrationConfigurations = self.getCalibrationConfigurations(itemname, dataItem, preProcessingResult)
                        
                        # Step 4:
                        # Iterate through all the calibration configurations and compute the
                        # DataAnalysis Result.
                        for calibrationConfiguration in calibrationConfigurations:
                            
                            # Step 5:
                            # Compute Result and store the result (along with the calibrationConfiguration)
                            self.computeDANAResult(itemname, dataItem, epoch, calibrationConfiguration, preProcessingResult)
                            
                        # Step 6:
                        # The danaResult obtained here is for the given dataItem corres. to
                        # the given calibrationConfiguration.
                        self.saveDANAResult(itemname, dataItem, epoch)

                except DANAException, err:
                    self.onError(itemname, dataItem, epoch, err, err.phase)
                    continue
                
        except Exception, err:
            return ExitCode.Failed, str(sys.exc_info())
       
        return ExitCode.Success, ""
    
    def run(self, pidfile, programname, timeinterval, force=False):
        """ This method runs the danaJob every timeinterval subject to the 
            constraint that if force is True, we process all the images
            that were already processed.
            
            Keyword Arguments:
            pidfile      -- Ensure that only one Application specific dana runs
                            at a time.
            programname  -- Name of the application specific dana.
            timeinterval -- an integer time in seconds after which to repeat dana
            force        -- a boolean, if true we should re-process the processed
                            images as well
        """
        
        if not getLock(pidfile, programname):
            return
        
        while True:
            self.log.info("Running Data ANAlysis", extra=self.danatags)
            if force:
                exitcode, err = self.danaJob(force)
            else:
                exitcode, err = self.danaJob()
            self.log.info("Done Running Data ANAlysis", extra=self.danatags)
            if exitcode is not ExitCode.Success:
                self.log.critical("computation cycle failed" + err, extra=self.danatags)
            time.sleep(timeinterval) 
        