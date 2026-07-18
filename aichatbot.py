# aichatbot.py
"""
Enhanced AI Chatbot logic for FaceAI platform.
Provides intelligent responses for both user and admin contexts.
"""

import re
from datetime import datetime
import random

class FaceAIChatbot:
    def __init__(self):
        self.context = "general"
        self.user_name = None
        self.user_role = None
        
    def set_user_context(self, user_name=None, user_role=None):
        """Set user context for personalized responses"""
        self.user_name = user_name
        self.user_role = user_role
        
    def get_response(self, user_message: str) -> str:
        """Main method to get AI response based on user input"""
        if not user_message.strip():
            return "Please type a message so I can help you! 😊"
            
        message = user_message.lower().strip()
        
        # Check for greetings first
        greeting_response = self._handle_greetings(message)
        if greeting_response:
            return greeting_response
            
        # Check for admin-specific queries
        if self.user_role == "admin":
            admin_response = self._handle_admin_queries(message)
            if admin_response:
                return admin_response
        
        # Handle general queries
        return self._handle_general_queries(message)
    
    def _handle_greetings(self, message: str) -> str:
        """Handle greeting messages"""
        greetings = {
            "hi": "Hello! 👋 How can I assist you with FaceAI today?",
            "hello": "Hi there! 😊 What can I help you with?",
            "hey": "Hey! 👋 Ready to help you with FaceAI!",
            "good morning": "Good morning! ☀️ How can I assist you today?",
            "good afternoon": "Good afternoon! 🌤️ What can I help you with?",
            "good evening": "Good evening! 🌙 How can I assist you?",
            "how are you": "I'm functioning perfectly! 😊 How can I help you with FaceAI today?",
            "who are you": "I'm FaceAI's intelligent assistant! 🤖 I'm here to help you with everything about our face analysis platform.",
            "what can you do": "I can help you with FaceAI features, pricing, technical questions, admin tasks, and much more! Just ask me anything! 😊"
        }
        
        for greeting, response in greetings.items():
            if greeting in message:
                if self.user_name:
                    return f"Hi {self.user_name}! 👋 {response.split('!')[1] if '!' in response else response}"
                return response
                
        return None
    
    def _handle_admin_queries(self, message: str) -> str:
        """Handle admin-specific queries"""
        admin_queries = {
            "user": {
                "keywords": ["user", "users", "member", "members", "account", "accounts"],
                "responses": [
                    "I can help you manage users! You can view all users, edit their details, change roles, or delete accounts from the user management table.",
                    "User management is available in the main admin panel. You can see total users, their roles, creation dates, and last login times.",
                    "Need to manage users? Check the User Management section where you can view, edit, or delete user accounts."
                ]
            },
            "system": {
                "keywords": ["system", "stats", "statistics", "performance", "status"],
                "responses": [
                    "System information is displayed in the System Information section. You can see total users, active sessions, system status, and backup information.",
                    "The admin panel shows real-time system statistics including user count, system status, and performance metrics.",
                    "Check the System Information section for detailed stats about the platform's performance and user activity."
                ]
            },
            "backup": {
                "keywords": ["backup", "data", "export", "download"],
                "responses": [
                    "You can generate system backups and reports using the Quick Actions buttons in the System Information section.",
                    "Data backup and export features are available in the admin panel's Quick Actions area.",
                    "Use the 'Generate Report' or 'System Backup' buttons to export data and create backups."
                ]
            },
            "report": {
                "keywords": ["report", "analytics", "data", "insights"],
                "responses": [
                    "Generate comprehensive reports using the 'Generate Report' button in the Quick Actions section.",
                    "You can create detailed analytics reports about user activity, system performance, and platform usage.",
                    "Reports and analytics are available through the admin panel's reporting tools."
                ]
            },
            "settings": {
                "keywords": ["setting", "config", "admin", "panel"],
                "responses": [
                    "Admin settings and configuration options are available in the admin panel. You can manage system preferences and platform settings.",
                    "Access admin settings through the Quick Actions section or the main admin interface.",
                    "System configuration and admin settings can be managed from the admin panel."
                ]
            }
        }
        
        for category, data in admin_queries.items():
            if any(keyword in message for keyword in data["keywords"]):
                return random.choice(data["responses"])
        
        return None
    
    def _handle_general_queries(self, message: str) -> str:
        """Handle general user queries"""
        
        # Face Analysis Features
        if any(word in message for word in ["face", "detection", "recognition"]):
            if "detect" in message:
                return "Our Face Detection feature uses advanced AI to detect faces in images or video streams in real-time with high accuracy! 🎯"
            elif "recogn" in message:
                return "Face Recognition helps identify and verify people using state-of-the-art deep learning models. Perfect for security and authentication! 🔐"
            else:
                return "Our face analysis features include detection, recognition, emotion analysis, age/gender estimation, and driver monitoring! 🚀"
        
        # Technology & AI
        if any(word in message for word in ["ai", "technology", "deep learning", "neural", "model"]):
            return "We use cutting-edge AI technology including deep learning, computer vision, and edge computing for real-time face analysis! 🤖✨"
        
        # Pricing & Plans
        if any(word in message for word in ["price", "cost", "plan", "subscription", "billing"]):
            return "We offer flexible pricing: Free plan for basic features, Pro plan ($49/month) for advanced features, and Enterprise for custom solutions! 💰"
        
        # Demo & Trial
        if any(word in message for word in ["demo", "trial", "test", "try"]):
            return "Yes! You can try our features with the Free plan, or check out our live demo to see FaceAI in action! 🎮"
        
        # Integration & API
        if any(word in message for word in ["api", "integrat", "sdk", "develop", "code"]):
            return "We provide easy-to-use APIs and SDKs for web, mobile, and desktop integration. Perfect for developers! 💻"
        
        # Support & Help
        if any(word in message for word in ["help", "support", "contact", "assist"]):
            return "I'm here to help! You can also contact our support team through the Contact page, or check our FAQ section for common questions! 📞"
        
        # Features
        if any(word in message for word in ["feature", "capability", "function"]):
            return "Our features include: Face Detection, Recognition, Emotion Analysis, Age/Gender Estimation, Driver Monitoring, and Real-time Processing! 🎯"
        
        # Security & Privacy
        if any(word in message for word in ["security", "privacy", "safe", "protect"]):
            return "Your data security is our priority! We use encryption, on-device processing, and never store personal data. Privacy by design! 🔒"
        
        # Performance & Speed
        if any(word in message for word in ["speed", "fast", "performance", "real-time"]):
            return "Our AI delivers results in milliseconds! Perfect for real-time applications with edge computing capabilities! ⚡"
        
        # Use Cases
        if any(word in message for word in ["use case", "application", "industry", "business"]):
            return "FaceAI is used in security, retail, healthcare, automotive, and many other industries! Check our Use Cases page for examples! 🏢"
        
        # Company & Team
        if any(word in message for word in ["company", "team", "about", "who"]):
            return "We're a passionate team of AI researchers and engineers dedicated to building world-class face analysis solutions! 👥"
        
        # Newsletter & Updates
        if any(word in message for word in ["newsletter", "update", "news", "subscribe"]):
            return "Stay updated! Sign up for our newsletter at the bottom of the home page to get the latest AI news and product updates! 📧"
        
        # FAQ & Questions
        if any(word in message for word in ["faq", "question", "common"]):
            return "Check our FAQ section for common questions about features, pricing, integration, and more! 📋"
        
        # Partners & Trust
        if any(word in message for word in ["partner", "trust", "client", "customer"]):
            return "We're trusted by leading companies worldwide! See the Trusted By section on our home page for our partners! 🤝"
        
        # Technical Questions
        if any(word in message for word in ["technical", "spec", "requirement", "compatibility"]):
            return "Our platform is compatible with most devices and browsers. Check our documentation for technical specifications! 📱💻"
        
        # Account & Login
        if any(word in message for word in ["account", "login", "sign up", "register"]):
            return "Create your account using the Sign Up button! It's free and takes just a few seconds to get started! 🚀"
        
        # Error & Issues
        if any(word in message for word in ["error", "problem", "issue", "bug", "not working"]):
            return "Having issues? Try refreshing the page, or contact our support team for immediate assistance! 🔧"
        
        # Thanks & Goodbye
        if any(word in message for word in ["thank", "thanks", "appreciate"]):
            return "You're very welcome! 😊 Feel free to ask me anything else about FaceAI!"
        
        if any(word in message for word in ["bye", "goodbye", "see you", "later"]):
            return "Goodbye! Have a wonderful day! 👋 Come back anytime if you need help!"
        
        # Fallback responses
        fallback_responses = [
            "I'm here to help you with FaceAI! Ask me about our features, pricing, integration, or anything else! 😊",
            "Great question! I can help you with FaceAI features, pricing, technical questions, or general inquiries. What would you like to know? 🤔",
            "I'm your FaceAI assistant! I can help with features, pricing, integration, support, and more. Just let me know what you need! 💡",
            "Not sure about that, but I can definitely help you with FaceAI features, pricing, integration, or technical questions! 🚀",
            "Interesting question! While I focus on FaceAI-related topics, I can help you with features, pricing, integration, and support! 📚"
        ]
        
        return random.choice(fallback_responses)

# Global chatbot instance
chatbot = FaceAIChatbot()

def get_ai_response(user_message: str, user_name: str = None, user_role: str = None) -> str:
    """
    Main function to get AI response.
    
    Args:
        user_message: The user's input message
        user_name: Optional user name for personalization
        user_role: Optional user role (user/admin) for context-specific responses
    
    Returns:
        str: AI response
    """
    # Set user context if provided
    if user_name or user_role:
        chatbot.set_user_context(user_name, user_role)
    
    return chatbot.get_response(user_message) 