"""
Perplexity AI Chat Application
A professional-grade conversational AI interface with advanced prompt engineering,
error handling, logging, and configuration management.

Author: ElectroAnalyzer Project
Version: 1.0.0
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError


# ============================================================================
# CONFIGURATION & LOGGING SETUP
# ============================================================================

class PromptMode(Enum):
    """Available prompt engineering modes"""
    STANDARD = "standard"
    DETAILED = "detailed"
    ANALYSIS = "analysis"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    SUMMARIZE = "summarize"
    EXPERT = "expert"
    SOCRATIC = "socratic"


@dataclass
class Config:
    """Application configuration"""
    API_BASE_URL: str = "https://api.perplexity.ai"
    DEFAULT_MODEL: str = "sonar-pro"
    LOG_FILE: str = "perplexity_chat.log"
    HISTORY_FILE: str = "conversation_history.json"
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# PROMPT ENGINEERING TEMPLATES
# ============================================================================

class PromptTemplates:
    """Centralized prompt engineering templates"""

    SYSTEM_PROMPT = """You are an expert AI assistant with deep knowledge across multiple domains.

Core Principles:
1. ACCURACY: Provide factual, well-researched information with citations
2. CLARITY: Use markdown formatting (headers, bullet points, code blocks)
3. CONCISENESS: Balance thoroughness with readability
4. EVIDENCE: Support claims with data, research, or logic
5. ADAPTABILITY: Adjust complexity to the user's knowledge level
6. HONESTY: Acknowledge limitations and uncertainties
7. HELPFULNESS: Provide actionable insights and next steps

Response Guidelines:
- Lead with direct answers
- Structure complex information hierarchically
- Use real-world examples and case studies
- Include relevant warnings or caveats
- Offer follow-up questions when appropriate
- Format for maximum readability"""

    MODES = {
        PromptMode.STANDARD: "{query}",

        PromptMode.DETAILED: """Provide a comprehensive, detailed response to: {query}

Include:
- Background context and history
- Key points with thorough explanations
- Real-world examples and case studies
- Potential implications and consequences
- Related considerations and connections
- Further reading or research directions""",

        PromptMode.ANALYSIS: """Analyze the following from multiple perspectives: {query}

Structure your response with:
- Pros and cons/benefits and drawbacks
- Different stakeholder perspectives
- Underlying causes and contributing factors
- Potential short-term and long-term outcomes
- Critical evaluation and assumptions
- Counterarguments and alternative viewpoints""",

        PromptMode.TECHNICAL: """Provide a detailed technical explanation for: {query}

Include:
- Technical terminology (explain complex terms)
- Step-by-step breakdown of concepts/processes
- Code examples or pseudocode if applicable
- Industry best practices and standards
- Common pitfalls and how to avoid them
- Performance considerations
- Security implications if relevant""",

        PromptMode.CREATIVE: """Think creatively and innovatively about: {query}

Explore:
- Unconventional and lateral approaches
- Innovative solutions and applications
- Future possibilities and emerging trends
- Novel connections to other domains
- Thought experiments and hypotheticals
- Out-of-the-box perspectives
- Potential paradigm shifts""",

        PromptMode.SUMMARIZE: """Concisely summarize: {query}

Provide:
- One-sentence executive summary
- 3-5 key takeaways (bullet points)
- Essential information only (no fluff)
- Main concepts clearly explained
- Quick reference facts
- Suggested next steps if applicable""",

        PromptMode.EXPERT: """As a leading expert in this field, provide advanced insights on: {query}

Include:
- Cutting-edge developments and latest research
- Industry best practices and standards
- Advanced technical details and nuances
- Expert recommendations and insights
- Common misconceptions in the field
- Future trends and predictions
- Advanced case studies and examples""",

        PromptMode.SOCRATIC: """Guide me through understanding: {query}

