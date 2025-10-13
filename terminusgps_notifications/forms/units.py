from django import forms
from django.utils.translation import gettext_lazy as _


class WialonUnitSelectionForm(forms.Form):
    units = forms.MultipleChoiceField(
        choices=[],
        help_text=_("Ctrl+click to select multiple. Cmd+click on Mac."),
        widget=forms.widgets.SelectMultiple(
            attrs={
                "class": "p-2 border rounded bg-gray-100",
                "autofocus": True,
            }
        ),
    )
