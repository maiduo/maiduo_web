#! -*- encoding:utf-8 -*-

from django import forms
from models import Message

class MessageForm(forms.ModelForm):
    message_type = forms.CharField(max_length=1, initial="T", required=False)

    class Meta:
        model = Message
