import pickle
import logging
logger = logging.getLogger('gumstix.comms.message')
class Message:
    def __init__(self, functionName, params = []):
        self.functionName = functionName
        self.params = params
        logger.debug('Message Created:'
                     + '/n/t Function Name: /t' + str(self.functionName)
                     + '/n/t Parameters: /n/t/t' + str(self.params))

    def getFunctionName(self):
        return self.functionName

    def getParams(self):
        return self.params

    def serialize(self):
        return pickle.dumps(self)

    def unserialize(serializedObject):
        return pickle.loads(serializedObject)

    unserialize = staticmethod(unserialize)
