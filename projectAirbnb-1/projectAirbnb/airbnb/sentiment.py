import sklearn
import nltk
from airbnb.models import BnbReview
from sklearn.feature_extraction.text import CountVectorizer

def sentiment(valuesobjBnbReview):
    review=[]
    for objDict in valuesobjBnbReview:
        review.append(objDict['comments'])
    print(review)
    train = BnbReview.objects.all().values_list('comments',flat=True)
    sentiment = ['neg', 'pos']