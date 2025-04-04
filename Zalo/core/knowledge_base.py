import json
import os
import random
import re
import difflib


class KnowledgeBase:
    def __init__(self, knowledge_base_path="knowledge_base.json", filename="knowledge.json", similarity_threshold=0.6):
        """Initialize the Knowledge Base with both knowledge_base.json and knowledge.json."""
        
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.knowledge_base_path = os.path.join(base_dir, knowledge_base_path)
            self.filename = os.path.join(base_dir, filename)
        except:
            self.knowledge_base_path = knowledge_base_path
            self.filename = filename
        
        self.similarity_threshold = similarity_threshold
        self.load_knowledge_base()
        self.load_knowledge()
        
        self.conversation_context = {
            'last_topic': None,
            'last_response': None,
            'conversation_history': []
        }

    def load_knowledge_base(self):
        """Load the knowledge base from knowledge_base.json."""
        try:
            os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
            
            if not os.path.exists(self.knowledge_base_path):
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
                self.knowledge_base = base_data
            else:
                with open(self.knowledge_base_path, 'r') as file:
                    self.knowledge_base = json.load(file)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self.knowledge_base = {"topics": {}, "responses": {}, "metadata": {}}
    
    def load_knowledge(self):
        """Load the knowledge from knowledge.json."""
        try:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            
            if not os.path.exists(self.filename):
                with open(self.filename, 'w') as file:
                    json.dump({"topics": {}}, file, indent=4)
                self.knowledge = {"topics": {}}
            else:
                with open(self.filename, 'r') as file:
                    self.knowledge = json.load(file)
        except Exception as e:
            print(f"Error loading knowledge: {e}")
            self.knowledge = {"topics": {}}

    def save_knowledge_base(self):
        """Save the knowledge base to knowledge_base.json."""
        try:
            self.knowledge_base["metadata"] = {
                "last_updated": os.path.getmtime(self.knowledge_base_path),
                "total_topics": len(self.knowledge_base["topics"])
            }
            with open(self.knowledge_base_path, 'w') as file:
                json.dump(self.knowledge_base, file, indent=4)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def save_knowledge(self):
        """Save the knowledge to knowledge.json."""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.knowledge, file, indent=4)
        except Exception as e:
            print(f"Error saving knowledge: {e}")

    def get_response(self, topic, context_sensitive=True):
        """Retrieve the response for a given topic with context sensitivity."""
        topic = topic.lower().strip()
        
        # Find the most relevant topic using fuzzy matching if necessary
        if topic not in self.knowledge_base["topics"]:
            topic = self.find_similar_topic(topic)
        
        if topic:
            responses = self.knowledge_base["topics"][topic]
            if context_sensitive and self.conversation_context['last_topic']:
                context_responses = [
                    r for r in responses if r.get('context') == self.conversation_context['last_topic']
                ]
                selected_response = random.choice(context_responses) if context_responses else random.choice(responses)
            else:
                selected_response = random.choice(responses)
            
            # Update conversation context
            self.conversation_context['last_topic'] = topic
            self.conversation_context['last_response'] = selected_response
            self.conversation_context['conversation_history'].append({
                'input': topic,
                'response': selected_response
            })
            return selected_response['text']
        return None

    def teach(self, topic, response):
        """Teach Zalo a new topic and response (saves to knowledge.json)."""
        topic = topic.lower().strip()
        self.knowledge["topics"][topic] = [{"text": response}]
        self.save_knowledge()

    def learn(self, topic, response, context=None):
        """Learn a new piece of information (saves to knowledge_base.json)."""
        topic = topic.lower().strip()
        if topic not in self.knowledge_base["topics"]:
            self.knowledge_base["topics"][topic] = []
        
        response_entry = {
            "text": response,
            "context": context,
            "timestamp": os.path.getmtime(self.knowledge_base_path)
        }
        
        # Avoid duplicate responses
        if response_entry not in self.knowledge_base["topics"][topic]:
            self.knowledge_base["topics"][topic].append(response_entry)
        
        self.save_knowledge_base()
        return f"Learned about {topic}!"

    def find_similar_topic(self, user_input):
        """Find similar topics using fuzzy matching."""
        user_input = user_input.lower().strip()
        if user_input in self.knowledge_base["topics"]:
            return user_input
        topics = list(self.knowledge_base["topics"].keys())
        matches = difflib.get_close_matches(user_input, topics, n=1, cutoff=self.similarity_threshold)
        return matches[0] if matches else None

    def forget(self, topic=None, response=None):
        """Forget specific knowledge."""
        if topic and topic in self.knowledge_base["topics"]:
            if not response:
                del self.knowledge_base["topics"][topic]
                self.save_knowledge_base()
                return f"Forgot everything about {topic}"
            self.knowledge_base["topics"][topic] = [
                r for r in self.knowledge_base["topics"][topic] if r['text'] != response
            ]
            if not self.knowledge_base["topics"][topic]:
                del self.knowledge_base["topics"][topic]
            self.save_knowledge_base()
            return f"Forgot specific information about {topic}"
        return "Nothing to forget"

    def export_knowledge(self, export_path=None):
        """Export knowledge base to a specified path."""
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
        """Import knowledge from another knowledge base file."""
        try:
            with open(import_path, 'r') as file:
                imported_data = json.load(file)
            for topic, responses in imported_data.get("topics", {}).items():
                if topic not in self.knowledge_base["topics"]:
                    self.knowledge_base["topics"][topic] = []
                for response in responses:
                    if response not in self.knowledge_base["topics"][topic]:
                        self.knowledge_base["topics"][topic].append(response)
            self.save_knowledge_base()
            return len(imported_data.get("topics", {}))
        except Exception as e:
            print(f"Error importing knowledge base: {e}")
            return 0