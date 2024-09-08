import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeniAiException(Exception):
    """Base class for exceptions in the GenAi chatbot."""
    pass

class ChatBot:
    """ChatBot for interacting with the Gemini API."""
    CHATBOT_NAME = "ชื่ออะไรไม่รู้ไปก่อน นึกออกค่อยมาใส่"

    def __init__(self, api_key):
        self.genai = genai
        self.genai.configure(api_key=api_key)
        self.model = self.genai.GenerativeModel('gemini-1.5-flash')
        self.conversation = None
        self._conversation_history = []

        self.preload_conversation()

    def send_prompt(self, prompt, temperature=0.1):
        if temperature < 0 or temperature > 1:
            raise GeniAiException('Temperature must be between 0 and 1')
        if not prompt:
            raise GeniAiException('Prompt cannot be empty')

        try:
            # สร้างการตั้งค่าการสร้างเนื้อหา (generation config)
            generation_config = self._generative_config(temperature)

            # เพิ่มการตั้งค่าการบล็อก (safety settings) ในการส่งข้อความ
            response = self.conversation.send_message(
                content=prompt,
                generation_config=generation_config,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            return f'{response.text}\n'
        except Exception as e:
            raise GeniAiException(str(e))

    @property
    def history(self):
        if self.conversation:
            return [
                {'role': message.role, 'text': message.parts[0]} for message in self.conversation.history
            ]
        return []

    def clear_conversation(self):
        self.conversation = self.model.start_chat(history=[])

    def start_conversation(self):
        self.conversation = self.model.start_chat(history=self._conversation_history)

    def _generative_config(self, temperature):
        return genai.types.GenerationConfig(
            temperature=temperature
        )

    def _construct_message(self, text, role='user'):
        return {
            'role': role,
            'parts': [text]
        }

    def preload_conversation(self, conversation_history=None):
        if conversation_history is not None:
            self._conversation_history = conversation_history
        else:
            self._conversation_history = [
                self._construct_message(
                    'From now on, return the output as a JSON object that can be loaded in Python with the key as \'text\'. For example {"text": "<output goes here"}'
                ),
                self._construct_message(
                    '{"text": "Sure, I can return the output as a regular JSON object with the key as \'text\'. Here is an example: {"text": "Your Output"}}',
                    'model'
                )
            ]
