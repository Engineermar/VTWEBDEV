

def viewRecordRevisions(view_for_model,record_id):
	'''
	For history recording reasons, certain changes to items are recorded such as Catalog. Here, we see the change a specific item
	went thru.

	@input: view_for_model : the name of the database model passed by reference
			record_id : the db id of the record whose revision history we want to see
	@output: list of reviesions for the given item

	Note:

	Security is checked by calling application only.
	
	'''

	fields=['id','pre_name','new_name','createdon','user__first_name','user__user_name','user_id']


	return list(view_for_model.objects.filter(source_id=record_id).values(*fields).order_by('-createdon',))


def addRecordRevision(view_for_model,record_id,existing_name,new_name,added_by,kind):
	'''
	add a new revision to the model.

	returns reply and status as a normal APIView setup

	@input: view_for_model: the database model where the revision is stored
			record_id is the id of the record to be revised (e.g. a Category's name was changed)
			existing_name: the current name of the record (e.g. Computing)
			new_name: the new name of the record (e.g. ICT Item)
			added_by: the user who made the changes
			kind: a string that is supposed to be a descriptive of the kind of the record that was changed (.e.g. Products, Department etc)



	We add only if existing and new are diferent

	Output: None
	
	'''
	if new_name.lower()!=existing_name.lower():
		

		status=200
		
		
		try:
			fields={'pre_name':existing_name,'new_name':new_name,'source_id':record_id,'user_id':added_by}

			add_new=view_for_model(**fields)
			add_new.save()
			if not add_new:
				#log the error here
				pass
				

		except:
			#log the  error here
			pass