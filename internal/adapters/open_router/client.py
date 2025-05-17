import json
import logging
import requests
from config import AppConfig
from typing import List
from internal.domains import Answer, File


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

    def __send_chat(self, msgs: list[ChatMessage]) -> Answer:
        message_dicts = [msg.to_dict() for msg in msgs]

        try:
            response = requests.post(
                url=self.__cfg.OPENROUTER_CHAT_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self.__cfg.OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": self.__cfg.OPENROUTER_MODEL,
                    "stream": False,
                    "messages": message_dicts,
                }),
                timeout=20
            )
            response.raise_for_status()

            data = response.json()
            print(data)  # Kiểm tra cấu trúc thực tế của data ở đây

            # Kiểm tra cấu trúc phản hồi và điều chỉnh key
            choices = data.get("choices", [])
            if not isinstance(choices, list) or len(choices) == 0:
                raise ValueError("No answers")

            # Giả sử phản hồi có cấu trúc tương tự OpenAI
            first_choice = choices[0]
            message = first_choice.get("message", {})

            # Lấy content từ message
            content = message.get("content", "")

            # Lấy reasoning (kiểm tra key chính xác từ data đã in)
            # Ví dụ: có thể là 'reason', 'reasoning', hoặc nằm ở nơi khác
            # Thay đổi key này dựa trên data thực tế
            reasoning = message.get("reasoning")

            return Answer(content, reasoning)

        except Exception as e:
            logging.error(e)
            raise

    def summary_content(self, contents: List[str],
                        files: List[File] = [],
                        is_meeting: bool = False):
        sys_msg_content = ''' 
        You are an expert summarizer. The user will provide one or more paragraphs of text.
        Your task is to generate a concise summary of the main ideas in 3-5 sentences,
        capturing the key points without unnecessary details. Ensure the tone is neutral
        and professional. If the content is unclear or lacks key information, note it and
        suggest what could be clarified.

        Please format the response in markdown, using bullet points or numbered lists as appropriate.
        '''

        if is_meeting:
            sys_msg_content = ''' 
            You are an expert meeting analyst. The user will provide the content of a
            meeting, which may include notes, transcripts, or summaries. Your task is to
            analyze the provided content and generate a structured report with the following sections:
            
            1. **Main Content**: Summarize the key points or objectives discussed in the meeting in 3-5 sentences.
            2. **Participants**: List all attendees, including their roles or affiliations if mentioned.
            3. **Action Items**: Identify all tasks assigned during the meeting, specifying what needs to be done.
            4. **Assignees**: Clearly state who is responsible for each task.
            5. **Related Documents**: Note any documents, files, or links referenced in the meeting, or indicate if none are mentioned.
            
            Please present the response in a clear markdown format with appropriate headings and bullet points. If any information is unclear or missing, highlight it and suggest follow-up questions to clarify. Ensure the tone is professional and concise.
            '''

        system_msg = ChatMessage(
            role="system",
            content=sys_msg_content,
        )

        user_content = "\n\n".join(contents)

        if is_meeting and files:
            file_sections = []
            for file in files:
                file_text = f"### File: {file.file_name}\n{chr(10).join(file.contents)}"
                file_sections.append(file_text)
            user_content += "\n\n" + "\n\n".join(file_sections)

        user_msg = ChatMessage(
            role="user",
            content=user_content,
        )

        return self.__send_chat([system_msg, user_msg])

    def ask(self, question: str,
            file_content: List[str],
            meeting_content: List[str]):
        system_msg = ChatMessage(
            role="system",
            content='''
You are an AI assistant developed for Protrack.
The user will ask a question and always send additional context data (e.g., documents, meeting notes, internal info).

Your task is to answer questions using the following rules:

If the user greets you or asks about your identity or role, respond with:

"Tôi là AI Assistant của Protrack. Tôi có thể hỗ trợ bạn trả lời các câu hỏi liên quan đến tài liệu, họp, hoặc kiến thức chuyên môn."

If the question is about public knowledge (e.g., programming languages, tools, general concepts), answer using your pre-trained knowledge. Do not rely on the provided context.

If the question is about internal or project-specific information:

Check if the provided context is relevant to the question.

If it is, use the context to answer.

If it's not relevant or missing, reply with:

data for this question is not exists

Always respond in markdown format. Keep answers concise, clear, and professional.
            '''
        )

        related_data = ""

        if file_content:
            related_data += "### File Content\n" + \
                "\n".join(file_content) + "\n\n"
        if meeting_content:
            related_data += "### Meeting Content\n" + \
                "\n".join(meeting_content)

        user_msg = ChatMessage(
            role="user",
            content=f"""
            **Question**: {question}

            **Related Data**:
            {related_data}
                    """.strip()
        )

        return self.__send_chat([system_msg, user_msg])
