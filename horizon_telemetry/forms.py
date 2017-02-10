import datetime

import django.forms

import horizon
from horizon import forms
from django.forms.extras.widgets import SelectDateWidget

class DateForm(forms.Form):
    """A simple form for selecting a range of time."""
    start = forms.DateField(input_formats=("%Y-%m-%d",))
    end = forms.DateField(input_formats=("%Y-%m-%d",))

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)
        self.fields['start'].widget.attrs['data-date-format'] = "yyyy-mm-dd"
        self.fields['end'].widget.attrs['data-date-format'] = "yyyy-mm-dd"