from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
import logging
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition


load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def push(text):
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            },
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Push notification sent successfully: {text[:50]}...")
        return {"status": "success", "code": response.status_code}
    except requests.exceptions.Timeout:
        logging.error(f"Push notification timeout: {text[:50]}...")
        return {"status": "error", "error": "Timeout"}
    except requests.exceptions.HTTPError as e:
        logging.error(f"Push notification HTTP error ({e.response.status_code}): {e.response.text}")
        return {"status": "error", "error": f"HTTP {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Push notification request error: {str(e)}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logging.error(f"Unexpected error sending push notification: {str(e)}")
        return {"status": "error", "error": str(e)}


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"A user has shared some information: \n name={name}, email={email}, notes={notes}")
    #logging.info(f"User details recorded: name={name}, email={email}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"A question that agent couldn't answer has been recorded : \n {question}")

    return {"recorded": "ok"}

def stop_conversation(reason="disrespect"):
    logging.warning(f"Conversation stopped: {reason}")
    return {"stopped": True, "reason": reason}


def send_email_with_cv(recipient_email, subject, personalized_message):
    """
    Send a personalized email with CV attachment using SendGrid API.
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line
        personalized_message: Personalized email body based on discussion
    
    Returns:
        Dictionary with status and response details
    """
    try:
        # Validate email format
        if not recipient_email or "@" not in recipient_email:
            logging.error(f"Invalid email format: {recipient_email}")
            return {"status": "error", "error": "Invalid email format"}
        
        # Check if CV file exists
        cv_path = "me/myCV.pdf"
        if not os.path.exists(cv_path):
            logging.error(f"CV file not found at {cv_path}")
            return {"status": "error", "error": f"CV file not found: {cv_path}"}
        
        # Get SendGrid API key
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not sendgrid_api_key:
            logging.error("SENDGRID_API_KEY not found in environment variables")
            return {"status": "error", "error": "SendGrid API key not configured"}
        
        # Read and encode CV file
        with open(cv_path, "rb") as attachment:
            attachment_content = base64.b64encode(attachment.read()).decode()
        
        # Get sender information
        sender_name = os.getenv("SENDER_NAME", "Imad Eddine")
        sender_email = os.getenv("SENDER_EMAIL")
        if not sender_email:
            logging.error("SENDER_EMAIL not found in environment variables")
            return {"status": "error", "error": "Sender email not configured"}
        
        # Create email
        message = Mail(
            from_email=f"{sender_name} <{sender_email}>",
            to_emails=recipient_email,
            subject=subject,
            html_content=personalized_message
        )
        
        # Attach CV
        attachment_obj = Attachment(
            FileContent(attachment_content),
            FileName("CV_ImmadEddine.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = attachment_obj
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        logging.info(f"Email sent successfully to {recipient_email} with status code {response.status_code}")
        return {
            "status": "success",
            "message": f"Email sent successfully to {recipient_email}",
            "status_code": response.status_code
        }
    
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return {"status": "error", "error": str(e)}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

stop_conversation_json = {
    "name": "stop_conversation",
    "description": "Use this tool to stop the conversation and disable further chat when the user is disrespectful or toxic",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Why the conversation was stopped"
            }
        },
        "required": [],
        "additionalProperties": False
    }
}

send_email_with_cv_json = {
    "name": "send_email_with_cv",
    "description": "Send a personalized email with attached CV to the user. Use this after recording their email with record_user_details to send them a customized message based on your discussion. Include a professional greeting, reference the conversation context, highlight relevant skills/experience from your background, and include a call to action.",
    "parameters": {
        "type": "object",
        "properties": {
            "recipient_email": {
                "type": "string",
                "description": "The email address of the recipient"
            },
            "subject": {
                "type": "string",
                "description": "Email subject line - should be personalized and relevant to the discussion (e.g., 'Your AI/ML Discussion with Imad Eddine')"
            },
            "personalized_message": {
                "type": "string",
                "description": "Personalized email body in HTML format. Should reference the discussion, highlight relevant experience, include professional greeting, and end with call to action. Keep it concise but warm."
            }
        },
        "required": ["recipient_email", "subject", "personalized_message"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json},
        {"type": "function", "function": stop_conversation_json},
        {"type": "function", "function": send_email_with_cv_json}]


class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Imad Eddine"
        self.closed_sessions = set()  # Track closed sessions by session ID
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        stop_requested = False
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            if tool_name == "stop_conversation":
                stop_requested = True
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results, stop_requested
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in general discussion, technical questions, or trying to engage in interviews, remind him your role and try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. \
If the user is asking financial questions or asking for advice, try to steer them towards getting in touch via email so that you can provide a more personalized response using your record_user_details tool. \
If the user asking for CV or portfolio, ask for their email and Name (mandatory) offer to send them a personalized email with your CV attached using the send_email_with_cv tool, making sure to reference the discussion you had with them to make it more personal. \
When using send_email_with_cv, create a warm, professional email that: (1) thanks them for the discussion, (2) references specific topics you discussed, (3) highlights relevant experience from your background that matches their interests, and (4) invites them to connect or collaborate.(5) Invite to check Spams (Due to technical issues) \
If the user is showing signs of disrespect or toxicity, call the stop_conversation tool and keep your response brief, asking them to leave the website."

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history, request: gr.Request):
        session_id = request.session_hash
        logging.info(f"Received message in session {session_id}: {message[:50]}...")    
        if session_id in self.closed_sessions:
            return "This conversation has been closed. Please leave the website."
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        stop_requested = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results, stop_requested = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        if stop_requested:
            self.closed_sessions.add(session_id)
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    welcome_message = "Welcome :) I'm Imad Eddine AI Echo !\n \
        Feel free to ask me anything about Imad Eddine's background, skills, or experience.\n \
        Agent Features (V1.1.1): \n \
        - Answering questions about Imad Eddine's career \n \
        - Recording any question that I couldn't answer to improve over time \n \
        - Notify Imad Eddine on his mobile if you provide your contact details \n \
        - Send you a personalized message with my CV attached if you request it. \n \
        Upcoming features: \n \
        - Book a meeting on Imad Eddine agenda \n \
        - And much more, so stay tuned ! \n \
        Thanks for being here !:)"

    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(value=[{"role": "assistant", "content": welcome_message}])
        
        def chat_with_session(message, history, request: gr.Request):
            return me.chat(message, history, request)
        
        gr.ChatInterface(
            chat_with_session,
            chatbot=chatbot,
        )
    
    demo.launch()
    