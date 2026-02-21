"""
EDSL Flow Plugin - Survey flow visualization service for EDSL.

This plugin provides flow visualization for EDSL Surveys, creating
flowchart visualizations showing question flow, skip logic, and
parameter dependencies.

The service is automatically discovered when this package is installed.

Usage:
    from edsl.surveys import Survey

    survey = Survey.example()
    fs = survey.flow.show()  # Returns FileStore with PNG
    fs.view()  # Display the image
"""

from edsl_flow.service import FlowService

__version__ = "0.1.0"
__all__ = ["FlowService"]
