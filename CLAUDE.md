# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Automated Course Content Generator (ACCG) is a Streamlit-based AI application that helps educators and content creators generate comprehensive course content using OpenAI's GPT models. The application follows a multi-stage AI pipeline to create course outlines, detailed lessons, and quizzes. The application now supports multiple output formats including HTML, PPT-style slides, and PowerPoint presentations.

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

**For Unsplash (image generation):**

```
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

**For all providers (full setup):**

```
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

## Architecture Overview

### Core Application Flow

1. **User Input**: Course parameters (name, education level, difficulty, modules, etc.)
2. **AI Pipeline**: Multi-stage content generation using specialized prompts
3. **Image Integration**: Automatic educational image search and insertion via Unsplash API
4. **Content Assembly**: Structured course outline → detailed content → quizzes → images
5. **Export**: PDF generation for downloadable course materials

### Key Components

**Main Application** (`app.py`):

- Streamlit web interface with two-column layout
- Session state management for user interactions
- AI orchestration through OpenAI API calls or OpenRouter
- Multi-provider support (OpenAI, OpenRouter with various models)
- **Unsplash API integration for automatic educational image insertion**
- PDF generation using FPDF library

**Image Generation Features**:

- **Automatic Image Search**: Searches for relevant educational images based on content placeholders
- **Subject-Aware Queries**: Customizes image searches based on subject (English/Math)
- **Safe Content Filtering**: Uses Unsplash's content filter for educational appropriateness
- **Attribution Management**: Automatically includes proper photo credits per Unsplash guidelines
- **Fallback Handling**: Gracefully degrades to placeholders when images aren't available

**Prompt Modules** (`prompts/`):

- `tabler_prompt.py`: Creates course outlines following Bloom's Taxonomy
- `dictator_prompt.py`: Converts outlines to structured Python dictionaries
- `quizzy_prompt.py`: Generates 30 MCQ questions per module
- `coursify_prompt.py`: (Unused) Originally for detailed lesson content
- `elementary_english_prompt.py`: English-specific content generation
- `elementary_math_prompt.py`: Math-specific content generation
- `interactive_content_prompt.py`: Interactive activities generation
- `quiz_generator_prompt.py`: Quiz creation templates

### AI Agent Workflow

The application uses specialized AI "agents" in sequence:

1. **Tabler**: Creates comprehensive course outlines
2. **DICTator**: Structures outlines as Python dictionaries
3. **Coursify**: Generates detailed lesson content (embedded in main logic)
4. **Quizzy**: Creates assessment questions
5. **Image Generator**: Fetches relevant educational images from Unsplash

### Data Management

- **Session State**: Streamlit's built-in state management
- **Persistence**: Shelve database for chat history (`chat_history.bak`, `chat_history.dir`)
- **Configuration**: Custom Streamlit theme in `.streamlit/config.toml`

## Important Development Notes

### Prompt Engineering

- Each prompt module defines specific AI behavior and output formatting
- Prompts enforce strict structural requirements for consistent parsing
- Content generation follows educational best practices (Bloom's Taxonomy)
- Image placeholders use `[이미지: 설명]` format for automatic replacement

### State Management Patterns

- Heavy use of `st.session_state` for maintaining user flow
- Conditional UI rendering based on generation stages
- Progressive disclosure of content as it's generated

### Content Generation Pipeline

- Multi-stage approach prevents overwhelming single AI calls
- Each stage has specific validation and error handling
- Users can modify and regenerate content at each stage
- Images are fetched after content generation for optimal performance

### Image Integration Architecture

- **Placeholder Detection**: Regex pattern matching for `[이미지: description]` markers
- **Smart Search**: Educational keywords added based on subject context
- **Fallback Strategy**: Generic educational images when specific searches fail
- **Attribution**: Automatic credit generation following Unsplash guidelines
- **HTML Integration**: Responsive image containers with proper styling

### Multi-Format Export Architecture

- **PDF Export**: FPDF library creates formatted downloadable content with Base64 encoding for in-browser downloads
- **Slide Generation**: Interactive HTML slides with PPT-style navigation, keyboard controls, and responsive design
- **PowerPoint Export**: python-pptx library generates native PPTX files with proper formatting and structure
- **Mobile View**: Responsive mobile-optimized display for all content types

## Technology Stack

- **Python 3.x**: Core language
- **Streamlit**: Web framework and UI
- **OpenAI API / OpenRouter**: Multi-provider AI content generation
  - OpenAI: GPT-3.5-turbo, GPT-4, GPT-4-turbo
  - OpenRouter: Claude, Llama, Gemini, and other models
- **Unsplash API**: High-quality educational image sourcing
- **FPDF**: PDF creation and formatting
- **python-pptx**: PowerPoint presentation generation
- **python-dotenv**: Environment variable management
- **shelve**: Local data persistence
- **requests**: HTTP client for API communications

## File Structure Context

```
├── app.py                 # Main Streamlit application
├── src/                  # Source code directory
│   ├── config/           # Configuration modules
│   ├── models/           # Data models and types
│   ├── services/         # Business logic services
│   │   ├── ai_service.py      # AI content generation
│   │   ├── slide_generator.py # HTML slide generation
│   │   ├── ppt_generator.py   # PowerPoint generation
│   │   └── export_service.py  # Export functionality
│   ├── templates/        # HTML templates for slide generation
│   ├── ui/               # User interface components
│   └── utils/            # Utility functions
├── prompts/              # AI prompt modules
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
└── venv/                # Virtual environment (not committed)
```

## Key Development Considerations

### Content Quality Assurance

- Bloom's Taxonomy integration ensures educational progression
- 30 questions per module maintain assessment consistency
- Multi-stage validation prevents content quality degradation
- Educational image filtering ensures age-appropriate content

### User Experience Patterns

- Two-column layout separates input from output
- Progress indicators show generation status
- Expandable sections organize large amounts of content
- Clear action buttons guide user through workflow
- Visual content enhances learning engagement

### Error Handling

- API key validation and error messaging
- Content generation failure recovery
- User input validation and feedback
- Graceful image loading failures with placeholder retention

### Performance Considerations

- Efficient session state usage
- Structured API calls to minimize token usage
- Progressive content loading for better UX
- Asynchronous image loading where possible
