from django import forms

class ImportObserverLogForm(forms.Form):
    observer_log = forms.FileField()
