from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	phone_number = forms.CharField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "last_name", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		user.phone_number = self.cleaned_data['last_name']
		if commit:
			user.save()
		return user