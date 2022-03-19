from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django import forms
from django.core.files.storage import default_storage

class UploadFileForm(forms.Form):
	title = forms.CharField(max_length=50)
	file = forms.FileField()


def index(request):
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			# handle_uploaded_file(request.FILES['file'])
			file = request.FILES['myfile']
			file_name = default_storage.save(file.name, file)
			print(file_name)
			HttpResponse("Hello POST.")

	return HttpResponse("Hello, world. You're at the polls index.")
