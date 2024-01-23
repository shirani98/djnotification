DjNotification - Django Notification App
========================================


Overview
--------

`DjNotification` is a Django app designed to facilitate real-time notification management in a Django project. It provides features similar to Firebase Cloud Messaging (FCM) with WebSocket integration for seamless communication.

Key Features
------------

- **Notification Groups:** Create and manage notification groups with different types, including public, private, and custom groups.

- **Notification Types:** Send various types of notifications, such as cards, modals, image-only, and top banners.

- **User Subscriptions:** Allow users to subscribe and unsubscribe from notification groups.

- **Django Admin Integration:** Manage subscriptions, groups, and notifications through the Django admin interface.

- **REST API Support:** Use Django REST Framework to create, retrieve, and paginate notifications through API endpoints.

- **Scheduled Notifications**: Admin can schedule notifications for the future by setting a specific time for them to be sent.

- **Expiration Time for Notifications**: Notifications can have an expiration time, and users who join a group with active notifications can receive those notifications.

- **Real-time Member Presence**: Users can see real-time updates of members present in each group.

- **Send Notifications via API or Admin Panel**: Notifications can be sent programmatically via API using the `NotificationAPIView` or manually created and sent through the Django admin panel.

Example Usage
-------------

1. **Install DjNotification**

   ```
   pip install djnotification
   ```
2. Add DjNotification to **INSTALLED_APPS** in settings.py:

    ```
    INSTALLED_APPS = [
    # ...
    'djnotification',
    # ...
    ]
    ```
3. **Run Migrations**
   ```
   python manage.py migrate
   ```
4. **Run Celery Workers**
        Ensure Celery is installed (pip install celery) and run the Celery worker:
        ```
        celery -A your_project_name worker -l info
        ```


5. **Define Notification Groups**
    Define notification groups using Django admin or your application code. Groups are instances of the Group model in the djnotification app.

6. **Send Notification from API or Admin**
        Sending Notification from API or Admin panel action.


Project Concept
---------------
Imagine DjNotification as a Django-based notification system similar to Firebase Cloud Messaging (FCM) with WebSocket integration. It allows for real-time communication and notification delivery to users or groups, making it a powerful tool for keeping users informed and engaged in your Django project.


Contributing
------------
Contributions are welcome! Please follow these guidelines when contributing to the project. Fork the repository, create a branch, make your changes, and submit a pull request.

License
-------
This project is licensed under the MIT License.