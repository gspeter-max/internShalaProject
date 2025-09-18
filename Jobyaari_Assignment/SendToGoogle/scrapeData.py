from email.charset import add_charset
from pytrends.request import TrendReq 
import time 

def getResponse( kw_list):
    
    response = TrendReq(timeout = (4,7))
    try:
        response.build_payload( kw_list, cat = 9 , timeframe = 'now 1-H')
        print( response.related_quries()) 
        getting_data = response.trending_searches(pn = 'IN') 
        print('first thing is happened')

        print(getting_data)
    except Exception as e:
        print(f'60 mins is runing ')
        print(f'because the error : {e}')
        time.sleep(60)

    time.sleep(10)
