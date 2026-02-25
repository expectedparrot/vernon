.PHONY: help run clean view-results install-deps

help:
	@echo "Hot Dog Feedback Study - Makefile Commands"
	@echo "==========================================="
	@echo "make run           - Run the survey and generate results"
	@echo "make clean         - Remove generated data files"
	@echo "make view-results  - Display results summary (after running)"
	@echo "make install-deps  - Install required Python packages"

install-deps:
	pip install edsl -U

run:
	python create_results.py

clean:
	rm -rf data/*.json.gz
	@echo "Cleaned up results files"

view-results:
	python -c "from edsl import Results; r = Results.load('data/results.json.gz'); print(r.select('overall_satisfaction', 'best_part', 'improvement').to_pandas())"
