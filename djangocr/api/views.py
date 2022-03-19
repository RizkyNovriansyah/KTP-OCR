from django.shortcuts import render

# Create your views here.
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django import forms
from django.core.files.storage import default_storage
from .models import Attachment

class UploadFileForm(forms.Form):
	file = forms.FileField()


class APIList(APIView):
	"""
	List all snippets, or create a new snippet.
	"""
	def get(self, request, format=None):
		# snippets = Snippet.objects.all()
		# serializer = SnippetSerializer(snippets, many=True)
		return Response({"hello get"})

	def post(self, request, format=None):
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			# handle_uploaded_file(request.FILES['file'])
			file = request.FILES['file']
			# file_name = default_storage.save(file.name, file)
			instance = Attachment(files=request.FILES['file'])
			instance.save()
			print(instance.files.path)
		# serializer = SnippetSerializer(data=request.data)
		# if serializer.is_valid():
		#     serializer.save()
		#     return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response({"hello post"})