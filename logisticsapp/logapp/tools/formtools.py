'''
 * Rwanda Law Reform Comission
 *
 * Developed by Sium, Kigali, Rwanda 2016-2017. All Rights Reserved
 *
 * This content is protected by national and international patent laws.
 *
 * Possession and access to this content is granted exclusively to Developers
 * of RLRC and Sium, while full ownership is granted only to Rwanda Law Reform Comission.
 
 *
 * @package	RLWC - LRC
 * @author	Kiflemariam Sium (kmsium@gmail.com || sium@go.rw || sium@iconicdatasystems.com)
 * @copyright	Copyright (c) RLCR Limited, 2017
 * @license	http://
 * @link	http://
 * @since	Version 1.0.0
 * @filesource
 '''
#Form error checker

def createErrorDataJSON(errors,version=1):
	'''
	Returns list of errors in a friendly and combined manner.

	@input: errors is a list of possible errors from serailizers (serializer.errors) or a simple dictionary of errors
	@input: version ==1 means the errors is from serailizers. else, it is a diciontary of errors from non-serailizers.

	Note we don't send back the "field" that caused the error her; just the error messages. E.g.

	errors={'birtdate':"Must be 18-20"}

	We return only the "Must be 18-20" as per front-end requirement. You can easily adjust that to return the key and the value


	return: an array of error messages


	'''



	reply=[]

	if version==1:

		for item in errors:
			reply.append(errors[item][0])

	else:
		#most notablly called from crops/views.py and uses no serializers.
		for item in errors:
			reply.append(errors[item])

	return reply



def csvFromUrlToNumbers(p, num='int',ignore_zero=True,reply_format='list'):
	'''

	returns an array list or a csv of numbers only from p

	@input p: a CSV input of data of any characters combination
	@input num: which characters are we interested it it? it can be:
		int=>integers
		dec=>float/decimials
		str=>string (not properly implemented yet but hte idea is to filter out only strings

	@input ignore_zero:if num=int or dec, should we return zeros or ignore it?

	@input reply_format: return should be array or csv format string?


	'''
	reply=list()

	#remove last ,
	
	p=str(p).strip()


	
	if p.endswith(','):
		p=p[:-1]

	data=p

	if data:
		data=str(data)
		data=data.split(',')
		if num=='int':
			if ignore_zero:
				for i in data:
					#is i a number?

					if i.isdigit() and int(i)>0:
						reply.append(i)
			else:
				for i in data:
					#is i a number?

					if i.isdigit():
						reply.append(i)

		elif num=='dec':
			if ignore_zero:

				for i in data:
					#is i a number?

					if i.isdigit() and int(i)>0:
						reply.append(i)
			else:
				for i in data:
					#is i a number?

					if i.isdigit():
						reply.append(i)


		elif num=='str':
			for i in data:
				#is i a number?
				i=str(i)

				reply.append(i.strip())


	if reply_format=='str':
		return ','.join(reply)

	return reply