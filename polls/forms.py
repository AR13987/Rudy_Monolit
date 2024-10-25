from django import forms
from .models import UserProfile
from .models import Question



class UserProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    fields = ['first_name', 'last_name', 'phone_number', 'gender', 'avatar', 'email']



class QuestionForm(forms.ModelForm):
  choices = forms.CharField(
    label="Варианты ответов (через запятую)",
    widget=forms.Textarea,
    required=True
  )

  class Meta:
    model = Question
    fields = ['question_text', 'short_description', 'full_description', 'image', 'choices']
