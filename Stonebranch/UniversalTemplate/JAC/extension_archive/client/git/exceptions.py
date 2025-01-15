class GitBaseException(Exception):
    def __init__(self, value):
        self.error_description = value

    def __str__(self):
        return repr(self.error_description)


class GitFileNotExistError(GitBaseException):
    pass


class GitRepoNotExistException(GitBaseException):
    pass


class GitBranchNotExistException(GitBaseException):
    pass


class GitClientException(GitBaseException):
    pass


class GitAuthException(GitBaseException):
    pass
