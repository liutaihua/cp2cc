#coding=utf8


NO_METHOD = 0x01
INVALID_METHOD = 0x02
OAUTH_ERROR = 0x03
PERMISSION_ERROR = 0x04
PRIVACY_ERROR = 0x05
INVALID_ARGUMENTS = 0x06
NOT_FOUND = 0x07
LOCKED = 0x08
THROTTLED = 0x09
ALREADY_IN_USE = 0x10



class Error(Exception):
    @property
    def message(self):
        return "%s" % (self.__class__.__name__)

    def __str__(self):
        return self.message


class UserVisibleError(Error):
    """raised for errors that should be shown in the UI.
    Subclasses should implement to_html and to_api methods.
    """
    def to_html(self):
        raise NotImplementedError

    def to_api(self):
        raise NotImplementedError


class PrivateDataError(Error):
    """raised when a user tried to view another user's private data

    The user tried to view private data and must either be logged in or be a
    contact of the user to see it
    """
    # TODO should care about whether the user is logged in or not
    def __init__(self, view, current_user=None):
        self.view = view
        self.current_user = current_user


class UserDoesNotExistError(Error):
    def __init__(self, nick, current_user=None):
        self.nick = nick
        self.current_user = current_user

    @property
    def message(self):
        return "User %s does not exist" % self.nick

class DisabledFeatureError(UserVisibleError):
    # TODO(teemu): we should probably add an extra field 
    # for a user-friendly description of the disabled feature. 
    def to_html(self):
        return "This feature is disabled at the moment."

    def to_api(self):
        return "This feature is disabled at the moment."


class ValidationError(UserVisibleError):
    def __init__(self, user_message, field=None):
        self.user_message = user_message
        self.field = field

    def to_html(self):
        return self.user_message

    def to_api(self):
        return "%d:%d" % (self.field, self.user_message)

    def __str__(self):
        return self.user_message

class DatastoreError(ValidationError):
    pass

class ServiceError(ValidationError):
    """ the kind of error thrown when an external service tells us we're wrong """
    pass

class FeatureDisabledError(ValidationError):
    """ an error to raise when a feature has been disabled """
    pass


class ApiException(UserVisibleError):
    message = None
    code = 0x00

    def __init__(self, message=None, code=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message

    def to_dict(self):
        return dict(code=self.code, message=self.message)

    def __str__(self):
        return self.message

    def to_html(self):
        return self.message

    def to_api(self):
        return self.to_dict()

class ApiNotFound(ApiException):
    code = NOT_FOUND

class ApiDeleted(ApiNotFound):
    pass

class ApiLocked(ApiException):
    code = LOCKED

class ApiNoTasks(ApiNotFound):
    pass

class ApiThrottled(ApiException):
    code = THROTTLED

class ApiPermissionDenied(ApiException):
    code = PERMISSION_ERROR

class ApiOwnerRequired(ApiException):
    code = PRIVACY_ERROR

class ApiViewableRequired(ApiException):
    code = PRIVACY_ERROR

class ApiNoMethod(ApiException):
    code = NO_METHOD

class ApiInvalidMethod(ApiException):
    code = INVALID_METHOD

class ApiInvalidArguments(ApiException):
    code = INVALID_ARGUMENTS

class ApiOAuth(ApiException):
    code = OAUTH_ERROR

class ApiAlreadyInUse(ApiException):
    code = ALREADY_IN_USE
