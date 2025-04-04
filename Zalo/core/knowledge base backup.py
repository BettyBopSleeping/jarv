import json
import os
import random
import re
import difflib


class KnowledgeBase:
    def __init__(self, knowledge_base_path="knowledge_base.json", similarity_threshold=0.6):
        """Initialize the Knowledge Base with advanced features.
        
        :param knowledge_base_path: Path to the JSON knowledge base file
        :param similarity_threshold: Threshold for fuzzy matching topics
        """
        # Ensure paths work on different platforms
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.knowledge_base_path = os.path.join(base_dir, knowledge_base_path)
        except:
            self.knowledge_base_path = knowledge_base_path
        
        # Similarity threshold for fuzzy matching
        self.similarity_threshold = similarity_threshold
        
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base()
        
        # Context tracking
        self.conversation_context = {
            'last_topic': None,
            'last_response': None,
            'conversation_history': []
        }

    def load_knowledge_base(self):
        """Load the knowledge base from a JSON file with enhanced error handling.
        
        :return: Dictionary containing the knowledge base
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
            
            if not os.path.exists(self.knowledge_base_path):
                # Create an empty knowledge base if file doesn't exist
                base_data = {
                    "topics": {},
                    "responses": {},
                    "metadata": {
                        "created_at": os.path.getctime(self.knowledge_base_path),
                        "last_updated": os.path.getmtime(self.knowledge_base_path)
                    }
                }
                with open(self.knowledge_base_path, 'w') as file:
                    json.dump(base_data, file, indent=4)
                return base_data
            
            with open(self.knowledge_base_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {
                "topics": {},
                "responses": {},
                "metadata": {}
            }

    def save_knowledge_base(self):
        """Save the current knowledge base to a JSON file with additional metadata."""
        try:
            # Update metadata
            self.knowledge_base["metadata"] = {
                "last_updated": os.path.getmtime(self.knowledge_base_path),
                "total_topics": len(self.knowledge_base["topics"])
            }
            
            with open(self.knowledge_base_path, 'w') as file:
                json.dump(self.knowledge_base, file, indent=4)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def learn(self, topic, response, context=None):
        """Learn a new piece of information with advanced features.
        
        :param topic: The topic to learn about
        :param response: The information or response to associate with the topic
        :param context: Optional context for the response
        :return: Confirmation message
        """
        # Normalize topic
        topic = topic.lower().strip()
        
        # Add to knowledge base
        if topic not in self.knowledge_base["topics"]:
            self.knowledge_base["topics"][topic] = []
        
        # Create a response entry with optional context
        response_entry = {
            "text": response,
            "context": context,
            "timestamp": os.path.getmtime(self.knowledge_base_path)
        }
        
        # Avoid duplicate responses
        if response_entry not in self.knowledge_base["topics"][topic]:
            self.knowledge_base["topics"][topic].append(response_entry)
        
        # Save the updated knowledge base
        self.save_knowledge_base()
        return f"Learned about {topic}!"

    def find_similar_topic(self, user_input):
        """Find similar topics using fuzzy matching.
        
        :param user_input: User's input to match against topics
        :return: Most similar topic or None
        """
        user_input = user_input.lower().strip()
        
        # Direct match first
        if user_input in self.knowledge_base["topics"]:
            return user_input
        
        # Fuzzy matching
        topics = list(self.knowledge_base["topics"].keys())
        matches = difflib.get_close_matches(user_input, topics, n=1, cutoff=self.similarity_threshold)
        
        return matches[0] if matches else None

    def get_response(self, user_input, context_sensitive=True):
        """Get a response from the knowledge base with advanced features.
        
        :param user_input: User's input
        :param context_sensitive: Whether to use conversation context
        :return: A response from the knowledge base or None
        """
        user_input = user_input.lower().strip()
        
        # Find the most relevant topic
        topic = self.find_similar_topic(user_input)
        
        if not topic:
            return None
        
        # Get responses for the topic
        responses = self.knowledge_base["topics"][topic]
        
        # Context-sensitive response selection
        if context_sensitive and self.conversation_context['last_topic']:
            # Prefer responses that build upon previous context
            context_responses = [
                r for r in responses 
                if r.get('context') == self.conversation_context['last_topic']
            ]
            
            if context_responses:
                selected_response = random.choice(context_responses)
            else:
                selected_response = random.choice(responses)
        else:
            selected_response = random.choice(responses)
        
        # Update conversation context
        self.conversation_context['last_topic'] = topic
        self.conversation_context['last_response'] = selected_response
        self.conversation_context['conversation_history'].append({
            'input': user_input,
            'topic': topic,
            'response': selected_response
        })
        
        return selected_response['text']

    def forget(self, topic=None, response=None):
        """Forget specific knowledge.
        
        :param topic: Topic to forget entirely
        :param response: Specific response to remove from a topic
        :return: Confirmation message
        """
        if topic and topic in self.knowledge_base["topics"]:
            # Forget entire topic
            if not response:
                del self.knowledge_base["topics"][topic]
                self.save_knowledge_base()
                return f"Forgot everything about {topic}"
            
            # Remove specific response from topic
            self.knowledge_base["topics"][topic] = [
                r for r in self.knowledge_base["topics"][topic] 
                if r['text'] != response
            ]
            
            # Remove topic if no responses left
            if not self.knowledge_base["topics"][topic]:
                del self.knowledge_base["topics"][topic]
            
            self.save_knowledge_base()
            return f"Forgot specific information about {topic}"
        
        return "Nothing to forget"

    def export_knowledge(self, export_path=None):
        """Export knowledge base to a specified path.
        
        :param export_path: Path to export the knowledge base
        :return: Path of exported file
        """
        if not export_path:
            export_path = f"{self.knowledge_base_path}.backup"
        
        try:
            with open(export_path, 'w') as file:
                json.dump(self.knowledge_base, file, indent=4)
            return export_path
        except Exception as e:
            print(f"Error exporting knowledge base: {e}")
            return None

    def import_knowledge(self, import_path):
        """Import knowledge from another knowledge base file.
        
        :param import_path: Path to the knowledge base file to import
        :return: Number of topics imported
        """
        try:
            with open(import_path, 'r') as file:
                imported_data = json.load(file)
            
            # Merge imported topics
            for topic, responses in imported_data.get("topics", {}).items():
                if topic not in self.knowledge_base["topics"]:
                    self.knowledge_base["topics"][topic] = []
                
                # Add unique responses
                for response in responses:
                    if response not in self.knowledge_base["topics"][topic]:
                        self.knowledge_base["topics"][topic].append(response)
            
            # Save merged knowledge base
            self.save_knowledge_base()
            
            return len(imported_data.get("topics", {}))
        except Exception as e:
            print(f"Error importing knowledge base: {e}")
            return 0


# Example usage
if __name__ == "__main__":
    # Create or load a knowledge base
    kb = KnowledgeBase()
    
    # Learn some information
    kb.learn("python", "Python is a high-level programming language")
    kb.learn("python", "Python is great for data science", context="programming")
    
    # Get a response
    response = kb.get_response("tell me about python")
    print(response)
    
    # Export and import functionality
    export_path = kb.export_knowledge()
    print(f"Knowledge base exported to {export_path}")
    
    # Forget specific knowledge
    kb.forget("python", "Python is a high-level programming language")