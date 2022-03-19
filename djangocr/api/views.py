from django.shortcuts import render

# Create your views here.
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django import forms
from django.core.files.storage import default_storage
from .models import Attachment

import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt
from PIL import Image
import sys
import json
import re

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
			# print(read(instance.files.path))
			ocr = KTPOCR(instance.files.path)
			word = ocr.to_json()
			print(word)
			json_object = json.loads(word)
		# serializer = SnippetSerializer(data=request.data)
		# if serializer.is_valid():
		#     serializer.save()
		#     return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(json_object)

class KTPInformation(object):
	def __init__(self):
		self.nik = ""
		self.nama = ""
		self.tempat_lahir = ""
		self.tanggal_lahir = ""
		self.jenis_kelamin = ""
		self.golongan_darah = ""
		self.alamat = ""
		self.rt = ""
		self.rw = ""
		self.kelurahan_atau_desa = ""
		self.kecamatan = ""
		self.agama = ""
		self.status_perkawinan = ""
		self.pekerjaan = ""
		self.kewarganegaraan = ""
		berlaku_hingga = "SEMUR HIDUP"

class KTPOCR(object):
	def __init__(self, image):
		self.image = cv2.imread(image)
		self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
		self.th, self.threshed = cv2.threshold(self.gray, 127, 255, cv2.THRESH_TRUNC)
		self.result = KTPInformation()
		self.master_process()

	def process(self, image):
		raw_extracted_text = pytesseract.image_to_string((self.threshed), lang="ind")
		return raw_extracted_text

	def word_to_number_converter(self, word):
		word_dict = {
			'|' : "1"
		}
		res = ""
		for letter in word:
			if letter in word_dict:
				res += word_dict[letter]
			else:
				res += letter
		return res


	def nik_extract(self, word):
		word_dict = {
			'b' : "6",
			'e' : "2",
		}
		res = ""
		for letter in word:
			if letter in word_dict:
				res += word_dict[letter]
			else:
				res += letter
		return res
	
	def extract(self, extracted_result):
		# print(extracted_result.replace('\n', ' -- '))
		for word in extracted_result.split("\n"):
			if "NIK" in word:
				word = word.split(':')
				self.result.nik = self.nik_extract(word[-1].replace(" ", ""))
				continue

			if "Nama" in word:
				word = word.split(':')
				self.result.nama = word[-1].replace('Nama ','')
				continue

			if "Tempat" in word:
				word = word.split(':')
				try:
					self.result.tanggal_lahir = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])[0]
					tempat_lahir = word[-1].replace(self.result.tanggal_lahir, '')
					if "." in tempat_lahir:
						tempat_lahir = "".join(tempat_lahir.split('.'))
					self.result.tempat_lahir = tempat_lahir
				except:
					self.result.tempat_lahir = ""
				continue

			if 'Darah' in word:
				print(word)
				self.result.jenis_kelamin = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)[0]
				word = word.split(':')
				try:
					self.result.golongan_darah = re.search("(O|A|B|AB)", word[-1])[0]
				except:
					self.result.golongan_darah = '-'
			if 'Alamat' in word:
				self.result.alamat = self.word_to_number_converter(word).replace("Alamat ","")
			if 'NO.' in word:
				self.result.alamat = self.result.alamat + ' '+word
			if "Kecamatan" in word:
				try:
					self.result.kecamatan = word.split(':')[1].strip()
				except:
					self.result.kecamatan = ""
			if "Desa" in word:
				print(word)
				wrd = word.split()
				desa = []
				for wr in wrd:
					print("wr",wr)
					if not 'desa' in wr.lower():
						if wr != " " and wr != ":":
							desa.append(wr)
				self.result.kelurahan_atau_desa = ' '.join(desa)
			if 'Kewarganegaraan' in word:
				print("word",word)
				try:
					kewarganegaraan = word.split(':')[1].strip()
					if "WNI" in kewarganegaraan:
						kewarganegaraan = "WNI"
				except:
					kewarganegaraan = "WNI"
				self.result.kewarganegaraan = kewarganegaraan
			if 'Pekerjaan' in word:
				wrod = word.split()
				pekerjaan = []
				for wr in wrod:
					if not '-' in wr:
						pekerjaan.append(wr)
				result_pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan', '').strip()
				print("word",word)
				if "PELAJAR" in result_pekerjaan:
					result_pekerjaan = "PELAJAR/MAHASISWA"
				self.result.pekerjaan = result_pekerjaan 
			if 'Agama' in word:
				agama = word.replace('Agama',"").strip()
				if "ISLAM" in agama :
					agama = "ISLAM"
				self.result.agama = agama
			if 'Perkawinan' in word:
				status_perkawinan = word.split(':')[1]
				if "BELUM" in word.split(':')[1]:
					status_perkawinan = "BELUM KAWIN"
				self.result.status_perkawinan = status_perkawinan
				
			if "RTRW" in word:
				print(word)
				word = word.replace("RT/RW",'')
				self.result.rt = word.split('/')[0].strip()
				self.result.rw = word.split('/')[1].strip()

	def master_process(self):
		raw_text = self.process(self.image)
		self.extract(raw_text)

	def to_json(self):
		return json.dumps(self.result.__dict__, indent=4)



