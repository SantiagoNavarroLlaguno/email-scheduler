from django import forms
from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, Folder, ContactList, Email, EmailTemplate
from .tasks import send_scheduled_email


# Define custom send email action
def send_email_action(modeladmin, request, queryset):
    for email in queryset:
        # Add logic to send email here
        send_mail(
            subject=email.subject,
            message=email.body,
            from_email=email.sender.email,
            recipient_list=[email.recipient.email],
            fail_silently=False,
        )
        messages.success(request, f"Email sent to {email.recipient.email}")
send_email_action.short_description = "Send selected Emails"


# EmailAdminForm class
class EmailAdminForm(forms.ModelForm):
    template = forms.ModelChoiceField(queryset=EmailTemplate.objects.all(), required=False)

    class Meta:
        model = Email
        fields = '__all__'


# EmailAdmin class
@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    form = EmailAdminForm
    list_display = ['subject', 'sender', 'recipient', 'timestamp']
    actions = [send_email_action]

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('template'):
            template = form.cleaned_data['template']
            obj.subject = template.subject
            obj.body = template.body
        if obj.scheduled_time and obj.scheduled_time > timezone.now():
            send_scheduled_email.apply_async((obj.id,), eta=obj.scheduled_time)
            messages.info(request, "Email scheduled to be sent at %s" % obj.scheduled_time)
        else:
            # Send immediately
            send_scheduled_email.delay(obj.id)
        super().save_model(request, obj, form, change)


# CustomUserAdmin class
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Folder)
admin.site.register(ContactList)
