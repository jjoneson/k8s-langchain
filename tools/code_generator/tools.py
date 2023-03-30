from typing import List
from pydantic import BaseModel
from langchain.tools.base import BaseTool
from design_patterns.design_pattern import DesignPattern

from design_patterns.kubernetes.generic_app_istio.pattern import GenericAppWithIstio


class CodeGeneratorModel(BaseModel):
    design_patterns = dict[str, DesignPattern]

    @classmethod
    def from_design_patterns(cls, design_patterns: List[DesignPattern]):
        """Create a CodeGeneratorModel from a list of design patterns."""
        return cls(design_patterns={design_pattern.name: design_pattern for design_pattern in design_patterns})
    
    def get_design_pattern(self, name: str) -> DesignPattern:
        """Get a design pattern by name."""
        return self.design_patterns[name]
    
    def get_detailed_design_pattern_list(self) -> List[str]:
        """Get a list of design patterns with detailed information."""
        return [f"Design Pattern: {design_pattern.name}:\n{design_pattern.use_case}\n---" for design_pattern in self.design_patterns.values()]
    
    def get_design_pattern_template_names(self, name: str) -> List[str]:
        """Get a list of design pattern template names."""
        return self.get_design_pattern(name).get_template_names()

    def get_design_pattern_template(self, name: str, template_name: str) -> str:
        """Get a design pattern template by name."""
        return self.get_design_pattern(name).get_template(template_name)

class DesignPatternListTool(BaseTool):
    """Tool for listing design patterns."""
    name = "design_pattern_list"
    description = """Use this tool to get a list of available design patterns.
    Returns a list of design pattern names and uase cases.
    """
    model = CodeGeneratorModel


    def _run(self, tool_input: str) -> str:
        """Get a list of design patterns."""
        return self.model.get_detailed_design_pattern_list()

    async def _arun(self, tool_input: str) -> str:
        """Get a list of design patterns asynchronously."""
        return self._run(tool_input)
    
class DesignPatternListTemplatesTool(BaseTool):
    """Tool for listing design pattern templates."""
    name = "design_pattern_list_templates"
    description = """Use this tool to get a list of design pattern templates.
    Input is a design pattern name.
    Returns a list of design pattern templates
    """
    model = CodeGeneratorModel


    def _run(self, tool_input: str) -> str:
        """Get a list of design patterns."""
        return ",".join(self.model.get_design_pattern_template_names(tool_input))

    async def _arun(self, tool_input: str) -> str:
        """Get a list of design patterns asynchronously."""
        return self._run(tool_input)
    
class DesignPatternGetTemplateTool(BaseTool):
    """Tool for getting a design pattern template."""
    name = "design_pattern_get_template"
    description = """Use this tool to get a specific design pattern template.
    Input is a comma separated list of design pattern name and template name.
    Returns a design pattern template
    """
    model = CodeGeneratorModel


    def _run(self, tool_input: str) -> str:
        """Get a list of design patterns."""
        design_pattern_name, template_name = tool_input.split(",")
        # trim whitespace
        design_pattern_name = design_pattern_name.strip()
        template_name = template_name.strip()
        return self.model.get_design_pattern_template(design_pattern_name, template_name)

    async def _arun(self, tool_input: str) -> str:
        """Get a list of design patterns asynchronously."""
        return self._run(tool_input)
