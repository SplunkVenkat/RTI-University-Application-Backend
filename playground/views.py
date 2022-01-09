# from django.shortcuts import render
# from django.http import HttpResponse

# # Create your views here.
# def sayhello(request):
#     return HttpResponse({'status':200})
from django.shortcuts import render

from django.http.response import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from playground.models import  Application, ApplicationDropDown, CommissionAppeal, FirstAppeal
from playground.serializers import  ApplicationSerializer , ApplicationDropdownSerializer, CommissionAppealSerializer, FirstAppealSerializer
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
import csv
from django.utils.encoding import smart_str


@api_view(['GET'])
def application_csv_download(request):
    response = HttpResponse(content_type='text/csv')
    now = datetime.now()
    date_time = now.strftime("%m/%d/%y")
    response['Content-Disposition'] = 'attachment; filename="applicants-as-of-now-{}.csv"'.format(date_time)
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow([
		smart_str(u"S.no"),
		smart_str(u"Application number"),
		smart_str(u"Name"),
		smart_str(u"Mobile number"),
        smart_str(u"Date created"),
		smart_str(u"First appeal"),
        smart_str(u"Commision appeal"),
		smart_str(u"Application status"),
	])
    applicants = Application.objects.all()
    i=1
    for applicant in applicants:
        writer.writerow([
		smart_str(i),
		smart_str(applicant.application_number),
		smart_str(applicant.name),
		smart_str(applicant.mobilenumber),
        smart_str(applicant.date_created),
		smart_str('Yes' if applicant.first_appeal else 'No'),
        smart_str('Yes' if applicant.commission_appeal else 'No'),
		smart_str('Complete' if applicant.application_status else 'In Progress'),
	    ])
        i=i+1
    return response


# Application view dd
class ApplicationView(APIView):

    def get_object(self, pk=None):
        try:
            return Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, format=None ,pk=None):
        if pk:
             app = Application.objects.get(pk=pk)
             serializer = ApplicationSerializer(app)
             return Response(serializer.data, status=status.HTTP_200_OK)
        applications = Application.objects.all()
        applications_serializer = ApplicationSerializer(applications, many=True)
        return Response(applications_serializer.data)

    def post(self, request, format=None):
         application_serializer = ApplicationSerializer(data=request.data,partial=True)
         if application_serializer.is_valid():
             application_serializer.save()
             return Response(application_serializer.data, status=status.HTTP_201_CREATED) 
         return Response(application_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, format=None):
        appId = request.query_params["id"]
        applicant = Application.objects.get(pk=appId)
        serializer = ApplicationSerializer(applicant, data=request.data, partial=True)
        if serializer.is_valid():
            applicant = serializer.save()
            return Response(ApplicationSerializer(applicant).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None ,pk=None):
        fa_or_ca = request.query_params.get("appeal")
        if pk:
             app = Application.objects.get(pk=pk)
             fa = None
             ca = None
             if  app.first_appeal:
                 fa = app.first_appeal
             if  app.commission_appeal:
                 ca = app.commission_appeal
             try:
                if fa_or_ca:
                     if fa_or_ca == "fa":
                         fa.delete()
                     if fa_or_ca == "ca":
                         ca.delete()
                else :
                    app.delete()
                    if fa:
                        fa.delete()
                    if ca:
                        ca.delete()

                return Response(status=status.HTTP_200_OK)
             except:
                 return Response(status=status.HTTP_400_BAD_REQUEST)

        


# pagination config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# filter config
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])

# application pagination view
class ApplicationRecordsView(generics.ListAPIView):
    search_fields = ['application_number']
    filter_backends = (DynamicSearchFilter,)
    queryset =  Application.objects.all()
    serializer_class = ApplicationSerializer
    pagination_class = StandardResultsSetPagination

# application pagination view
class ApplicationRecordsRemainingView(generics.ListAPIView):
    search_fields = ['application_number']
    filter_backends = (DynamicSearchFilter,)
    max_dt = datetime.today() - timedelta(days=28)
    queryset =  Application.objects.filter(date_receive__lte=max_dt,application_status=False)
    serializer_class = ApplicationSerializer
    pagination_class = StandardResultsSetPagination

# dropdown configuration view
class ApplicationDropdownView(APIView):

     def get(self, request, format=None):
        snippets = ApplicationDropDown.objects.all()
        serializer = ApplicationDropdownSerializer(snippets, many=True)
        return Response(serializer.data)

     def post(self, request, format=None):
        dropdown_serializer = ApplicationDropdownSerializer(data=request.data)
        if dropdown_serializer.is_valid():
            dropdown_serializer.save()
            return Response(dropdown_serializer.data, status=status.HTTP_201_CREATED)
        return Response(dropdown_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
     def patch(self, request, format=None):
        appId = request.query_params["id"]
        applicant = ApplicationDropDown.objects.get(pk=appId)
        serializer = ApplicationDropdownSerializer(applicant, data=request.data, partial=True)
        if serializer.is_valid():
            applicant = serializer.save()
            return Response(ApplicationDropdownSerializer(applicant).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

     def delete(self, request, format=None ,pk=None):
         appId = request.query_params["id"]
         applicant = ApplicationDropDown.objects.get(pk=appId)
         applicant.delete()
         return Response(status=status.HTTP_200_OK)

class FirstAppealView(APIView):
    
    def post(self, request, format=None):
        appId = request.query_params["id"]
        applicant = Application.objects.get(pk=appId)
        FA_serializer = FirstAppealSerializer(data=request.data)
        if FA_serializer.is_valid():
            FA_serializer.save()
            applicant['first_appeal']=FirstAppeal.objects.get(pk=FA_serializer.data['id']) 
            applicant.save()
            return Response(FA_serializer.data, status=status.HTTP_201_CREATED)
        return Response(FA_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class CommissionAppealView(APIView):
    
    def post(self, request, format=None):
        appId = request.query_params["id"]
        applicant = Application.objects.get(pk=appId)
        CA_serializer = CommissionAppealSerializer(data=request.data)
        if CA_serializer.is_valid():
            CA_serializer.save()
            applicant['commission_appeal']=CommissionAppeal.objects.get(pk=CA_serializer.data['id']) 
            applicant.save()
            return Response(CA_serializer.data, status=status.HTTP_201_CREATED)
        return Response(CA_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
