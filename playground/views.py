# from django.shortcuts import render
# from django.http import HttpResponse

# # Create your views here.
# def sayhello(request):
#     return HttpResponse({'status':200})
from django.shortcuts import render

from django.http.response import JsonResponse
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


@api_view(['GET','POST','PATCH'])
def applications(request):
    if request.method == 'GET':
        applications = Application.objects.all()
        applications_serializer = ApplicationSerializer(applications, many=True)
        return Response(applications_serializer.data, safe=False)
    if request.method == 'POST':
        application_data = JSONParser().parse(request)
        app_id = Application.objects.filter(application_number__startswith=application_data['application_number']).order_by('-application_number').first()
        if app_id:
            application_data['application_number'] = app_id.application_number + 1
        else:
            application_data['application_number'] = application_data['application_number'] * 10000 + 1
        tutorial_serializer = ApplicationSerializer(data=application_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return Response(tutorial_serializer.data, status=status.HTTP_201_CREATED) 
        return Response(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        application_data = JSONParser().parse(request)
        appId = request.query_params["id"]
        applicant = Application.objects.get(pk=appId)
        # first appeal patch
        if application_data['first_appeal']:
            FA = FirstAppeal(appeal_reason = application_data['first_appeal']['appeal_reason'],
                            appeal_endorsement=application_data['first_appeal']['appeal_endorsement'],
                            appeal_application_number='FA'+application_data['application_number'],
                            appeal_date = application_data['first_appeal']['appeal_date'],
                            appeal_date_receive = application_data['first_appeal']['appeal_date_receive'])
            FA.save()
            applicant.first_appeal = FA
        # commission appeal patch
        if application_data['commission_appeal']:
            CA = CommissionAppeal(commission_date = application_data['commission_appeal']['commission_date'],
                            notice_date=application_data['commission_appeal']['notice_date'],
                            hearing_date=application_data['commission_appeal']['hearing_date'],
                            commission_application_number = 'CA'+application_data['application_number'],
                            commission_case_number = application_data['commission_appeal']['commission_case_number'],
                            commission_file_number = application_data['commission_appeal']['commission_file_number'])
            CA.save()
            applicant.commission_appeal = CA
        applicant.save()
        return Response({}, status=status.HTTP_201_CREATED) 


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
