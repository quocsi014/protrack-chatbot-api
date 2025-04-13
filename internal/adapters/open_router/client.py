import json
import requests
from config import AppConfig
from typing import List


class ChatMessage:
    def __init__(self, role: str, content: str):
        self.__role = role
        self.__content = content

    def to_dict(self):
        return {
            "role": self.__role,
            "content": self.__content
        }


class OpenRouterClient:
    def __init__(self, cfg: AppConfig):
        self.__cfg = cfg

    def __send_chat(self, msgs: list[ChatMessage]):
        message_dicts = [msg.to_dict() for msg in msgs]

        response = requests.post(
            url=self.__cfg.OPENROUTER_CHAT_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self.__cfg.OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": self.__cfg.OPENROUTER_MODEL,
                "messages": message_dicts,
            })
        )
        return response

    def summary_content(self, contents: List[str], is_meeting: bool = False):
        sys_msg_content = '''
        You are an expert summarizer. The user will provide one or more paragraphs of text.
        Your task is to generate a concise summary of the main ideas in 3-5 sentences,
        capturing the key points without unnecessary details. Ensure the tone is neutral
        and professional. If the content is unclear or lacks key information, note it and
        suggest what could be clarified.
        '''

        if is_meeting:
            sys_msg_content = '''
            You are an expert meeting analyst. The user will provide the content of a
            meeting, which may include notes, transcripts, or summaries. Your task is to
            analyze the provided content and generate a structured report with the
            following sections:
            1. **Main Content**: Summarize the key points or objectives discussed in the
               meeting in 3-5 sentences.
            2. **Participants**: List all attendees, including their roles or affiliations
               if mentioned.
            3. **Action Items**: Identify all tasks assigned during the meeting,
               specifying what needs to be done.
            4. **Assignees**: Clearly state who is responsible for each task.
            5. **Related Documents**: Note any documents, files, or links referenced in
               the meeting, or indicate if none are mentioned.

            Please present the response in a clear, HTML format (e.g., bullet points
            or numbered sections), in vietnamese. If any information is unclear or missing, highlight it
            and suggest follow-up questions to clarify. Ensure the tone is professional
            and concise.
            '''

        system_msg = ChatMessage(
            role="system",
            content=sys_msg_content,
        )

        user_msg = ChatMessage(
            role="user",
            content="\n\n".join(contents),
        )

        res = self.__send_chat([system_msg, user_msg])
        try:
            res_json = res.json()  # parse response to JSON
            # pretty print
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
        except Exception as e:
            print("Error parsing response JSON:", e)
            print(res.text)
        return json.dumps(res_json, indent=2, ensure_ascii=False)

    def ask(self, question: str, content: str):
        system_msg = ChatMessage(
            role="system",
            content='''
                The user will provide the question and related data,
                and rely on that data to answer the question.
            ''',
        )

        user_msg = ChatMessage(
            role="user",
            content=f'''
            question: {question}\n
            relative data:{content}
                ''',
        )

        return self.__send_chat([system_msg, user_msg])
