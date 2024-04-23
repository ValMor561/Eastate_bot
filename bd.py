import psycopg2
import config
from datetime import datetime

#Класс для подключения к базе данных
class BDRequests():

    #Установка соединения
    def __init__(self):
        self.connection = psycopg2.connect(
            host=config.HOST,
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            client_encoding='utf8'
        )

    def __del__(self):
        self.connection.close()

    def insert_big_city(self, data, time):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."AllField" (city, district, flat_type, payment_type, cost_limit, fioandphone, good_time) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        cursor.execute(insert_query, (data['city'], data['district'], data['flat_type'], data['payment_type'], data['cost_limit'], data['fioandphone'], time))
        self.connection.commit()

    def insert_saratov(self, data, good_time):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."Saratov" (offer_type, fioandphone, good_time) VALUES (%s, %s, %s);'
        cursor.execute(insert_query, (data['type'], data['fioandphone'], good_time))
        self.connection.commit()

    def insert_consult(self, data, good_time):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."Consult" (fioandphone, question, good_time) VALUES (%s, %s, %s);'
        cursor.execute(insert_query, (data['fioandphone'], data['comment'], good_time))
        self.connection.commit()

    def insert_policy(self, data, good_time):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."Policy" (policy_type, offer, fioandphone, good_time) VALUES (%s, %s, %s, %s);'
        cursor.execute(insert_query, (data['type'], data['offer'], data['fioandphone'], good_time))
        self.connection.commit()

    def insert_policy_all(self, data, good_time):
        cursor = self.connection.cursor()
        insert_query = f'INSERT INTO public."Policy" (policy_type, offer, fioandphone, position, employer, client_weight, height, diseases, bank, count, building_year, gas, good_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        cursor.execute(insert_query, (data['type'], data['offer'], data['fioandphone'], data['position'], data['employer'], data['weight'], data['height'], data['diseases'], data['bank'], data['count'], data['year'], data['gas'], good_time))
        self.connection.commit()

    def delete_by_id(self, tablename, id):
        cursor = self.connection.cursor()
        delete_query = f'DELETE FROM public."{tablename}" WHERE id = %s;'
        cursor.execute(delete_query, (id, ))
        self.connection.commit()

    def select_all(self, tablename):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM public."{tablename}";')
        result = cursor.fetchall()
        return result
