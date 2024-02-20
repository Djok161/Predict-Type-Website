from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
import requests
from bs4 import BeautifulSoup
from  seleniumbase import Driver
import time
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

mystem = Mystem()
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(
	['магазин', 'номер', 'бесплатно', 'это', 'услуга', 'услуг', 'оказывать', '№', 'главная', 'главный', '|',
	 '-', 'официальный', 'сайт', 'онлайн'])

with open('controll/cites.txt', 'r', encoding='utf-8') as file:
	cities = [line.strip().lower() for line in file]

header = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
	          'application/signed-exchange;v=b3',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
	'cache-control': 'no-cache',
	'dnt': '1',
	'pragma': 'no-cache',
	'sec-fetch-mode': 'navigate',
	'sec-fetch-site': 'none',
	'sec-fetch-user': '?1',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
}
agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'


def preprocess_text(text):
	text = str(text)
	tokens = mystem.lemmatize(text.lower())
	tokens = [token for token in tokens if token not in russian_stopwords \
	          and token != " " \
	          and len(token) >= 3 \
	          and token.strip() not in punctuation \
	          and not any(char.isdigit() for char in token) \
	          and token.strip() not in cities]
	text = " ".join(tokens)
	return text


driver = Driver(browser="chrome",
                uc=True,
                headless2=True,
                incognito=True,
                agent=agent,
                do_not_track=True,
                undetectable=True, )


def get_page_info(url):
	try:
		response = requests.get(url, timeout=20)
		response.raise_for_status()

		# Если статус ответа равен 200 - едем дальше
		soup = BeautifulSoup(response.text, 'lxml')
		title = soup.title.text if soup.title else ""
		keywords = soup.find('meta', {'name': 'keywords'})
		keywords = keywords.get('content') if keywords else ""
		og_title = soup.find('meta', {'property': 'og:title'})
		og_title = og_title.get('content') if og_title else ""
		og_description = soup.find('meta', {'property': 'og:description'})
		og_description = og_description.get('content') if og_description else ""
		description = soup.find('meta', {'name': 'description'})
		description = description.get('content') if description else ""
		title = f'{title}{og_title}'
		description = f'{description}{og_description}'
		result_string = f"{title}{keywords}{description}"
		return result_string

	except requests.exceptions.RequestException as e:
		print(f"Request failed: {e}")
		try:
			nesoup = driver.get(url)
			time.sleep(1)
			pocti_soup = driver.page_source
			soup = BeautifulSoup(pocti_soup, 'lxml')
			title = soup.title.text if soup.title else ""
			keywords = soup.find('meta', {'name': 'keywords'})
			keywords = keywords.get('content') if keywords else ""
			og_title = soup.find('meta', {'property': 'og:title'})
			og_title = og_title.get('content') if og_title else ""
			og_description = soup.find('meta', {'property': 'og:description'})
			og_description = og_description.get('content') if og_description else ""
			description = soup.find('meta', {'name': 'description'})
			description = description.get('content') if description else ""
			title = f'{title}{og_title}'
			description = f'{description}{og_description}'
			result_string = f"{title}{keywords}{description}"
			return result_string

		except Exception as e:
			print(f"Selenium driver failed: {e}")
			return -1


loaded_model = joblib.load('controll/random_forest_model9.pkl')

loaded_vectorizer = joblib.load('controll/tfidf_vectorizer9.pkl')


def load_and_predict(keywords: str):
	X_new = loaded_vectorizer.transform([keywords])

	y_pred_new = loaded_model.predict(X_new)

	return y_pred_new[0]
