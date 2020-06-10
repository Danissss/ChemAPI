from django.shortcuts import render
from django.http import HttpResponse

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen
import requests
import json





# get value from post request: request.POST.get("title", "")
# For convenience, a dictionary-like object that searches POST first, then GET. Inspired by PHP’s $_REQUEST.
# def login(request):
#     if request.method == 'POST':
#         # Your code for POST
#     else:
#         # Your code for GET
#     return render(request, 'login.html')

def predict_som(request, structure, protein):
	print(structure, protein)
	data = {"structure": structure, "protein": protein}
	# # res = requests.post("http://localhost:8080/api/sompred")
	# request = Request("http://127.0.0.1:8080/api/sompred", urlencode(data).encode())
	# print(request)
	# json = urlopen(request).read().decode()
	# print(json)

	res = requests.post("http://localhost:8080/api/sompred/", data=data)
	return HttpResponse(res.content.decode(), content_type="application/json") 




