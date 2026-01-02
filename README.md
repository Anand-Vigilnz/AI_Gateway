# AI Gateway – Secure Chat Application

This repository contains two Streamlit-based chat applications:

1. **`main.py`** – Full-featured chat application with Rproxy security scanning
2. **`app.py`** – Simple chatbot with UI-configurable settings

---

## `app.py` – Simple ChatBot

**Purpose:**  
Simple Streamlit-based chatbot that sends messages directly to OpenAI API (or Rproxy if configured). Features UI-configurable API URL, API key, and model name for easy testing and switching between endpoints.

---

## `app.py` Features

- **💬 Simple Chat Interface** - Clean, conversational UI for chatting with AI
- **⚙️ UI-Configurable Settings** - Change API URL, API Key, and Model Name directly in the sidebar
- **🔄 Environment Variable Fallback** - Values initialized from `.env` file, editable in UI
- **📝 Full Conversation History** - All messages displayed in UI for context
- **🎯 Single Message Mode** - Sends only current message to avoid context-based blocking
- **🛡️ Rproxy Support** - Works with Rproxy gateway if API URL points to it
- **⚠️ Threat Detection** - Displays security threats when messages are blocked
- **🗑️ Clear History** - Button to clear chat history
- **📊 Connection Info** - Real-time display of current API URL and model

---

## `main.py` Features

- **💬 Simple Chat Interface** - Clean, conversational UI for chatting with AI
- **🛡️ Security Scanning** - All messages go through Rproxy for threat detection
- **🤖 Direct OpenAI Integration** - Safe messages sent directly to OpenAI (no database dependency)
- **📊 Security Status** - Visual indicators for allowed/blocked messages
- **⚠️ Threat Details** - Expandable threat information for blocked messages
- **⚙️ .env Configuration** - Easy configuration via environment variables
- **🔄 Chat History** - Persistent conversation history during session
- **📈 Performance Metrics** - Latency and status code display for each message

---

## Architecture

### `app.py` Flow Diagram

```
User Input → UI Configuration → Send Current Message Only → API (OpenAI/Rproxy) → Response to UI
                                                                    ↓
                                                           If Blocked → Show Threats
```

### How `app.py` Works

1. **User sends message** → Added to full conversation history (for UI display)
2. **Extract current message only** → Only the current user message is sent to API (not conversation history)
3. **Send to API** → Message sent to configured API URL (OpenAI or Rproxy)
   - **If Rproxy blocks** → Detects `action: "blocked"` in response, displays threat details
   - **If allowed** → Processes as OpenAI response, displays content
4. **Display response** → Response added to conversation history and shown in UI

**Key Design Decision:** Only the current message is sent to avoid context-based blocking by Rproxy, while full conversation history is maintained in the UI for user reference.

### `main.py` Flow Diagram

```
User Input → Rproxy (Security Scan) → If Safe → OpenAI LLM → Response to UI
                              ↓
                         If Blocked → Show Threats
```

### How `main.py` Works

1. **User sends message** → Added to chat history
2. **Security Scan** (if Rproxy configured) → Message sent to Rproxy for threat detection
   - **If Blocked** → Display blocked message with threat details
   - **If Allowed** → Proceed to OpenAI
   - **If Rproxy not configured** → Skip scan, proceed directly to OpenAI
3. **Send to OpenAI LLM** → Message sent to OpenAI API
4. **LLM Response** → Display response in chat interface

---

## Project Structure

- `app.py` – Simple chatbot with UI-configurable settings
- `main.py` – Full-featured chat application with Rproxy security scanning
- `config.py` – Configuration loader for .env file
- `.env.example` – Template for environment variables
- `requirements.txt` – Python dependencies
- `legacy/` – Previous version files (database-dependent)

---

## Installation

1. Create and activate a virtual environment (recommended):

```bash
cd "AI Gateway"
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# - API_URL: Your Rproxy gateway URL/Openai URL
# - RPROXY_AUTH_HEADER: Your Rproxy API key/ OPENAI api key
# - DEFAULT_MODEL: OpenAI model(e.g gpt-4o-mini)
```

