from openai import OpenAI

class Llm():
    def __init__(self, func, func_call, model, api_key):
        self.client = OpenAI(api_key=api_key)
        self.func = func
        self.func_call = func_call
        self.model = model
        self.conversation_history = []
        self.iter_num = 0

    # GPT function call api
    def chat_with_gpt_func(self, prompt, conversation_history=None):
        if conversation_history is None:
            conversation_history = []

        conversation_history.append({"role": "user", "content": prompt})

        functions = self.func

        response = self.client.chat.completions.create(
            model=self.model,
            messages=conversation_history,
            functions=functions,
            function_call=self.func_call,
            temperature=0,
        )

        message = response.choices[0].message
        conversation_history.append(message)

        return message.function_call.arguments, conversation_history
    
    def get_prompt_from_file(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            prompt = file.read()
        return prompt

    # Call the gpt api
    def call(self, prompt):
        response, conversation_history = self.chat_with_gpt_func(prompt, self.conversation_history)
        self.iter_num += 1
        return response, conversation_history