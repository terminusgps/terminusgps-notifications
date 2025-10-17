from django import forms
from django.utils.translation import gettext_lazy as _


class WialonUnitSelectionForm(forms.Form):
    units = forms.TypedMultipleChoiceField(
        choices=[],
        help_text=_("Ctrl+click to select multiple. Cmd+click on Mac."),
        widget=forms.widgets.SelectMultiple(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "autofocus": True,
            }
        ),
        coerce=int,
    )
