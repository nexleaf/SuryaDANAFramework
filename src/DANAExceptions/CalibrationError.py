'''
Created on Nov 12, 2010

@author: surya
'''
from DANAExceptions.DANAException import DANAException

class CalibrationError(DANAException):
    """ This Exception is thrown if there was an 
        error fetching calibration data corres.
        to the dataItem.
        
    """
   
    def __init__(self, err):
        """ Contructor
        
            Keyword Arguments:
            err              -- The Exception that caused a Calibration
                                Error.
        """
        self.phase = "CALIB"
        self.err = err
        
    def __str__(self):
        """ String representation
        """
        return str(self.err)