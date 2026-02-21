"""
FlowService: Survey flow visualization service for EDSL.

Creates flowchart visualizations of Survey logic showing question flow,
skip logic, and parameter dependencies. Returns FileStore objects.

Requires: pydot, graphviz (system package)
"""

from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from edsl.services import ExternalService, method_type, MethodType

if TYPE_CHECKING:
    from edsl.surveys import Survey
    from edsl.scenarios import Scenario, FileStore
    from edsl.agents import Agent


class FlowService(ExternalService):
    """
    Survey flow visualization service.

    Creates flowchart visualizations of Survey logic showing questions,
    skip logic rules, and parameter dependencies. Returns FileStore
    containing PNG images.

    Example:
        survey = Survey.example()
        fs = survey.flow.show()  # Returns FileStore with PNG
        fs.view()  # Display the image

        # Save to file
        fs = survey.flow.show(filename="my_survey.png")
    """

    service_name = "flow"
    extends = ["Survey"]

    def _get_pydot(self):
        """Get the pydot module."""
        try:
            import pydot
            return pydot
        except ImportError:
            raise ImportError(
                "The 'pydot' package is required for flow visualization.\n"
                "Install it with: pip install pydot\n"
                "You also need graphviz installed:\n"
                "  Ubuntu: sudo apt-get install graphviz\n"
                "  Mac: brew install graphviz\n"
                "  Windows: choco install graphviz"
            )

    @method_type(MethodType.INSTANCE)
    def show(
        self,
        instance: "Survey",
        filename: Optional[str] = None,
        scenario: Optional[Dict[str, Any]] = None,
        agent: Optional[Dict[str, Any]] = None,
    ) -> "FileStore":
        """
        Create a flow diagram visualization of the survey.

        Args:
            instance: The Survey to visualize (may be dict if serialized)
            filename: Optional path to save the PNG file
            scenario: Optional Scenario data for context
            agent: Optional Agent data for context

        Returns:
            FileStore: A FileStore containing the PNG image
        """
        from edsl.scenarios import FileStore
        from edsl.surveys import Survey

        # Reconstruct Survey from dict if needed (instance comes serialized from API)
        if isinstance(instance, dict):
            survey = Survey.from_dict(instance)
        else:
            survey = instance

        # Generate the PNG data
        png_data = self._create_flow_diagram(survey, scenario, agent)

        # Save to file if requested
        if filename:
            with open(filename, "wb") as f:
                f.write(png_data)

        # Create and return FileStore
        return FileStore(
            path=filename or "survey_flow.png",
            base64_string=base64.b64encode(png_data).decode("utf-8"),
            suffix="png",
            mime_type="image/png",
            binary=True,
        )

    def _create_flow_diagram(
        self,
        survey: "Survey",
        scenario_data: Optional[Dict[str, Any]] = None,
        agent_data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Create a flow diagram for the survey.

        Args:
            survey: The Survey object to visualize
            scenario_data: Optional scenario dict for context
            agent_data: Optional agent dict for context

        Returns:
            bytes: PNG image data
        """
        pydot = self._get_pydot()
        from edsl.surveys.navigation_markers import RulePriority, EndOfSurvey

        scenario = scenario_data or {}

        FONT_SIZE = "10"
        graph = pydot.Dot(graph_type="digraph", fontsize=FONT_SIZE)

        # First collect all unique parameters and different types of references
        params_and_refs: Set[str] = set()
        param_to_questions: Dict[str, List[int]] = {}
        reference_types: Dict[str, Set[Tuple[str, int]]] = {}
        reference_colors = {
            "answer": "purple",
            "question_text": "red",
            "question_options": "orange",
            "comment": "blue",
            "default": "grey",
        }

        # Build a mapping of questions to their groups
        question_to_group: Dict[int, str] = {}
        if survey.question_groups:
            for group_name, (start_idx, end_idx) in survey.question_groups.items():
                for q_idx in range(start_idx, end_idx + 1):
                    if q_idx < len(survey.questions):
                        question_to_group[q_idx] = group_name

        # Create question groups as subgraph clusters first
        group_colors = [
            "lightblue",
            "lightgreen",
            "lightyellow",
            "lightcyan",
            "lightpink",
            "lavender",
            "mistyrose",
            "honeydew",
        ]

        group_clusters = {}
        if survey.question_groups:
            for i, (group_name, (start_idx, end_idx)) in enumerate(
                survey.question_groups.items()
            ):
                color = group_colors[i % len(group_colors)]

                # Create a subgraph cluster for the group
                cluster = pydot.Cluster(
                    f"cluster_{group_name}",
                    label=f"Group: {group_name}",
                    style="filled",
                    fillcolor=color,
                    color="black",
                    fontsize=str(int(FONT_SIZE) + 2),
                    fontname="Arial Bold",
                )
                group_clusters[group_name] = cluster

        # First pass: collect parameters and their question associations
        for index, question in enumerate(survey.questions):
            question_node = pydot.Node(
                f"Q{index}",
                label=f"{question.question_name}",
                shape="ellipse",
                fontsize=FONT_SIZE,
            )

            # Add node to appropriate cluster or main graph
            if index in question_to_group:
                group_name = question_to_group[index]
                group_clusters[group_name].add_node(question_node)
            else:
                graph.add_node(question_node)

            if hasattr(question, "detailed_parameters"):
                for param in question.detailed_parameters:
                    if "agent." in param:
                        # Handle agent trait references
                        params_and_refs.add(param)
                        if param not in param_to_questions:
                            param_to_questions[param] = []
                        param_to_questions[param].append(index)
                    if "scenario." in param:
                        params_and_refs.add(param)
                        if param not in param_to_questions:
                            param_to_questions[param] = []
                        param_to_questions[param].append(index)
                    elif "." in param:
                        source_q, ref_type = param.split(".", 1)
                        if ref_type not in reference_types:
                            reference_types[ref_type] = set()
                        reference_types[ref_type].add((source_q, index))
                    else:
                        params_and_refs.add(param)
                        if param not in param_to_questions:
                            param_to_questions[param] = []
                        param_to_questions[param].append(index)

        # Add group clusters to the graph
        for cluster in group_clusters.values():
            graph.add_subgraph(cluster)

        # Add edges for all reference types
        for ref_type, references in reference_types.items():
            color = reference_colors.get(ref_type, reference_colors["default"])
            for source_q_name, target_q_index in references:
                # Find the source question index by name
                try:
                    source_q_index = next(
                        i
                        for i, q in enumerate(survey.questions)
                        if q.question_name == source_q_name
                    )
                except StopIteration:
                    continue

                ref_edge = pydot.Edge(
                    f"Q{source_q_index}",
                    f"Q{target_q_index}",
                    style="dashed",
                    color=color,
                    label=f".{ref_type}",
                    fontcolor=color,
                    fontname="Courier",
                    fontsize=FONT_SIZE,
                )
                graph.add_edge(ref_edge)

        # Create parameter nodes and connect them to questions
        for param in params_and_refs:
            param_node_name = f"param_{param}"
            node_attrs = {
                "label": f"{{{{ {param} }}}}",
                "shape": "box",
                "style": "filled",
                "fillcolor": "lightgrey",
                "fontsize": FONT_SIZE,
            }

            # Special handling for agent traits
            if param.startswith("agent."):
                node_attrs.update(
                    {
                        "fillcolor": "lightpink",
                        "label": f"Agent Trait\n{{{{ {param} }}}}",
                    }
                )
            # Check if parameter exists in scenario
            elif scenario and param.startswith("scenario."):
                node_attrs.update(
                    {"fillcolor": "lightgreen", "label": f"Scenario\n{{{{ {param} }}}}"}
                )

            param_node = pydot.Node(param_node_name, **node_attrs)
            graph.add_node(param_node)

            # Connect this parameter to all questions that use it
            for q_index in param_to_questions.get(param, []):
                param_edge = pydot.Edge(
                    param_node_name,
                    f"Q{q_index}",
                    style="dotted",
                    arrowsize="0.5",
                    fontsize=FONT_SIZE,
                )
                graph.add_edge(param_edge)

        # Add an "EndOfSurvey" node
        graph.add_node(
            pydot.Node(
                "EndOfSurvey",
                label="End of Survey",
                shape="rectangle",
                fontsize=FONT_SIZE,
                style="filled",
                fillcolor="lightgrey",
            )
        )

        # Add edges for normal flow through the survey
        num_questions = len(survey.questions)
        for index in range(num_questions - 1):
            graph.add_edge(pydot.Edge(f"Q{index}", f"Q{index+1}", fontsize=FONT_SIZE))

        if num_questions > 0:
            graph.add_edge(
                pydot.Edge(f"Q{num_questions-1}", "EndOfSurvey", fontsize=FONT_SIZE)
            )

        # Filter to relevant rules (priority > DEFAULT)
        relevant_rules = [
            rule
            for rule in survey.rule_collection
            if rule.priority > RulePriority.DEFAULT.value
        ]

        # Edge colors to cycle through
        colors = [
            "blue",
            "red",
            "orange",
            "purple",
            "brown",
            "cyan",
            "darkgreen",
        ]
        rule_colors = {
            rule: colors[i % len(colors)] for i, rule in enumerate(relevant_rules)
        }

        for rule in relevant_rules:
            color = rule_colors[rule]
            edge_label = f"if {rule.expression}"
            source_node = f"Q{rule.current_q}"
            target_node = (
                f"Q{rule.next_q}"
                if rule.next_q != EndOfSurvey and rule.next_q < num_questions
                else "EndOfSurvey"
            )
            if rule.before_rule:
                edge = pydot.Edge(
                    source_node,
                    target_node,
                    label=edge_label,
                    color=color,
                    fontcolor=color,
                    tailport="n",
                    headport="n",
                    fontname="Courier",
                    fontsize=FONT_SIZE,
                )
            else:
                edge = pydot.Edge(
                    source_node,
                    target_node,
                    label=edge_label,
                    color=color,
                    fontcolor=color,
                    fontname="Courier",
                    fontsize=FONT_SIZE,
                )

            graph.add_edge(edge)

        # Generate PNG bytes
        try:
            png_data = graph.create_png()
        except FileNotFoundError:
            raise RuntimeError(
                "Graphviz not found. Please install it:\n"
                "  Ubuntu: sudo apt-get install graphviz\n"
                "  Mac: brew install graphviz\n"
                "  Windows: choco install graphviz"
            )

        return png_data
