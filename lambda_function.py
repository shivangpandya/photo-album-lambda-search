import json
import boto3
from botocore.vendored import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

def clearIndices():
    host = 'https://search-photos-khcjss3c77o2erqokp2pi6dvea.us-east-1.es.amazonaws.com/photos/'
    res = requests.delete(host)
    res = json.loads(res.content.decode('utf-8'))
    return res   

def searchIndices():
    host = 'https://search-photos-khcjss3c77o2erqokp2pi6dvea.us-east-1.es.amazonaws.com/photos/_search?q=dog'
    res = requests.get(host)
    res = json.loads(res.content.decode('utf-8'))
    return res

def searchElasticIndex(search):
    print("hello")
    photos = []
    for s in search:
        host = 'https://search-photos-khcjss3c77o2erqokp2pi6dvea.us-east-1.es.amazonaws.com/photos/_search?q='+s
        res = requests.get(host)
        res = json.loads(res.content.decode('utf-8'))
        print(res)
        for item in res["hits"]["hits"]:
            bucket = item["_source"]["bucket"]
            key = item["_source"]["objectKey"]
            photoURL = "https://{0}.s3.amazonaws.com/{1}".format(bucket,key)
            photos.append(photoURL)
    return photos

def prepareForSearch(res):
    photos = []
    if res["slots"]["query"] != None:
        photos.append(res["slots"]["query"])
    if res["slots"]["search"] != None:
        photos.append(res["slots"]["search"])
    return photos

def sendToLex(message):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='photosforsearch',
        botAlias='photos',
        userId='sunidhicloud',
        inputText=message)
    return response
    
def lambda_handler(event, context):
    # TODO implement
    print("hello")
    credentials = boto3.Session().get_credentials()
    region = "us-east-1"
    service = "es"
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )
    photos = []
    print(event)
    # res = clearIndices() used to clear indexes in ES 
    # res = searchIndices() #used to check index
    message = event["params"]["querystring"]["q"]
    resFromLex = sendToLex(message)
    search = prepareForSearch(resFromLex)
    photos = searchElasticIndex(search)
    print("Reached end of search function")
    # print(photos)
    return {
        'statusCode': 200,
        'body': json.dumps(photos)
    }
