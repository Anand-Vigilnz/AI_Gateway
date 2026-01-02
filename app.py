"""
app.py

Purpose:
    Simple Streamlit-based chatbot that sends messages directly to OpenAI API.
    Supports configurable API URL, API key, and model name via environment variables.

Author:
    Anand S

Date:
    2025-12-16

Last Modified:
    2025-12-16
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

import config


def send_to_openai(
    messages: List[Dict[str, str]],
    model: str,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> Tuple[Dict[str, Any], float, int]:
    """
    Send messages to OpenAI API for LLM inference.

    Parameters
    ----------
    messages:
        List of message dictionaries with "role" and "content" keys.
    model:
        OpenAI model name (e.g., "gpt-4o-mini").
    api_key:
        OpenAI API key. If None, uses OPENAI_API_KEY from config.
    api_url:
        OpenAI API URL. If None, uses OPENAI_API_URL from config.
    timeout_seconds:
        Request timeout in seconds.

    Returns
    -------
    response_dict:
        OpenAI API response dictionary.
    latency_ms:
        Round-trip latency in milliseconds.
    status_code:
        HTTP status code returned by OpenAI.
    """
    if not messages:
        raise ValueError("Messages list must not be empty.")
    
    if api_key is None:
        api_key = config.OPENAI_API_KEY
    
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file.")
    
    if api_url is None:
        api_url = config.OPENAI_API_URL
    
    if not api_url:
        raise ValueError("OpenAI API URL is required. Set OPENAI_API_URL in .env file.")
    
    if not model:
        model = config.DEFAULT_MODEL

    request_body = {
        "model": model,
        "messages": messages,
    }
    
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    start = time.perf_counter()
    try:
        resp = requests.post(
            api_url,
            json=request_body,
            headers=headers,
            timeout=timeout_seconds,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        
        # Parse response JSON first
        try:
            response_data = resp.json()
        except json.JSONDecodeError:
            response_data = {"raw": resp.text}
        
        # Check if this is a Rproxy response with action field
        # Rproxy can return status 200 with action="blocked" or action="error"
        if "action" in response_data:
            action = response_data.get("action")
            if action == "blocked":
                error_payload = {
                    "error": True,
                    "message": response_data.get("message", "Message blocked by security gateway"),
                    "raw": response_data,
                    "threats": response_data.get("threats", []),
                }
                return error_payload, elapsed_ms, resp.status_code
            elif action == "error":
                error_payload = {
                    "error": True,
                    "message": response_data.get("message", "Error from gateway"),
                    "raw": response_data,
                }
                return error_payload, elapsed_ms, resp.status_code
            # If action == "allowed", continue to process as OpenAI response
        
        # Check HTTP status codes for errors
        if resp.status_code >= 400:
            try:
                error_data = response_data if isinstance(response_data, dict) else resp.json()
                error_message = error_data.get("error", {}).get("message") if isinstance(error_data.get("error"), dict) else error_data.get("error") or resp.text
            except:
                error_message = resp.text or f"HTTP {resp.status_code} error"
            
            error_payload = {
                "error": True,
                "message": error_message,
                "raw": {"status_code": resp.status_code, "response": resp.text},
            }
            return error_payload, elapsed_ms, resp.status_code
        
        return response_data, elapsed_ms, resp.status_code
        
    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        error_payload = {
            "error": True,
            "message": f"Request timeout after {timeout_seconds}s. API may be slow or unreachable.",
            "raw": {},
        }
        return error_payload, elapsed_ms, 0
        
    except requests.exceptions.ConnectionError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        error_payload = {
            "error": True,
            "message": f"Connection error: Unable to reach API at {api_url}. Check your network and URL.",
            "raw": {"error": str(exc)},
        }
        return error_payload, elapsed_ms, 0
        
    except requests.RequestException as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        error_payload = {
            "error": True,
            "message": f"Request failed: {str(exc)}",
            "raw": {"error": str(exc)},
        }
        return error_payload, elapsed_ms, 0
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        error_payload = {
            "error": True,
            "message": f"Unexpected error: {str(exc)}",
            "raw": {"error": str(exc)},
        }
        return error_payload, elapsed_ms, 0


def _extract_openai_content(response: Dict[str, Any]) -> str:
    """
    Extract message content from OpenAI API response.

    Parameters
    ----------
    response:
        OpenAI API response dictionary.

    Returns
    -------
    Extracted message content string.
    """
    if "choices" in response and isinstance(response["choices"], list) and len(response["choices"]) > 0:
        first_choice = response["choices"][0]
        if isinstance(first_choice, dict):
            if "message" in first_choice and isinstance(first_choice["message"], dict):
                return first_choice["message"].get("content", "")
            elif "text" in first_choice:
                return first_choice["text"]
            elif "delta" in first_choice and isinstance(first_choice["delta"], dict):
                return first_choice["delta"].get("content", "")
    return ""


def _init_session_state() -> None:
    """
    Initialize Streamlit session state keys with values from config.
    """
    defaults: Dict[str, Any] = {
        "chat_history": [],
        "api_url": config.OPENAI_API_URL,
        "api_key": config.OPENAI_API_KEY,
        "model_name": config.DEFAULT_MODEL,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    """
    Main Streamlit application entry point.
    """
    st.set_page_config(
        page_title="Simple ChatBot",
        page_icon="💬",
        layout="wide",
    )
    
    st.title("💬 Simple ChatBot")
    st.markdown(
        "Chat with AI using OpenAI API. Configure API URL, API key, and model in the sidebar or via environment variables."
    )
    
    _init_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown(
            "**Note:** Values are initialized from `.env` file but can be changed here. "
            "Changes take effect immediately for new messages."
        )
        
        st.subheader("API Configuration")
        
        st.text_input(
            "API URL",
            value=st.session_state.api_url,
            key="api_url",
            help="The OpenAI API endpoint URL (e.g., https://api.openai.com/v1/chat/completions).",
        )
        
        st.text_input(
            "API Key",
            value=st.session_state.api_key,
            key="api_key",
            type="password",
            help="Your OpenAI API key. Leave empty to use value from .env file.",
        )
        
        st.text_input(
            "Model Name",
            value=st.session_state.model_name,
            key="model_name",
            help="OpenAI model to use (e.g., gpt-4o-mini, gpt-4, gpt-3.5-turbo).",
        )
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
        
        st.divider()
        st.markdown("### 📊 Connection Info")
        st.info(f"**API URL:** `{st.session_state.api_url}`")
        st.info(f"**Model:** `{st.session_state.model_name}`")
        if not st.session_state.api_key:
            st.warning("⚠️ API key not set. Please enter it above or set OPENAI_API_KEY in .env file.")
        else:
            st.success("✅ API key configured")

    # Display chat history
    for message in st.session_state.chat_history:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        timestamp = message.get("timestamp")
        
        with st.chat_message(role):
            st.write(content)
            if timestamp:
                st.caption(f"{timestamp}")
            
            # Show error details if present
            if message.get("error"):
                # Check if this is a blocked message with threats
                threats = message.get("threats", [])
                if threats:
                    st.error("🛡️ Message blocked by security gateway")
                    with st.expander("Security threats detected", expanded=True):
                        for idx, threat in enumerate(threats, start=1):
                            category = str(threat.get("category", "unknown")).replace("_", " ")
                            severity = threat.get("severity", "UNKNOWN")
                            method = threat.get("method", "unknown")
                            reason = threat.get("reason", "")
                            
                            st.markdown(f"**{idx}. {category}**")
                            cols = st.columns([1, 1])
                            with cols[0]:
                                st.markdown(f"Severity: `{severity}`")
                            with cols[1]:
                                st.markdown(f"Method: `{method}`")
                            if reason:
                                st.markdown(f"*{reason}*")
                            if idx < len(threats):
                                st.divider()
                else:
                    with st.expander("❌ Error Details", expanded=False):
                        st.error(message.get("error_message", "Unknown error"))
                        if message.get("raw_data"):
                            st.json(message.get("raw_data"))

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to history immediately
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.chat_history.append(user_message)
        
        # Process the message
        with st.spinner("🤖 Getting response from AI..."):
            try:
                # Send only the current message to avoid context-based blocking by Rproxy
                # Full conversation history is still maintained in UI for display purposes
                openai_messages = [{
                    "role": "user",
                    "content": user_input
                }]
                
                # Send to OpenAI API
                # Use UI values, but fall back to config if empty
                api_key = st.session_state.api_key if st.session_state.api_key else None
                api_url = st.session_state.api_url if st.session_state.api_url else None
                model = st.session_state.model_name if st.session_state.model_name else None
                
                openai_response, openai_latency, openai_status = send_to_openai(
                    messages=openai_messages,
                    model=model,
                    api_key=api_key,
                    api_url=api_url,
                )
                
                # Extract content from OpenAI response
                if openai_response.get("error"):
                    content = openai_response.get("message", "Error from API.")
                    threats = openai_response.get("threats", [])
                    assistant_message = {
                        "role": "assistant",
                        "content": content,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": True,
                        "error_message": content,
                        "threats": threats,
                        "raw_data": openai_response.get("raw", {}),
                        "latency_ms": openai_latency,
                        "status_code": openai_status,
                    }
                else:
                    content = _extract_openai_content(openai_response)
                    if not content:
                        content = "No response content received from API."
                    
                    assistant_message = {
                        "role": "assistant",
                        "content": content,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": False,
                        "latency_ms": openai_latency,
                        "status_code": openai_status,
                    }
                
                st.session_state.chat_history.append(assistant_message)
                st.rerun()
                
            except Exception as exc:
                error_message = {
                    "role": "assistant",
                    "content": f"Error: {str(exc)}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": True,
                    "error_message": str(exc),
                    "raw_data": {"error": str(exc)},
                    "latency_ms": 0,
                    "status_code": 0,
                }
                st.session_state.chat_history.append(error_message)
                st.rerun()


if __name__ == "__main__":
    main()

