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

# Install core dependencies
pip install -r requirements.txt

# For GPU-accelerated Stable Diffusion (optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Performance optimization (optional, Windows may have build issues)
pip install xformers --index-url https://download.pytorch.org/whl/cu121
```

### Cross-Platform Installation

```bash
# Windows automated setup
install_and_run.bat

# Environment reset (Windows)
recreate_venv.bat

# Debug UI components
python debug_selectbox.py
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

# Stable Diffusion Configuration
USE_STABLE_DIFFUSION=true

# Ollama Configuration (local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=gemma3:latest

# Provider Selection
MODEL_SELECTION=openai  # or openrouter, ollama
OPENROUTER_DEFAULT_MODEL=openai/gpt-4
```

## Architecture Overview

### Core Application Flow

1. **User Input**: Course parameters (name, education level, difficulty, modules, etc.)
2. **AI Pipeline**: Multi-stage content generation using specialized prompts (OpenAI/OpenRouter/Ollama)
3. **Image Integration**: Dual system - Unsplash API search OR local Stable Diffusion generation
4. **Content Assembly**: Structured course outline → detailed content → quizzes → images
5. **Export**: Multi-format export (PDF, HTML slides, PowerPoint presentations)

### Key Components

**Main Application** (`app.py`):

- Streamlit web interface with two-column layout
- Session state management for user interactions
- Multi-provider AI orchestration (OpenAI, OpenRouter, Ollama)
- **Dual Image Generation System**: Unsplash API + Local Stable Diffusion
- Multi-format export (PDF, HTML slides, PowerPoint)

**Dual Image Generation System**:

- **Unsplash Integration**: Professional educational image search with attribution
- **Stable Diffusion**: Local AI image generation with educational optimization
- **Model Support**: SDXL, SD v2.1, SD v1.5, SDXL Turbo for different use cases
- **Subject-Aware Prompts**: Customized generation for math, English, science, history
- **Performance Tiers**: Fast (4 steps), Default (25 steps), High Quality (50 steps)
- **Safety Filters**: Child-safe content with educational focus
- **GPU/CPU Support**: Automatic device detection with memory optimization
- **Seamless Switching**: Users can toggle between Unsplash and Stable Diffusion

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
5. **Image Generator**: Dual system - Unsplash search OR Stable Diffusion generation

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

### Dual Image Generation Architecture

- **Placeholder Detection**: Regex pattern matching for `[이미지: description]` markers
- **Provider Selection**: Users can switch between Unsplash API and Stable Diffusion
- **Unsplash Integration**: Smart search with educational keywords and safe content filtering
- **Stable Diffusion Pipeline**: Local generation with subject-specific prompts and safety filters
- **Model Management**: Automatic model loading with GPU/CPU optimization and memory management
- **Fallback Strategy**: Graceful degradation from SD to Unsplash to placeholders
- **Attribution System**: Automatic crediting for both Unsplash photos and AI-generated images

### Multi-Format Export Architecture

- **PDF Export**: FPDF library creates formatted downloadable content with Base64 encoding for in-browser downloads
- **Slide Generation**: Interactive HTML slides with PPT-style navigation, keyboard controls, and responsive design
- **PowerPoint Export**: python-pptx library generates native PPTX files with proper formatting and structure
- **Mobile View**: Responsive mobile-optimized display for all content types

## Technology Stack

- **Python 3.12+**: Core language
- **Streamlit**: Web framework and UI
- **Multi-Provider AI**: OpenAI API, OpenRouter, Ollama
  - OpenAI: GPT-3.5-turbo, GPT-4, GPT-4-turbo
  - OpenRouter: Claude, Llama, Gemini, and other models
  - Ollama: Local LLM inference
- **Dual Image Generation**:
  - **Unsplash API**: Professional educational image sourcing
  - **Stable Diffusion**: Local AI image generation (torch, diffusers, transformers)
- **Export Libraries**: FPDF (PDF), python-pptx (PowerPoint), markdown2 (enhanced processing)
- **ML Stack**: PyTorch 2.2+, diffusers 0.25+, transformers 4.30+, accelerate, Pillow
- **Utilities**: python-dotenv, shelve, requests, xformers (optional optimization)

## File Structure Context

```
├── app.py                 # Main Streamlit application
├── src/                  # Source code directory
│   ├── config/           # Configuration modules
│   ├── models/           # Data models and types
│   ├── services/         # Business logic services
│   │   ├── ai_service.py      # Multi-provider AI content generation
│   │   ├── image_service.py   # Dual image generation orchestration
│   │   ├── slide_generator.py # HTML slide generation
│   │   ├── ppt_generator.py   # PowerPoint generation
│   │   └── export_service.py  # Multi-format export functionality
│   ├── module/           # Core modules
│   │   └── generate_image/    # Complete Stable Diffusion module
│   │       ├── config.py           # Model configurations and settings
│   │       ├── stable_diffusion_generator.py  # Main generator class
│   │       └── usage_example.py   # Implementation examples
│   ├── templates/        # HTML templates for slide generation
│   ├── ui/               # User interface components
│   └── utils/            # Utility functions
├── prompts/              # AI prompt modules
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
├── constraints.txt       # Package exclusions (PyPDF conflicts)
├── install_and_run.bat   # Windows automated setup
├── recreate_venv.bat     # Environment reset script
├── debug_selectbox.py    # UI debugging tool
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
- Structured AI API calls to minimize token usage
- Progressive content loading for better UX
- GPU memory management for Stable Diffusion
- Model caching and attention optimization
- Graceful fallback between image providers

## Important Development Workflows

### Image Generation Provider Selection

The application supports dual image generation modes:

```python
# Switch to Stable Diffusion
image_service.set_image_source(use_stable_diffusion=True)

# Switch to Unsplash API  
image_service.set_image_source(use_stable_diffusion=False)
```

### Stable Diffusion Model Configuration

Available models in `src/module/generate_image/config.py`:
- **SDXL** (default): High resolution, best quality
- **SDXL Turbo**: Fast generation (4 steps)
- **SD v2.1**: Improved stability 
- **SD v1.5**: Compatibility mode

### Multi-Provider AI Setup

The application can use multiple AI providers:
1. **OpenAI**: Direct API integration
2. **OpenRouter**: Access to Claude, Llama, Gemini via unified API
3. **Ollama**: Local LLM inference for privacy

### Package Conflict Resolution

The `constraints.txt` file prevents PyPDF conflicts:
```bash
# If PDF export fails, clean conflicting packages
pip uninstall --yes pypdf PyPDF2 pyfpdf
pip install --upgrade fpdf2
```
