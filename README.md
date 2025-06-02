# Data Scientist Agent
Our data scientist agent can do everything that a true data scientist can do as long as you write the correct prompt.

## setup environment
```bash
pip install --upgrade metagpt
pip install streamlit
cd MetaGPT
metagpt --init-config
```
## setop model api key
```bash
vim ~/.metagpt/config2.yaml
```
find something like 
```bash
llm:
  api_type: "openai"  # or azure / ollama / groq etc. Check LLMType for more options
  model: "gpt-4-turbo"  # or gpt-3.5-turbo
  base_url: "https://api.openai.com/v1"  # or forward url / other llm url
  api_key: "YOUR_API_KEY"
```
change the api_key into your own

## let's start 
Ensure working directory is root of the repository.

```bash
streamlit run app.py
```
