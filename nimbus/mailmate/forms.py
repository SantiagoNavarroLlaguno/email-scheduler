from django import forms

class EmailForm(forms.Form):
    recipients = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter recipient IDs separated by commas'}), help_text='Enter recipient IDs separated by commas.')
    subject = forms.CharField(max_length=255)
    body = forms.CharField(widget=forms.Textarea)
    