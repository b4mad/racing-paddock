.PHONY: rbr_landmarks

rbr_landmarks:
	pipenv run python manage.py load_data --landmarks-rbr $(PWD)/data/MyPacenotes/ --track-name="Kuri Bush 1"
