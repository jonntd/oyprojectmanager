########################################################################
class User(object):
    """a class for managing users
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', initials=''):
        self._name = name
        self._initials = initials
        #self._type = ''
        pass
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """returns the user name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getInitials(self):
        """returns the user initials
        """
        return self._initials
    
    
    
    #----------------------------------------------------------------------
    def setName(self, name):
        """sets the user name
        """
        self._name = name
    
    
    
    #----------------------------------------------------------------------
    def setInitials(self, initials):
        """sets the user initials
        """
        self._initials = initials