from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


USER_PERMISSIONS = [('can_send_email', 'Can send email')]
USER_UNIQUE_TOGETHER = [('email', 'username')]
EMAIL_PERMISSIONS = [("can_send_email", "Can send email")]


class CustomUser(AbstractUser):
    username = models.CharField(max_length=31)
    email = models.EmailField()
    password = models.CharField(max_length=63)
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Define reverse relationship to access contact lists
    @property
    def contact_lists(self):
        return self.contactlist_set.all()

    class Meta:
        # Provide unique related names for reverse accessors to avoid clashes with built-in User model
        permissions = USER_PERMISSIONS
        unique_together = USER_UNIQUE_TOGETHER

    # Specify unique related names for reverse accessors
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username


class Folder(models.Model):
    name = models.CharField(max_length=63)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ContactList(models.Model):
    name = models.CharField(max_length=63)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contacts = models.ManyToManyField(CustomUser, related_name='in_contact_lists')

    def __str__(self):
        return self.name


class Email(models.Model):
    subject = models.CharField(max_length=63)
    body = models.TextField()
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_emails')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='email_attachments/', blank=True, null=True)
    folders = models.ManyToManyField(Folder, related_name='emails')
    scheduled_time = models.DateTimeField(default=timezone.now, help_text='Schedule email to be sent at a future time.')

    class Meta:
        permissions = EMAIL_PERMISSIONS

    def __str__(self):
        return self.subject


class EmailTemplate(models.Model):
    name = models.CharField(max_length=63)
    subject = models.CharField(max_length=63)
    body = models.TextField()

    def __str__(self):
        return self.name
    