from groq import AsyncGroq
import os
import re
import json
import logging
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLMInterface:
    def __init__(self):
        self.client = AsyncGroq(api_key=GROQ_API_KEY)
        self.history = []

    async def _parse_llm_response(self, llm_response: str, tag: str) -> str | dict | None:
        """Parse LLM response enclosed in specific XML-like tags.

        Args:
            llm_response (str): The complete LLM output.
            tag (str): Tag to extract ('tool_call' or 'user_message').

        Returns:
            dict | str | None: Parsed JSON if tag is 'tool_call', plain text if 'user_message', or None if parsing fails.
        """

        try:
            pattern = fr"<{tag}>(.*?)</{tag}>"
            match = re.search(pattern, llm_response, re.DOTALL)

            if not match:
                return None

            parsed_data = match.group(1).strip()
            if tag == "tool_call":
                try:
                    return json.loads(parsed_data)
                except json.JSONDecodeError as json_err:
                    logging.error(f"JSON decode error in tool_call: {json_err}")
                    return None

            if tag == "user_message":
                return parsed_data
        
        except Exception as e:
            logging.error(f"Error occurred during LLM response parsing: {e}")
            return None
    
    async def get_llm_response(self, tools_description: str) -> str:
        """Get LLM response from LLM using tool-aware prompt.

        Args:
            query (str): User query string.
            tools_description (str): Description of available tools.
        """
        try:
            system_message = (
                "You are a helpful assistant with access to the following tools:\n"
                f"{tools_description}\n\n"
                "## Decision rules:\n"
                "1. If the user's request can be answered without using any tool, respond **only** using the <user_message>...</user_message> tags.\n"
                "2. If the request requires one or more tools, respond **only** using a single <tool_call>...</tool_call> block (see format below). "
                "In this case, do **not** include a <user_message> block.\n"
                "3. A response must contain **either** a <tool_call> block **or** a <user_message> block—**never both**.\n\n"
                "## Tool call format:\n"
                "<tool_call>\n"
                "[\n"
                "  {\n"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '      "argument-name": "value"\n'
                "    }\n"
                "  },\n"
                "  ... (add more tool calls if needed)\n"
                "]\n"
                "</tool_call>\n\n"
                "## User message format:\n"
                "<user_message>\n"
                "Your natural language reply to the user goes here.\n"
                "</user_message>\n\n"
                "## Constraints:\n"
                "- Do **not** include any explanation or text outside of <tool_call> or <user_message> tags.\n"
                "- Use **only** the tools explicitly listed above.\n\n"
                "- Always include both the opening and closing tags for <user_message> or <tool_call>. Responses with missing tags are invalid.\n"
                "**IMPORTANT** - After receiving a tool's response, provide a final answer to the user in a friendly, natural language format using <user_message> tags. Do not include unnecessary details—respond only with information relevant to the user's original question."
            )

            messages = [{"role": "system", "content":system_message}]
            messages.extend(self.history)

            response = await self.client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                temperature=0.2,
                max_completion_tokens=1024,
                top_p=0.95,
                stream=False,
                stop=None,
            )
            self.history.append({"role": "assistant", "content": response.choices[0].message.content})
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error occurred during LLM response: {e}")
            return "Error"

    async def process_llm_response(self, llm_response: str) -> dict:
        """
        Process LLM response and extract structured data.

        Args:
            llm_response (str): Raw response string from LLM.

        Returns:
            dict: {
                "tool_call": bool,
                "tool_call_data" or "message_to_user": str or list or dict
            }
            Returns empty dict if nothing matched or on error.
        """
        try:
            result = {}

            if "<tool_call>" in llm_response:
                llm_parsed_data = await self._parse_llm_response(llm_response, "tool_call")
                if llm_parsed_data:
                    result["tool_call"] = True
                    result["tool_call_data"] = llm_parsed_data
                    return result

            if "<user_message>" in llm_response:
                llm_parsed_data = await self._parse_llm_response(llm_response, "user_message")
                if llm_parsed_data:
                    result["tool_call"] = False
                    result["message_to_user"] = llm_parsed_data
                    return result

            # Return empty result if no tags matched
            return result
        except Exception as e:
            logging.error(f"Error occurred during LLM response processing: {e}")
            return {}