from rest_framework import serializers 
from playground.models import Application, ApplicationDropDown, CommissionAppeal, FirstAppeal
 
 

class CommissionAppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionAppeal
        fields = ('id','commission_date',
                  'notice_date',
                  'hearing_date',
                  'commission_application_number',
                  'commission_case_number',
                  'commission_file_number')


class FirstAppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstAppeal
        fields = ('id','appeal_date',
                  'appeal_date_receive',
                  'appeal_application_number',
                  'appeal_reason',
                  'appeal_endorsement')

class ApplicationSerializer(serializers.ModelSerializer):
    first_appeal = FirstAppealSerializer(many=False)
    commission_appeal = CommissionAppealSerializer(many=False)
    class Meta:
        model = Application
        fields = ('id',
                  'name',
                  'of_name',
                  'date_created',
                  'address',
                  'mobilenumber',
                  'date_receive',
                  'is_svu',
                  'last_date',
                  'endorsement_date',
                  'endorsement',
                  'application_related',
                  'address_transmitted',
                  'application_number',
                  'first_appeal',
                  'commission_appeal',
                  'application_status')
        
    def create(self, validated_data):
         app_id = Application.objects.filter(application_number__startswith=validated_data['application_number']).order_by('-application_number').first()
         if app_id:
             validated_data['application_number'] = app_id.application_number + 1
         else:
             validated_data['application_number'] = validated_data['application_number'] * 10000 + 1
         instance = Application.objects.create(**validated_data)
         return instance

    def update(self, instance, validated_data):
        instance.name =  validated_data.get('name', instance.name)
        instance.of_name =  validated_data.get('of_name', instance.of_name)
        instance.date_created =  validated_data.get('date_created', instance.date_created)
        instance.address =  validated_data.get('address', instance.address)
        instance.mobilenumber =  validated_data.get('mobilenumber', instance.mobilenumber)
        instance.date_receive =  validated_data.get('dateReceive', instance.date_receive)
        instance.is_svu =  validated_data.get('is_svu', instance.is_svu)
        instance.last_date =  validated_data.get('last_date', instance.last_date)
        instance.application_status = validated_data.get('application_status', instance.application_status)
        if instance.is_svu == '1':
            instance.endorsement_date =  validated_data.get('endorsement_date', instance.endorsement_date)
            instance.endorsement =  validated_data.get('endorsement', instance.endorsement)
            instance.application_related = ''
            instance.address_transmitted = ''
        else:
            instance.application_related =  validated_data.get('application_related', instance.application_related)
            instance.address_transmitted =  validated_data.get('address_transmitted', instance.address_transmitted)
            instance.endorsement_date = None
            instance.endorsement = ''
        instance.application_number =  validated_data.get('application_number', instance.application_number)
        if validated_data.get('first_appeal'):
            FA_data = validated_data.pop('first_appeal')
            if FA_data:
                if instance.first_appeal:
                    instance.first_appeal.appeal_date = FA_data.get('appeal_date', instance.first_appeal.appeal_date)
                    instance.first_appeal.appeal_date_receive = FA_data.get('appeal_date_receive', instance.first_appeal.appeal_date_receive)
                    instance.first_appeal.appeal_application_number = FA_data.get('appeal_application_number', instance.first_appeal.appeal_application_number)
                    instance.first_appeal.appeal_reason = FA_data.get('appeal_reason', instance.first_appeal.appeal_reason)
                    instance.first_appeal.appeal_endorsement = FA_data.get('appeal_endorsement', instance.first_appeal.appeal_endorsement)
                    instance.first_appeal.save()
                else:
                    FA_data['appeal_application_number']="FA"+ str(instance.application_number)
                    FA_serializer = FirstAppealSerializer(data=FA_data)
                    if FA_serializer.is_valid():
                        FA_serializer.save()
                        instance.first_appeal = FirstAppeal.objects.get(pk=FA_serializer.data['id'])
        if validated_data.get('commission_appeal'):
            CA_data = validated_data.pop('commission_appeal')
            if CA_data:
                if instance.commission_appeal:
                    instance.commission_appeal.commission_date = CA_data.get('commission_date', instance.commission_appeal.commission_date)
                    instance.commission_appeal.notice_date = CA_data.get('notice_date', instance.commission_appeal.notice_date)
                    instance.commission_appeal.hearing_date = CA_data.get('hearing_date', instance.commission_appeal.hearing_date)
                    instance.commission_appeal.commission_application_number = CA_data.get('commission_application_number', instance.commission_appeal.commission_application_number)
                    instance.commission_appeal.commission_case_number = CA_data.get('commission_case_number', instance.commission_appeal.commission_case_number)
                    instance.commission_appeal.commission_file_number = CA_data.get('commission_file_number', instance.commission_appeal.commission_file_number)
                    instance.commission_appeal.save()
                else:
                    CA_serializer = CommissionAppealSerializer(data=CA_data)
                    CA_data['commission_application_number']="CA"+ str(instance.application_number)
                    if CA_serializer.is_valid():
                        CA_serializer.save()
                        instance.commission_appeal = CommissionAppeal.objects.get(pk=CA_serializer.data['id'])
        instance.save()
        return instance
class ApplicationDropdownSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = ApplicationDropDown
        fields = ('id',
                  'value_data')



 