4. Run the application:

```bash
# Run simple chatbot (app.py)
streamlit run app.py

```

---

## Configuration

### `app.py` Configuration

#### Environment Variables (.env file) - Optional

Values are initialized from `.env` but can be changed directly in the UI sidebar:

1. **OPENAI_API_KEY** (optional)
   - Your OpenAI API key for LLM requests
   - Get your API key from: https://platform.openai.com/api-keys
   - Format: `sk-...`
   - Can be set in `.env` or entered in UI sidebar

2. **OPENAI_API_URL** (optional)
   - The OpenAI API endpoint URL
   - Default: `https://api.openai.com/v1/chat/completions`
   - Can point to OpenAI directly or Rproxy gateway
   - Can be set in `.env` or changed in UI sidebar

3. **DEFAULT_MODEL** (optional)
   - Default OpenAI model to use
   - Examples: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
   - Default: `gpt-4o-mini`
   - Can be set in `.env` or changed in UI sidebar

#### UI Configuration

All settings can be configured directly in the sidebar:
- **API URL** – Editable text input
- **API Key** – Password-protected input
- **Model Name** – Editable text input

Changes take effect immediately for new messages without restarting the app.

### `main.py` Configuration

#### Environment Variables (.env file)

#### Required Variables

1. **OPENAI_API_KEY** (required)
   - Your OpenAI API key for LLM requests
   - Get your API key from: https://platform.openai.com/api-keys
   - Format: `sk-...`

#### Optional Variables

2. **RPROXY_URL** (optional)
   - The URL of your Prompt Security Gateway (Rproxy)
   - Example: `https://devaigw.vigilnz.com/`
   - Default: `https://devaigw.vigilnz.com/`
   - If not set, security scanning will be skipped and messages sent directly to OpenAI

3. **RPROXY_AUTH_HEADER** (optional)
   - API key for Rproxy authentication
   - Format: `vpsk_live_{entityId}{random}` or `Bearer vpsk_live_...`
   - Entity ID will be automatically extracted from the API key
   - If not set, security scanning will be skipped

4. **DEFAULT_MODEL** (optional)
   - Default OpenAI model to use if not specified in UI
   - Examples: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
   - Default: `gpt-4o-mini`

### Rproxy Configuration

**Note:** Rproxy configuration is optional. If `RPROXY_URL` or `RPROXY_AUTH_HEADER` is not set:
- The chatbot will work without security scanning
- Messages will be sent directly to OpenAI
- A warning will be displayed indicating that Rproxy is not configured
- This is useful for development or when security scanning is not needed

---

## Usage

### Starting `app.py`

1. (Optional) Configure `.env` file with default values
2. Run: `streamlit run app.py`
3. Open your browser to the URL shown in the terminal (usually `http://localhost:8501`)

### Using `app.py` Chat Interface

1. **Configure Settings** (Sidebar):
   - Enter or modify **API URL** (e.g., `https://api.openai.com/v1/chat/completions` or Rproxy URL)
   - Enter or modify **API Key** (your OpenAI API key)
   - Enter or modify **Model Name** (e.g., `gpt-4o-mini`)

2. **Send Messages**:
   - Type your message in the chat input
   - Only the current message is sent to API (not conversation history)
   - If using Rproxy and message is blocked, threat details are shown
   - If allowed, response is displayed

3. **View Details**:
   - Full conversation history is displayed in UI
   - Click "Security threats detected" to see threat details for blocked messages
   - Check connection info in sidebar for current settings

4. **Clear History**:
   - Click "🗑️ Clear Chat History" button in sidebar to reset conversation

### Starting `main.py`

1. Ensure your `.env` file is configured with all required variables
2. Run: `streamlit run main.py`
3. Open your browser to the URL shown in the terminal (usually `http://localhost:8501`)

### Using `main.py` Chat Interface

