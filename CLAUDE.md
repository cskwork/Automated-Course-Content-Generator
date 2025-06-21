# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Automated Course Content Generator (ACCG) is a Streamlit-based AI application that helps educators and content creators generate comprehensive course content using OpenAI's GPT models. The application follows a multi-stage AI pipeline to create course outlines, detailed lessons, and quizzes.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run app.py
```

### Environment Configuration
Create a `.env` file in the root directory:

**For OpenAI:**
```
OPENAI_API_KEY=your_api_key_here
```

**For OpenRouter:**
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

**For both providers (optional):**
```
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Architecture Overview

### Core Application Flow
1. **User Input**: Course parameters (name, education level, difficulty, modules, etc.)
2. **AI Pipeline**: Multi-stage content generation using specialized prompts
3. **Content Assembly**: Structured course outline → detailed content → quizzes
4. **Export**: PDF generation for downloadable course materials

### Key Components

**Main Application** (`app.py`):
- Streamlit web interface with two-column layout
- Session state management for user interactions
- AI orchestration through OpenAI API calls or OpenRouter
- Multi-provider support (OpenAI, OpenRouter with various models)
- PDF generation using FPDF library

**Prompt Modules** (`prompts/`):
- `tabler_prompt.py`: Creates course outlines following Bloom's Taxonomy
- `dictator_prompt.py`: Converts outlines to structured Python dictionaries
- `quizzy_prompt.py`: Generates 30 MCQ questions per module
- `coursify_prompt.py`: (Unused) Originally for detailed lesson content

### AI Agent Workflow
The application uses specialized AI "agents" in sequence:
1. **Tabler**: Creates comprehensive course outlines
2. **DICTator**: Structures outlines as Python dictionaries
3. **Coursify**: Generates detailed lesson content (embedded in main logic)
4. **Quizzy**: Creates assessment questions

### Data Management
- **Session State**: Streamlit's built-in state management
- **Persistence**: Shelve database for chat history (`chat_history.bak`, `chat_history.dir`)
- **Configuration**: Custom Streamlit theme in `.streamlit/config.toml`

## Important Development Notes

### Prompt Engineering
- Each prompt module defines specific AI behavior and output formatting
- Prompts enforce strict structural requirements for consistent parsing
- Content generation follows educational best practices (Bloom's Taxonomy)

### State Management Patterns
- Heavy use of `st.session_state` for maintaining user flow
- Conditional UI rendering based on generation stages
- Progressive disclosure of content as it's generated

### Content Generation Pipeline
- Multi-stage approach prevents overwhelming single AI calls
- Each stage has specific validation and error handling
- Users can modify and regenerate content at each stage

### PDF Export Architecture
- FPDF library creates formatted downloadable content
- Base64 encoding enables in-browser downloads
- Structured content organization with lessons and quizzes

## Technology Stack
- **Python 3.x**: Core language
- **Streamlit**: Web framework and UI
- **OpenAI API / OpenRouter**: Multi-provider AI content generation
  - OpenAI: GPT-3.5-turbo, GPT-4, GPT-4-turbo
  - OpenRouter: Claude, Llama, Gemini, and other models
- **FPDF**: PDF creation and formatting
- **python-dotenv**: Environment variable management
- **shelve**: Local data persistence
- **requests**: HTTP client for API communications

## File Structure Context
```
├── app.py                 # Main Streamlit application
├── prompts/              # AI prompt modules
│   ├── tabler_prompt.py   # Course outline generation
│   ├── dictator_prompt.py # Structure conversion
│   └── quizzy_prompt.py   # Quiz generation
├── .streamlit/           # Streamlit configuration
│   └── config.toml       # UI theme settings
├── requirements.txt      # Python dependencies
└── venv/                # Virtual environment (not committed)
```

## Key Development Considerations

### Content Quality Assurance
- Bloom's Taxonomy integration ensures educational progression
- 30 questions per module maintain assessment consistency
- Multi-stage validation prevents content quality degradation

### User Experience Patterns
- Two-column layout separates input from output
- Progress indicators show generation status
- Expandable sections organize large amounts of content
- Clear action buttons guide user through workflow

### Error Handling
- API key validation and error messaging
- Content generation failure recovery
- User input validation and feedback

### Performance Considerations
- Efficient session state usage
- Structured API calls to minimize token usage
- Progressive content loading for better UX