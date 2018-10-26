from airbnb.models import BnbHost, BnbListing, BnbReview
import csv, datetime, traceback, sys
listFiles=[r'C:\Users\schan\Desktop\PGPBA\Class3\data_listing.csv', r'C:\Users\schan\Desktop\PGPBA\Class3\data_review.csv']
for file in listFiles:
    with open(file, mode='r',encoding='utf8') as infile:
        Model = BnbHost
        if 'data_listing' in infile.name:
            Model = BnbListing
        elif 'data_review' in infile.name:
            Model = BnbReview
        reader = csv.reader(infile)
        reader = list(reader)
        floatLen = float(len(reader))
        print('*',floatLen)
        header=[]
        i=0
        for row in reader:
            if(i==0):
                header=row
                print(header)
            else:
                objDict={}
                j=0
                print(1)
                for item in row:
                    if item.strip()=='':
                        item=None
                        objDict[header[j].replace(u'\ufeff', '')]=item
                        j=j+1
                        continue
                    if header[j].replace(u'\ufeff', '') in ('host_since','review_date'):
                        objDict[header[j].replace(u'\ufeff', '')]=datetime.datetime.strptime(item, '%m/%d/%Y')
                    elif header[j].replace(u'\ufeff', '') in ('host_id','listing_id','review_id'):
                        if header[j].replace(u'\ufeff', '')=='host_id' and Model.__name__=='BnbListing':
                            #print(j,item,Model)
                            #print(row)
                            objDict[header[j].replace(u'\ufeff', '')]=BnbHost.objects.get(pk=int(item))
                        elif header[j].replace(u'\ufeff', '')=='listing_id' and Model.__name__=='BnbReview':
                            objDict[header[j].replace(u'\ufeff', '')]=BnbListing.objects.get(pk=int(item))
                        else:
                            objDict[header[j].replace(u'\ufeff', '')]=int(item)
                    else:
                        objDict[header[j].replace(u'\ufeff', '')]=item
                    j=j+1
                objModel=Model(**objDict)
                try:
                    objModel.save()
                except:
                    print(objDict)
                    print(traceback.format_exc())
                    sys.exit()
                print(str((i*100)/floatLen)+'%',i)
            i=i+1