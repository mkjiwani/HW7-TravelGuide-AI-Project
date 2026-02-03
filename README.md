# HW7-TravelGuide-AI-Project
A Streamlit-based AI Travel Planner using OpenAI and ReportLab
Author: Khalid Jiwani

**Purpose**
Planning a trip often involves hours of manual research across multiple websites to balance interests, logistics, and physical constraints. This project solves that problem by providing an automated, AI-powered concierge service.

**Relation to AI & AI-Assisted Workflows**

This application is a prime example of an AI-assisted workflow. It leverages Large Language Models (LLMs) to:
•	Synthesize Information: It processes natural language inputs (interests and constraints) to generate a cohesive, multi-day plan.
•	Contextual Reasoning: The AI acts as a "Travel Planner," applying logic to ensure that "guardrails" (e.g., wheelchair accessibility or dietary needs) are strictly followed throughout the itinerary.
•	Automated Content Transformation: It converts unstructured user preferences into structured Markdown and professional PDF documents.

**What the Code Does**

The application is built using Streamlit and the OpenAI API. High-level logic includes:
•	User Input Interface: Collects destination, duration, interests, and specific "guardrails" (preferences/constraints).
•	Intelligent Prompt Engineering: Constructs a detailed system and user prompt to guide the AI in generating a structured, five-section itinerary.
•	Robust AI Integration: Features a fallback model mechanism. If the primary model (GPT-4o) is unavailable, the script automatically attempts to use GPT-4-Turbo or GPT-3.5-Turbo to ensure service continuity.
•	Document Generation: Uses the reportlab library to parse the AI's Markdown output and generate a downloadable, formatted PDF itinerary for the user.

**How to Run or Use**

To run this project locally, follow these steps:
1.	Install Dependencies: Ensure you have Python installed, then run:
2.	pip install streamlit openai python-dotenv reportlab
3.	Set Up Environment Variables: Create a file named .env in the root directory and add your OpenAI API key:
4.	OPENAI_API_KEY=your_api_key_here
5.	Launch the App: Run the following command in your terminal:
6.	streamlit run travel_planner.py
7.	Generate a Plan: Enter your travel details in the web interface and click "Generate Travel Plan". Once finished, you can download the itinerary as a PDF.

**Security & Safe Sharing**
IMPORTANT: To maintain security and protect sensitive information:
•	No API Keys: The OPENAI_API_KEY is managed via a .env file which is not included in this repository.
•	Gitignore: A .gitignore file should be used to ensure .env and other local configuration files are never uploaded to GitHub.
•	No Private Data: This script does not store or transmit personal user data beyond the session requirements for the OpenAI API.

