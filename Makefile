serve:
	python .\server.py

train:
	rm -f *.pkl*
	python -m trainer.trainer

evaluate:
	rm -f *.csv
	python .\evaluator.py config

evaluate_all:
	rm -f *.csv
	rm -rf results/Twitter/*
	rm -rf results/Facebook/*
	python .\evaluator.py all

evaluate_statistics:
	rm -f *.csv
	rm -rf results/Twitter/*
	rm -rf results/Facebook/*
	python .\evaluator.py statistical