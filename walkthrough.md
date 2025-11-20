# Research Agent Project - Walkthrough

## Overview
I have restructured the project into a single Django application that serves the Vue.js frontend.
- **Single Container**: Django + Node.js (for build) in one Docker container.
- **Port**: 8009 (mapped to 8009 internally).
- **Structure**:
    - `research_agent/`: Django project root.
    - `research_agent/research_agent`: Django settings & config.
    - `research_agent/web_app`: Django app (serves frontend).
    - `research_agent/frontend`: Vue.js source code.
    - `research_agent/web_app/templates/web_app`: Compiled HTML.
    - `research_agent/web_app/static/web_app`: Compiled assets.

## How to Run
1. Open a terminal in the project root.
2. Run the following command to build and start the container:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - **App**: [http://localhost:8009](http://localhost:8009)

## Features Implemented
### 3-Column Layout (Light Theme)
- **Left Sidebar**: Conversation history (collapsible via hamburger menu).
- **Center**: Chat interface with "Add to sources" functionality.
- **Right Sidebar**: Source management (resizable width).

### Interactive Elements
- **Sidebar Toggle**: Click the hamburger menu in the top left to show/hide the conversation history.
- **Resize Sources**: Drag the divider between the chat and sources panel to adjust the width.
- **Add Source**: Clicking "Add Source" in the chat adds a new item to the right sidebar.
- **Expand Summary**: Click "Summary" on a source to view the abstract.
- **Context Toggle**: Toggle whether a source is included in the LLM context.

## Next Steps
- Connect the frontend to the Django backend.
- Implement actual OpenAI integration.
- Build the database models for Sources and Conversations.
