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
   
    def __init__(self, err):
        """ Contructor
        
            Keyword Arguments:
            err              -- The Exception that caused a Calibration
                                Error.
        """
        self.phase = "COMPU"
        self.err = err
        
    def __str__(self):
        """ String representation
        """
        return str(self.err)
    