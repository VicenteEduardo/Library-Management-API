.PHONY: run seed test lint

run:
	uvicorn app.main:app --reload

seed:
	python seed.py

test:
	pytest -q
