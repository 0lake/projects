.PHONY: install test train predict clean

install:
	pip install -e ".[dev]"

test:
	pytest

train:
	python -m churn.train

# make predict INPUT=new_customers.xlsx
predict:
	python -m churn.predict --input $(INPUT)

clean:
	rm -rf models .pytest_cache build *.egg-info src/*.egg-info