1. **Configure Settings** (Sidebar):
   - Set Rproxy URL (for security scanning)
   - Set Rproxy API Key
   - Set OpenAI Model Name

2. **Send Messages**:
   - Type your message in the chat input
   - Message is automatically scanned by Rproxy
   - If safe, sent to OpenAI and response displayed
   - If blocked, threat details are shown

3. **View Details**:
   - Click "Raw Request/Response Payload" to see full API requests/responses
   - View threat details for blocked messages
   - Check latency and status for each message

---

## Security Features

### `app.py`
- **Rproxy Support**: Works with Rproxy gateway if API URL points to it
- **Threat Detection**: Displays security threats when messages are blocked by Rproxy
- **Single Message Mode**: Sends only current message to avoid context-based false positives
- **Secure API Keys**: API keys can be stored in `.env` file or entered in UI (password-protected)

### `main.py`
- **Automatic Threat Detection**: All messages scanned before reaching LLM
- **Threat Details**: Detailed information about detected threats
- **Blocked Messages**: Malicious messages are blocked and never sent to LLM
- **Secure API Keys**: API keys stored in `.env` file (not in code)

---

## Troubleshooting

### `app.py` Issues

### "OpenAI API key is required"
- Enter your API key in the sidebar "API Key" field
- Or set `OPENAI_API_KEY` in your `.env` file
- Verify your API key is valid at https://platform.openai.com/api-keys

### Messages Getting Blocked
- If using Rproxy, messages may be blocked due to security rules
- `app.py` sends only the current message (not conversation history) to reduce false positives
- Try using OpenAI API directly: set API URL to `https://api.openai.com/v1/chat/completions`

### Connection Errors
- Verify your API URL is correct and accessible
- Check your network connection
- Ensure the API endpoint is running

### `main.py` Issues

### "Authorization header is required"
- Ensure `RPROXY_AUTH_HEADER` is set in your `.env` file
- Check that your API key format is correct: `vpsk_live_...`

### "OpenAI API key is required"
- Ensure `OPENAI_API_KEY` is set in your `.env` file
- Verify your API key is valid at https://platform.openai.com/api-keys

### "Entity ID could not be extracted"
- Check that your Rproxy API key follows the format: `vpsk_live_{entityId}{random}`
- The entity ID should be 24 hex characters after `vpsk_live_`

### Connection Errors
- Verify your Rproxy URL is correct and accessible
- Check your network connection
- Ensure Rproxy service is running

---

## Differences Between `app.py` and `main.py`

### `app.py` (Simple ChatBot)
- **UI-Configurable**: All settings (API URL, API Key, Model) can be changed in sidebar
- **Single Message Mode**: Sends only current message to avoid context-based blocking
- **Simpler Architecture**: Direct API calls, no separate scanning step
- **Flexible Endpoints**: Can work with OpenAI directly or Rproxy gateway
- **Full UI History**: Conversation history displayed in UI but not sent to API

### `main.py` (Full-Featured App)
- **Two-Step Flow**: Scan with Rproxy first, then send to OpenAI if allowed
- **Environment Variables Only**: Settings configured via `.env` file
- **Full Context**: Sends conversation history to maintain context
- **Security Focus**: Explicit security scanning step before LLM
- **Detailed Status**: Shows scan status, latency, and threat details

## Differences from Legacy Version

This version differs from the legacy version in the following ways:

1. **No Database Dependency**: LLM configuration is in the app, not in a database
2. **Direct OpenAI Integration**: Messages sent directly to OpenAI after scanning
3. **Two-Step Flow**: Scan first, then LLM (instead of Rproxy forwarding)
4. **Simplified Architecture**: Removed entity/target lookup logic

---

## Requirements

- Python 3.8+
- Streamlit 1.40.0+
- requests 2.32.3+
- python-dotenv 1.0.0+

---

## License

This is a standalone application for secure AI chat interactions.

---

## Author

Anand S

Date: 2025-12-16

