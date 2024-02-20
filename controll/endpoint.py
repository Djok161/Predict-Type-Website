from fastapi import APIRouter, Depends, HTTPException
from controll.textproc import get_page_info, preprocess_text, load_and_predict
from sqlalchemy.orm import Session
from validators import url as validate_url
from models.core import Website
from models.database import get_db

type_router = APIRouter()


@type_router.get('/type')
def type(url: str, session: Session = Depends(get_db)):
	if not validate_url(url):
		raise HTTPException(status_code=400, detail="Invalid URL")

	existing_website = session.query(Website).filter(Website.url == url).first()
	if existing_website:
		raise HTTPException(status_code=400, detail="Website already exists in the database")

	connect_to_site = get_page_info(url)
	if connect_to_site == -1:
		website = Website(url=url, class_website='99.99.99 - Нераспознанные Сайты')
		session.add(website)
		session.commit()
		raise HTTPException(status_code=500, detail="Error connecting to the website")

	preprocess_tags = preprocess_text(connect_to_site)

	if len(preprocess_tags.split()) < 4:
		website = Website(url=url, class_website='99.99.99 - Нераспознанные Сайты')
		session.add(website)
		session.commit()
		raise HTTPException(status_code=204, detail="Too few indices")

	site_predict = load_and_predict(preprocess_tags)

	website = Website(url=url, class_website=site_predict)
	session.add(website)
	session.commit()
	return {"type":site_predict}
