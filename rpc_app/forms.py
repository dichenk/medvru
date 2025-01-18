from django import forms


class RpcForm(forms.Form):
    method = forms.CharField(
        initial='auth.check',
        help_text='Например: auth.check'
    )
    params = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text='JSON параметры метода'
    )
