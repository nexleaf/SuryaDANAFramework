'''
Created on Nov 12, 2010

@author: surya
'''
from DANAExceptions.DANAException import DANAException

class ResultComputationError(DANAException):
    """ This Exception is thrown if there was an
        error while computing the DANAResult under
        a given calibrationConfiguration corres.
        to a dataItem.
    """
   
    def __init__(self, err, preProcessingResult, computationResult):
        """ Contructor
        
            Keyword Arguments:
            err                 -- The Exception that caused a Calibration
                                   Error.
            preProcessingResult -- The results on preProcessing an item.
            computationResult   -- The results on computing DANA results
                                   
        """
        self.phase = "COMPU"
        self.err = err
        self.preProcessingResult = preProcessingResult
        self.computationResult = computationResult
        
    def __str__(self):
        """ String representation
        """
        return str(self.err)
    