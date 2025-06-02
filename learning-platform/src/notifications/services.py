class NotificationServices:
    """
    A service class for handling operations related to notification.
    """

    def handle_partial_update(self, notification, data):
        """
        Partially update a user notification.

        This method allows the user to update notification is_read field.
        """

        notification.is_read = data.get("is_read", notification.is_read)
        notification.save(update_fields=["is_read"])

        return notification
