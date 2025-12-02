from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# Model to store the list of logged in users
class LoggedInUser(models.Model):
    """
    Tracks a single active session for a user account.

    Parameters
    ----------
    user : User
        The user who owns the active session.
    session_key : str
        The Django session key associated with the user's current login; may be blank.

    Returns
    -------
    LoggedInUser
        A model instance representing the active session for the given user.
    """

    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        """
        Provide a readable representation of the logged-in user.

        Parameters
        ----------
        self : LoggedInUser
            The current model instance.

        Returns
        -------
        str
            The username associated with the active session.
        """

        return self.user.username
