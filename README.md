---
title: Imad_Eddine_BOUIHI_AI_Echo
app_file: app.py
sdk: gradio
sdk_version: 6.5.1
---

# Echo Me Pro

An AI-powered personal assistant chat interface that answers questions about your career, background, skills, and experience. The application uses OpenAI's GPT-4 to engage professionally with potential clients and employers, while automatically recording contact information and unknown questions via push notifications.

## Features

- **AI-Powered Chat**: Uses OpenAI GPT-4o-mini to respond in your voice
- **Context-Aware**: Leverages your LinkedIn profile and personal summary for accurate responses
- **Lead Capture**: Automatically records user contact details when they express interest
- **Question Tracking**: Logs questions that couldn't be answered for future improvement
- **Push Notifications**: Sends real-time alerts via Pushover for user interactions
- **Error Handling**: Comprehensive logging and error handling for HTTP requests
- **Web Interface**: Clean Gradio-based chat interface

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Pushover account (for notifications)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd echo-me-pro
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PUSHOVER_TOKEN=your_pushover_app_token
   PUSHOVER_USER=your_pushover_user_key
   ```

3. **Add required personal files**:
   
   **IMPORTANT**: Before running the app, you must create these files in the `me/` directory:
   
   - **`me/summary.txt`**: A text file containing your personal summary, background, and key information
   - **`me/linkedin.pdf`**: Export your LinkedIn profile as PDF and place it here
   
   Create the directory if it doesn't exist:
   ```bash
   mkdir me
   ```
   
   Then add your files:
   - Save your personal summary as `me/summary.txt`
   - Export your LinkedIn profile to PDF and save as `me/linkedin.pdf`

4. **Install dependencies**:
   Using uv (recommended):
   ```bash
   uv pip install -r requirements.txt
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Using uv (recommended)
```bash
uv run app.py
```

### Using Python directly
```bash
python app.py
```

The application will start a local web server (typically at `http://localhost:7860`) and open in your default browser.

## Project Structure

```
echo-me-pro/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in repo)
├── me/
│   ├── summary.txt    # Personal summary
│   └── linkedin.pdf   # LinkedIn profile PDF
└── README.md          # This file
```

## How It Works

1. **Initialization**: Loads personal data (summary and LinkedIn profile)
2. **Chat Interface**: User interacts through Gradio chat interface
3. **AI Processing**: Messages are sent to OpenAI with context and tools
4. **Tool Calling**: AI can invoke tools to:
   - Record user contact details
   - Log unknown questions
5. **Notifications**: Push notifications sent for important interactions
6. **Logging**: All operations logged with timestamps and error details

## Deployment

The app can be deployed to Gradio Spaces:

```bash
gradio deploy
```

## Dependencies

- `gradio` - Web interface
- `openai` - OpenAI API client
- `openai-agents` - Agent framework
- `pypdf` - PDF parsing for LinkedIn profile
- `requests` - HTTP requests for push notifications
- `python-dotenv` - Environment variable management

## Configuration

Customize the experience by modifying:
- `me/summary.txt` - Personal summary text
- `me/linkedin.pdf` - LinkedIn profile PDF
- System prompt in `Me.system_prompt()` method
- OpenAI model in `me.chat()` method (default: `gpt-4o-mini`)

## Troubleshooting

**Missing files error**: If you get `FileNotFoundError` when running the app, ensure you have:
- Created the `me/` directory
- Added `me/summary.txt` with your personal summary
- Added `me/linkedin.pdf` with your LinkedIn profile export

**Gradio version error**: If you get `TypeError: ChatInterface.__init__() got an unexpected keyword argument 'type'`, ensure you're using Gradio 5.0+ or remove the `type` parameter.

**Missing environment variables**: Ensure your `.env` file contains all required API keys.

**Push notification failures**: Check Pushover credentials and review logs for specific HTTP errors.

## License

[Add your license here]

## Author

Imad Eddine BOUIHI
