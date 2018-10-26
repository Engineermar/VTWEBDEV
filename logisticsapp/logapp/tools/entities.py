'''
Used exclusively for entities in the system: Employees and HR Skeletons
'''



from django.db.models import Value,F

from hr.models import Employee,Head,Department,Division,Unit,Office

from django.db.models.functions import Concat


def entityInformation(entity_type,entity_id):
	'''
	Return the name or information of an entity (Employee,Head,Department,Division,Unit and Office)

	@input entity_type : the kind of entity we are interested n
	@input entity_id: the id of the entity we want

	@output: a dictionary with information about hte specicfic entity
	'''

	entity_info={}
	try:
		if entity_type=='Employee':
			entity_info=Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '), 'user__first_name'),email=F('user__email')).values('full_name','email','phone','id').get(company_id=entity_id)

		elif entity_type=='Head':
			entity_info=Head.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)

		elif entity_type=="Department":
			entity_info=Department.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)

		elif entity_type=='Division':
			entity_info=Division.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)

		elif entity_type=='Unit':
			entity_info=Unit.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
		elif entity_type=='Office':
			entity_info=Office.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
			

	except:
		entity_info={}


	return entity_info



