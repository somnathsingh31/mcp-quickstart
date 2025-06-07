import logging
from typing import Dict

class HelperFunctions:
    @staticmethod
    def format_tool(tool_name: str, tool_description: str, input_schema: Dict) -> str:
        """Format a tool definition for LLM usage.

        Args:
            tool_name (str): Name of the tool/function.
            tool_description (str): Description of the tool.
            input_schema (dict): JSON schema defining the input parameters.

        Returns:
            str: Formatted tool definition string.
        """
        try:
            parameters = {}

            if input_schema.get("type"):
                parameters["type"] = input_schema["type"]

            if input_schema.get("properties"):
                properties = {}
                for prop_name, prop_info in input_schema["properties"].items():
                    prop_def = {"type": prop_info.get("type", "string")}
                    if "description" in prop_info:
                        prop_def["description"] = prop_info["description"]
                    properties[prop_name] = prop_def
                parameters["properties"] = properties

            if input_schema.get("required"):
                parameters["required"] = input_schema["required"]

            return {
                "name": tool_name,
                "description": tool_description,
                "parameters": parameters
            }

        except Exception as e:
            logging.error(f"Error formatting tool schema: {e}")
            return {}