# YANA (Your ASL Native Assistant)

YANA is an AI-powered American Sign Language (ASL) assistant that combines real-time ASL detection with conversational AI capabilities. Developed as part of the FRI AI Research class, YANA aims to bridge communication gaps by translating ASL gestures into text and enabling natural conversations through AI.

# Features

- **Real-time ASL detection** using computer vision
- **Natural language conversation** through AI integration
- **Hand landmark tracking** for precise gesture recognition
- **Support for ASL alphabet (A-Z)**
- **Interactive testing modes** for both ASL and keyboard input

# Setup Instructions

1. **Get the Project Files:**
   - Download the project files from the shared Google Drive
   - Extract the files to your desired location
   - **IMPORTANT:** The provided `app.py` contains an API key for spare use. If you intend to use this program often, you will need to replace it with your own.

2. **Create and Activate Virtual Environment for Mac (If you haven't done so):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set Up OpenAI API (Required for AI conversation):**
   - Create an account at https://platform.openai.com/
   - Get your API key from the dashboard
   - Add credits to your account (starts with $5 free credit)
   - Open `app.py` and replace the placeholder API key with your own:
     ```python
     client = OpenAI(api_key="your-api-key-here")
     ```
   - **IMPORTANT:** Never share your API key or commit it to version control

5. **Run the Application:**
```bash
python app.py
```

# Usage

The application has two main modes:

1. **ASL Detection Mode:**
   - Press 'r' to record a gesture
   - Make ASL signs with your hand
   - Press 's' to send the detected letters
   - The AI will respond to your message

2. **Keyboard Testing Mode:**
   - Press 't' to type a message directly
   - The AI will respond to your input

**Key Controls:**
- Space: Add space to your message
- C: Clear current message
- S: Send message to AI
- T: Type message using keyboard
- ESC: Exit application

# Model Training

If you wish to train the ASL detection model on your own dataset:

1. **Collect Training Data:**
   - Press 'k' to enter manual keypoint logging mode
   - Press A-Z to record hand positions for each letter
   - Data will be saved to `model/keypoint_classifier/keypoint.csv`

2. **Train the Model:**
   - Open `keypoint_classification.ipynb`
   - Run all cells to train the model
   - The trained model will be saved automatically

# Contributors

- Allen Fertidos
- Mert Kanibir
- Jordan Lee
- Eldho Thomas
- Jonathan Zhang

# License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

# Acknowledgments

This project builds upon the ASL Detection framework by Akram ADRANE et al. and integrates modern AI conversation capabilities. Special thanks to the FRI IASA Research class for guidance and support.
