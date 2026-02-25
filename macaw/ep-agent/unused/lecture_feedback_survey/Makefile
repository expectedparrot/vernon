.PHONY: all run clean show-survey

all: run

# Run the complete study
run:
	@echo "Running lecture feedback survey..."
	python create_results.py

# Display the survey structure
show-survey:
	@echo "Displaying survey questions..."
	@python -c "from study_survey import survey; survey.show()"

# Clean up generated results
clean:
	@echo "Cleaning up results..."
	rm -f lecture_feedback_results.json
	rm -rf __pycache__
	find . -name "*.pyc" -delete

# Show help
help:
	@echo "Available commands:"
	@echo "  make run          - Run the survey and generate results"
	@echo "  make show-survey  - Display survey structure"
	@echo "  make clean        - Remove generated files"
	@echo "  make help         - Show this help message"
