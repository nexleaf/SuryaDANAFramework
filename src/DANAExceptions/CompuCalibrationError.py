'''
Created on Nov 12, 2010

@author: surya
'''
from DANAExceptions.DANAException import DANAException

class CompuCalibrationError(DANAException):
    """ This Exception is thrown if there was an 
        error fetching calibration data corres.
        to the dataItem.
        
    """
   
    def __init__(self, err, preProcessingResult):
        """ Contructor
        
            Keyword Arguments:
            err                 -- The Exception that caused a Calibration
                                   Error.
            preProcessingResult -- The results on preProcessing.
        """
        self.phase = "COMPUCALIB"
        self.err = err
        self.preProcessingResult = preProcessingResult
        
    def __str__(self):
        """ String representation
        """
        return str(self.err)