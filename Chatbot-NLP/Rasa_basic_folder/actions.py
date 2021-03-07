from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet,FollowupAction,AllSlotsReset
import zomatopy
import json
import difflib
import pprint
import pandas as pd
from flask_mail import Mail, Message
import os
import flask

def data_getter(lat,lon,cuisine,upper,lower,sort):
    cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'american':1,'north indian':50,'south indian':85,'mexican':73}
    zomato = zomatopy.initialize_app({"user_key":"0e4d797c7f6b1c44591533dc02d0c069"})
    address_all = []
    price_all = []
    rating_all = []
    for start in range(0,100,20):
      results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), limit=20, start=start,sort_price=sort)
      d = json.loads(results)
      response=""
      if d['results_found'] == 0:
        response= "no results"
      else:
        for restaurant in d['restaurants']:
          price = restaurant['restaurant']['average_cost_for_two']
          if price>=lower and price<=upper:
            rating_all.append(float(restaurant['restaurant']['user_rating']['aggregate_rating']))
            address_all.append(restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address'])
            price_all.append(restaurant['restaurant']['average_cost_for_two'])
    df = pd.DataFrame({'price':price_all,'rating':rating_all,'address':address_all})
    df = df.sort_values('rating',ascending=False).head(10)
    if len(df)>0:
        return df, True
    else:
        return response, False
			
class ActionSendMail(Action):
    def name(self):
      return 'action_send_mail'
    
    def run(self, dispatcher, tracker, domain):
      user_mail = tracker.get_slot('email')
      data = pd.read_csv('Top_10.csv')
      app = flask.Flask(__name__)
      app.config.update(DEBUG=True,MAIL_SERVER='smtp.gmail.com',MAIL_PORT=465,
                        MAIL_USE_SSL=True,MAIL_USERNAME = 'appfoddie@gmail.com',
                        MAIL_PASSWORD = 'login@1234')
      mail = Mail(app)
      try:
        msg = Message("Top restaurants",
                sender="appfoddie@gmail.com",
                recipients=[user_mail])
        
        msg.html = data.to_html()
        with app.app_context():
            mail.send(msg)
        dispatcher.utter_message('Mail Sent')
        os.unlink('Top_10.csv')
        return [SlotSet('send_email','done')]
      except Exception as e:
        return [SlotSet('send_email',None)]
		
class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"0e4d797c7f6b1c44591533dc02d0c069"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		upper = 0 
		lower = 0
		if '300' in price and '700' not in price:
		    upper = 299
		    sort = 'asc'
		elif '300' in price and '700' in price:
			upper = 700
			lower = 300
			sort = 'asc'
		else:
			lower = 700
			upper = 100000
			sort = 'desc'
		
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		print(lat,lon,upper,lower,loc)
		df, flag = data_getter(lat,lon,cuisine,upper,lower,sort)
		response = ""
		if flag and len(df)>0:
			df['rating'] = df['rating'].astype(str)
			print(len(df))
			df2 = df.copy()
			df2['name_rating'] = (df2['address']+' has been rated ' + df2['rating'])
			df2 = df2.head(5)
			response = '\n'.join(list(df2['name_rating']))
			df.to_csv('Top_10.csv',index=False)
		elif flag==False and len(df)>0:
			response = df
		else:
                        print(len(df))
                        response = 'No data'
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc)]

class ActionVerifyCity(Action):
    def get_closest_matches(self,city,all_cities):
      max_match = -1
      max_name = ""
      for name in all_cities:
        match =  difflib.SequenceMatcher(None, name, city).ratio()
        if match>max_match:
          max_match = match
          max_name = name
      diff_match = len(city) - int(max_match)
      if diff_match>2:
        if max_match < 0.85:
          max_name = ""
      else:
        if max_match < 0.78:
          max_name = ""
      return max_name
          
    def name(self):
      return 'action_verify_city'

    def run(self, dispatcher, tracker, domain):
      city = tracker.get_slot('location')
      
      all_cities = ['Mumbai','Delhi','Kolkata','Chennai','Bangalore','Hyderabad','Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad',
              'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 
              'Bikaner', 'Bilaspur', 'Bokaro Steel City', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 
              'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli-Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar',
              'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow',
              'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj',
              'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', '1Thrissur', 
              'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal']
      synonym_city = {'Bangalore':['Bengaluru','Bangaluru'],'Delhi':['New Delhi'],'Mumbai':['Bombay','Bombai'],'Kolkata':['Calcutta','Kolkatta'],'Prayagraj':['Allahabad']}
      all_syns = ['Bengaluru','Bangaluru','New Delhi','Bombay','Bombai','Calcutta','Allahabad']
      if city.title() in all_cities:
        return [SlotSet('location',city)]
      elif city.title() in all_syns:
        replacement_city = ''
        for rep in synonym_city:
            if city.title() in synonym_city[rep]:
                replacement_city = rep
        return [SlotSet('location',replacement_city)]
      else:
        matching_name = self.get_closest_matches(city.title(), all_cities)
        if matching_name != "" :
          dispatcher.utter_message(f'{city} not found, will search instead for {matching_name}')
          return [SlotSet('location',matching_name)]
        else:
          dispatcher.utter_message(f'Sorry we donot operate in {city}.')
          return [SlotSet('location',None)]

class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
          
