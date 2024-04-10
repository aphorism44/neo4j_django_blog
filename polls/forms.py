from django import forms


class EntryForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    entry_id = forms.CharField(widget=forms.HiddenInput)
    previous_entry_id = forms.CharField(widget=forms.HiddenInput, required=False)
    next_entry_id = forms.CharField(widget=forms.HiddenInput, required=False)
