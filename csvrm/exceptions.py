class ModelError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = "ModelError %s" % message
