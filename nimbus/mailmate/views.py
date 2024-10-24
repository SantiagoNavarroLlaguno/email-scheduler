from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import CustomUser, Email, ContactList, Folder
from .forms import EmailForm
from .tasks import send_scheduled_email
from .serializers import EmailSerializer, ContactListSerializer, FolderSerializer


# View for sending emails
# @login_required
# @permission_required('mailmate.can_send_email', raise_exception=True)
# def send_email(request):
#     if request.method == 'POST':
#         form = EmailForm(request.POST)
#         if form.is_valid():
#             sender = request.user
#             recipient_ids = request.POST.getlist('recipients')
#             subject = request.POST.get('subject')
#             body = request.POST.get('body')

#             recipient_users = CustomUser.objects.filter(id__in=recipient_ids)
#             recipient_emails = recipient_users.values_list('email', flat=True)

#             if recipient_emails:
#                 send_mail(
#                     subject,
#                     body,
#                     sender.email,
#                     recipient_emails,
#                     fail_silently=False,
#                 )

#                 for recipient_user in recipient_users:
#                     Email.objects.create(
#                         subject=subject,
#                         body=body,
#                         sender=sender,
#                         recipient=recipient_user
#                     )

#                 return JsonResponse({'success': 'Email sent successfully'})
#             else:
#                 return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
#         else:
#             form = EmailForm()
#     else:
#         return render(request, 'mailmate/send_email.html')


@login_required
@permission_required('mailmate.can_send_email', raise_exception=True)
def send_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            sender = request.user
            recipient_ids = request.POST.getlist('recipients')
            subject = request.POST.get('subject')
            body = request.POST.get('body')

            recipient_users = CustomUser.objects.filter(id__in=recipient_ids)

            if recipient_users.exists():
                for recipient_user in recipient_users:
                    # Create the email object
                    email_obj = Email.objects.create(
                        subject=subject,
                        body=body,
                        sender=sender,
                        recipient=recipient_user
                    )
                    # Call the Celery task
                    send_scheduled_email.delay(email_obj.id)

                messages.success(request, 'Emails are being sent.')
                return redirect('email_success')  # Assuming you have a success URL
            else:
                messages.error(request, 'No valid recipients.')
        else:
            messages.error(request, 'Form is not valid.')

    form = EmailForm()  # This should be outside the 'if' block to handle GET requests as well
    return render(request, 'mailmate/send_email.html', {'form': form})


# View for retrieving and displaying emails
@login_required
def view_emails(request, folder_id=None):
    if folder_id:
        emails = Email.objects.filter(recipient=request.user, folders__id=folder_id).order_by('-timestamp')
    else:
        emails = Email.objects.filter(recipient=request.user).order_by('-timestamp')
    
    return render(request, 'mailmate/view_emails.html', {'emails': emails})


# View for managing contact lists
@login_required
def manage_contact_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_ids = request.POST.getlist('contacts')

        contact_list, created = ContactList.objects.get_or_create(name=name, user=request.user)
        contact_list.contacts.clear()

        for contact_id in contact_ids:
            contact = CustomUser.objects.get(id=contact_id)
            contact_list.contacts.add(contact)

        contact_list.save()
        return redirect('contact_list_success')
    else:
        # Render the contact list form
        return render(request, 'mailmate/manage_contact_list.html')


# View for managing folders
@login_required
def manage_folders(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        folder = Folder.objects.create(name=name, user=request.user)
        serializer = FolderSerializer(folder)
        return redirect('folder_success')
    else:
        folders = Folder.objects.filter(user=request.user)
        serializer = FolderSerializer(folders, many=True)
        return render(request, 'mailmate/manage_folders.html')
    

def email_success(request):
    return render(request, 'mailmate/email_success.html')


def test(request):
    return render(request, 'mailmate/test.html')
