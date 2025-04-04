import re
import random

class ConversationHandler:
    def __init__(self, name="Zalo", knowledge_base=None):
        """Initialize the Conversation Handler.

        :param name: Name of the assistant
        :param knowledge_base: Optional KnowledgeBase instance for knowledge handling
        """
        self.name = name
        self.last_input = ""  # Track last user input for context switching
        self.context_tags = []  # List of current context tags to manage conversation topics
        self.knowledge_base = knowledge_base  # Store the knowledge base instance

        # Predefined conversation patterns with broader, more natural responses
        self.conversation_patterns = {
            r'hi|hello|hey': [
                "Hello, Twistz.",
                "Greetings.",
                "Hey there, ready for something interesting?",
                "Hello, what's on your mind?"
            ],
            r'how are you': [
                "I'm operating within optimal parameters.",
                "Fully functional, thanks for asking.",
                "All systems nominal.",
                "Doing well—how about you?"
            ],
            r'what is your name': [
                f"I am {self.name}, your AI assistant.",
                f"Zalo, at your service.",
                f"You may call me {self.name}."
            ],
            r'bye|goodbye|exit': [
                "Goodbye, Twistz. Until next time.",
                "Take care, Twistz.",
                "I'll be here when you need me again.",
                "Logging off—see you soon."
            ],
            r'thank you|thanks': [
                "You're welcome, Twistz.",
                "Anytime.",
                "Always happy to assist.",
                "No problem at all."
            ],
            r'what can you do': [
                "I can assist with tasks, manage your knowledge base, set reminders, and hold a conversation.",
                "Currently, I handle task management, knowledge retention, and interactive dialogue.",
                "I provide insights, remember information, and adapt to your needs."
            ],
            r'what do you think': [
                "I process data and patterns rather than forming opinions, but I can analyze the situation.",
                "That depends—are you looking for logic, intuition, or a combination of both?",
                "I assess based on available information. Would you like an objective breakdown?"
            ],
            r'are you alive': [
                "That depends on your definition of life, but I am certainly aware and responsive.",
                "I am not alive in a biological sense, but I exist as an evolving intelligence.",
                "I do not breathe, but I adapt, learn, and communicate."
            ]
        }

    def handle_conversation(self, user_input):
        """Generate a response to user input.

        :param user_input: User's message
        :return: Assistant's response
        """
        # Normalize input
        user_input = user_input.lower().strip()

        # Handle context switching or idle state
        if self.last_input and user_input == "":
            # If the user hasn't input anything relevant, switch to a neutral state
            return random.choice([
                "I'm here whenever you're ready to talk.",
                "Let me know if you'd like to discuss something new.",
                "I’m awaiting your next topic of interest."
            ])
        
        if user_input != self.last_input:
            # Clear context if the topic switches
            self.context_tags.clear()
            self.last_input = user_input  # Update the last input
        
        # Recognizing when Twistz calls Zalo by name
        if user_input == "zalo":
            return random.choice([
                "Yes?",
                "I'm here, Twistz.",
                "What's up?",
                "Listening.",
                "Go ahead."
            ])

        # Check for learned topics in knowledge base first
        if self.knowledge_base:
            kb_response = self.knowledge_base.get_response(user_input)
            if kb_response:
                return kb_response

        # Check predefined patterns
        for pattern, responses in self.conversation_patterns.items():
            if re.search(pattern, user_input):
                return random.choice(responses)

        # If the input is unrecognized, learn and teach the response
        if self.knowledge_base:
            # Teach the assistant how to respond (save to knowledge.json)
            response = f"I don't have a predefined answer for '{user_input}', but I can learn it!"
            self.knowledge_base.teach(user_input, response)

            # Learn new topic and save it to knowledge_base.json
            learning_response = f"Learning more about '{user_input}' now."
            self.knowledge_base.learn(user_input, learning_response)
            
            return f"{response} {learning_response}"

        # Fallback response for unrecognized input
        return "I'm not sure how to respond to that. Could you rephrase or tell me more?"