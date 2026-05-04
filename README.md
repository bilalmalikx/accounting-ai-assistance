# Accounting AI Assistant

## Local Setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull model
ollama pull llama3.2:3b

# 3. Install Python deps
pip install -r requirements.txt

# 4. Run
python run.py