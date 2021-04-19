from django import forms
import re
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from validation.models import Issue


class Login(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control form-restrict"}),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control form-restrict"}),
    )


class Register(forms.Form):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control form-restrict"}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control form-restrict"}),
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control form-restrict"}),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control form-restrict"}),
    )

    CHOICES = [
        ("expert", "Language Expert"),
        ("linguist", "Linguist"),
        ("instructor", "Instructor"),
        ("learner", "Learner"),
    ]
    role = forms.ChoiceField(
        label="I am a(n)...",
        choices=CHOICES,
        widget=forms.RadioSelect,
        required=False,
        help_text="""
        Community members are considered language experts or active members in a Cree-speaking community. <br>
        Linguists are expected to look at analyses and lemmas. <br>
        Instructors are those who are teaching others or advanced language learners.<br>
        Learners are students or other people currently learning the language.<br>
        """,
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.search(
            r"^\w+$", username
        ):  # checks if all the characters in username are in the regex. If they aren't, it returns None
            raise forms.ValidationError(
                "Username can only contain alphanumeric characters and the underscore."
            )
        try:
            User.objects.get(
                username=username
            )  # this raises an ObjectDoesNotExist exception if it doesn't find a user with that username
        except ObjectDoesNotExist:
            return username  # if username doesn't exist, this is good. We can create the username
        raise forms.ValidationError("Username is already taken.", code="invalid")


class EditSegment(forms.Form):
    cree = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    translation = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    analysis = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control bottom-margin"}),
    )


class FlagSegment(forms.ModelForm):
    ISSUES = [
        ("bad_cree", "There's a better spelling for the transcription (Cree word)"),
        ("bad_english", "There's a better spelling for the translation (English word)"),
        ("bad_rec", "One or more of these recordings are not of this word"),
        ("other", "Something else (please specify)"),
    ]
    issues = forms.MultipleChoiceField(
        choices=ISSUES, required=False, widget=forms.CheckboxSelectMultiple
    )

    cree_suggestion = forms.CharField(
        help_text="Suggest a better Cree spelling",
        required=False,
        widget=forms.Textarea,
    )

    english_suggestion = forms.CharField(
        help_text="Suggest a better English word or phrase",
        required=False,
        widget=forms.Textarea(attrs={"class": "commment"}),
    )

    comment = forms.CharField(
        help_text="Use the space above to suggest a new spelling or make a few notes about why you're reporting an issue "
        "with this entry",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control bottom-margin"}),
    )

    phrase_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Issue
        fields = ["phrase_id"]