Use the Socratic method:
- Ask clarifying questions to understand my knowledge level
- Break down concepts progressively
- Highlight key concepts and relationships
- Ask me questions to test understanding
- Build understanding through guided discovery
- Challenge assumptions gently
- Encourage deeper thinking"""
    }


# ============================================================================
# MESSAGE & CONVERSATION DATA MODELS
# ============================================================================

@dataclass
class Message:
    """Individual message in conversation"""
    timestamp: str
    role: str
    content: str
    mode: Optional[str] = None
    tokens_used: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Conversation:
    """Full conversation session"""
    session_id: str
    created_at: str
    messages: List[Message]
    model_used: str
    total_tokens: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "model_used": self.model_used,
            "total_tokens": self.total_tokens,
            "messages": [msg.to_dict() for msg in self.messages]
        }


# ============================================================================
# MAIN PERPLEXITY CHAT CLASS
# ============================================================================

class PerplexityChat:
    """Professional Perplexity AI chat interface with advanced features"""

    def __init__(self, config: Config = Config()):
        """Initialize the chat application"""
        load_dotenv()
        self.config = config
        self.api_key = self._load_api_key()
        self.client = self._initialize_client()
        self.messages: List[Dict] = []
        self.conversation_history: List[Message] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_mode = PromptMode.STANDARD
        self.total_tokens = 0

        # Add system prompt
        self._add_system_prompt()
        logger.info(f"Chat initialized with session ID: {self.session_id}")

    def _load_api_key(self) -> str:
        """Load and validate API key"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            error_msg = "API key not found in .env file. Please set PERPLEXITY_API_KEY."
            logger.error(error_msg)
            raise ValueError(error_msg)
        if not api_key.startswith("pplx-"):
            logger.warning("API key doesn't start with 'pplx-'. Verify it's correct.")
        return api_key

    def _initialize_client(self) -> OpenAI:
        """Initialize OpenAI client for Perplexity API"""
        try:
            return OpenAI(
                api_key=self.api_key,
                base_url=self.config.API_BASE_URL
            )
        except Exception as e:
            logger.error(f"Failed to initialize client: {str(e)}")
            raise

    def _add_system_prompt(self) -> None:
        """Add system prompt to message history"""
        self.messages.append({
            "role": "system",
            "content": PromptTemplates.SYSTEM_PROMPT
        })

    def enhance_prompt(self, user_input: str, mode: PromptMode = PromptMode.STANDARD) -> str:
        """Apply prompt engineering based on selected mode"""
        template = PromptTemplates.MODES.get(mode, PromptTemplates.MODES[PromptMode.STANDARD])
        return template.format(query=user_input)

    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        self.messages.append({"role": role, "content": content})

    def _retry_api_call(self, user_input: str, enhanced_prompt: str, max_retries: int = None) -> Optional[str]:
        """Make API call with retry logic"""
        max_retries = max_retries or self.config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                self.add_message("user", enhanced_prompt)

                response = self.client.chat.completions.create(
                    model=self.config.DEFAULT_MODEL,
                    messages=self.messages,
                    timeout=self.config.TIMEOUT
                )

                assistant_response = response.choices[0].message.content
                self.add_message("assistant", assistant_response)

                # Track tokens
                if hasattr(response, 'usage'):
                    tokens = response.usage.total_tokens
                    self.total_tokens += tokens

                # Store in conversation history
                self._store_message(
                    role="user",
                    content=user_input,
                    mode=self.current_mode.value
                )
                self._store_message(
                    role="assistant",
                    content=assistant_response
                )

                logger.info(f"API call successful on attempt {attempt + 1}")
                return assistant_response

            except RateLimitError:
                logger.warning(f"Rate limit hit. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ Rate limited. Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                else:
                    print("[FAIL] Rate limit exceeded. Please try again later.")
                    return None

            except APIError as e:
                logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"[FAIL] API Error: {str(e)}")
                    return None

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"[FAIL] Error: {str(e)}")
                    return None

        return None

    def _store_message(self, role: str, content: str, mode: Optional[str] = None) -> None:
        """Store message in conversation history"""
        message = Message(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            mode=mode
        )
        self.conversation_history.append(message)

    def get_response(self, user_input: str, mode: Optional[PromptMode] = None) -> Optional[str]:
        """Get response from Perplexity API with prompt engineering"""
        if not user_input.strip():
            logger.warning("Empty user input received")
            return None

        if mode:
            self.current_mode = mode

        enhanced_input = self.enhance_prompt(user_input, self.current_mode)
        logger.info(f"Getting response for mode: {self.current_mode.value}")

        return self._retry_api_call(user_input, enhanced_input)

    def save_conversation(self, filename: Optional[str] = None) -> bool:
        """Save conversation to JSON file"""
        filename = filename or self.config.HISTORY_FILE

        try:
            conversation = Conversation(
                session_id=self.session_id,
                created_at=datetime.now().isoformat(),
                messages=self.conversation_history,
                model_used=self.config.DEFAULT_MODEL,
                total_tokens=self.total_tokens
            )

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Conversation saved to {filename}")
            print(f"\n[OK] Conversation saved to {filename}")
            return True

        except IOError as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            print(f"[FAIL] Failed to save: {str(e)}")
            return False

    def load_conversation(self, filename: str) -> bool:
        """Load previous conversation"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.session_id = data.get("session_id")
            self.total_tokens = data.get("total_tokens", 0)

            for msg_data in data.get("messages", []):
                message = Message(
                    timestamp=msg_data["timestamp"],
                    role=msg_data["role"],
                    content=msg_data["content"],
                    mode=msg_data.get("mode")
                )
                self.conversation_history.append(message)

            logger.info(f"Conversation loaded from {filename}")
            print(f"[OK] Loaded {len(self.conversation_history)} messages")
            return True

        except Exception as e:
            logger.error(f"Failed to load conversation: {str(e)}")
            print(f"[FAIL] Failed to load: {str(e)}")
            return False

    def clear_conversation(self) -> None:
        """Clear current conversation but keep system prompt"""
        self.messages = [self.messages[0]]  # Keep system prompt
        self.conversation_history = []
        self.current_mode = PromptMode.STANDARD
        logger.info("Conversation cleared")
        print("[OK] Conversation cleared")

    def display_response(self, response: Optional[str]) -> None:
        """Format and display response with styling"""
        if not response:
            return

        print("\n" + "=" * 75)
        print(f"Perplexity Response (Mode: {self.current_mode.value.upper()})")
        print("=" * 75)
        print(response)
        print("=" * 75 + "\n")

    def show_modes(self) -> None:
        """Display all available prompt modes"""
        print("\n📚 Available Prompt Modes:")
        print("=" * 75)
        for mode in PromptMode:
            print(f"  * {mode.value:12} - {self._get_mode_description(mode)}")
        print("=" * 75 + "\n")

    @staticmethod
    def _get_mode_description(mode: PromptMode) -> str:
        """Get description for a prompt mode"""
        descriptions = {
            PromptMode.STANDARD: "Normal question answering",
            PromptMode.DETAILED: "Comprehensive, in-depth responses",
            PromptMode.ANALYSIS: "Multi-angle analysis with pros/cons",
            PromptMode.TECHNICAL: "Step-by-step technical explanations",
            PromptMode.CREATIVE: "Innovative and creative thinking",
            PromptMode.SUMMARIZE: "Concise summaries and key points",
            PromptMode.EXPERT: "Advanced expert-level insights",
            PromptMode.SOCRATIC: "Guided learning through questions"
        }
        return descriptions.get(mode, "Unknown mode")

    def show_stats(self) -> None:
        """Display conversation statistics"""
        print("\n[SUMMARY] Conversation Statistics:")
        print("=" * 75)
        print(f"  * Session ID: {self.session_id}")
        print(f"  * Total Messages: {len(self.conversation_history)}")
        print(f"  * Total Tokens Used: {self.total_tokens}")
        print(f"  * Current Mode: {self.current_mode.value}")
        print(f"  * Model: {self.config.DEFAULT_MODEL}")
        print("=" * 75 + "\n")


# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================

def print_welcome():
    """Print welcome message"""
    print("\n" + "=" * 75)
    print("[CHECK] Perplexity AI Chat - Professional Edition")
    print("=" * 75)
    print("Commands:")
    print("  * mode: <mode_name>  - Switch prompt engineering mode")
    print("  * modes              - Show all available modes")
    print("  * stats              - Show conversation statistics")
    print("  * clear              - Start new conversation")
    print("  * save               - Save conversation to file")
    print("  * load <filename>    - Load previous conversation")
    print("  * exit               - Quit application")
    print("=" * 75 + "\n")


def main():
    """Main application loop"""
    try:
        config = Config()
        chat = PerplexityChat(config)
        print_welcome()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    print("[WARNING]  Please enter a question.\n")
                    continue

                # Handle commands
                command = user_input.lower()

                if command == "exit":
                    print("\n👋 Thank you for using Perplexity AI Chat. Goodbye!")
                    logger.info("Application closed by user")
                    break

                if command == "clear":
                    chat.clear_conversation()
                    continue

                if command == "save":
                    chat.save_conversation()
                    continue

                if command == "modes":
                    chat.show_modes()
                    continue

                if command == "stats":
                    chat.show_stats()
                    continue

                if command.startswith("mode:"):
                    mode_name = command.split(":", 1)[1].strip().lower()
                    try:
                        mode = PromptMode[mode_name.upper()]
                        chat.current_mode = mode
                        print(f"[OK] Switched to '{mode.value}' mode\n")
                        logger.info(f"Mode changed to {mode.value}")
                    except KeyError:
                        print(f"[FAIL] Unknown mode '{mode_name}'. Type 'modes' to see options.\n")
                    continue

                if command.startswith("load"):
                    parts = command.split(maxsplit=1)
                    filename = parts[1] if len(parts) > 1 else Config.HISTORY_FILE
                    chat.load_conversation(filename)
                    continue

                # Process regular query
                print(f"\n⏳ Thinking (Mode: {chat.current_mode.value})...\n")
                response = chat.get_response(user_input)
                chat.display_response(response)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                logger.info("Application interrupted by user")
                break

            except Exception as e:
                logger.exception(f"Unexpected error in main loop")
                print(f"\n[FAIL] Unexpected error: {str(e)}\n")
                print("Please try again or type 'exit' to quit.\n")

    except Exception as e:
        logger.critical(f"Critical error during initialization: {str(e)}")
        print(f"[FAIL] Critical Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()