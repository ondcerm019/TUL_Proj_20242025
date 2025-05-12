"""This module defines constants."""

TAGS = {
    "PERSONAL_NAME": "pn",
    "INSTITUTION": "i",
    "COMPANY": "c",
    "LOCATION": "l",
    "DATE": "d",
    "ZIPCODE": "z",
    "PHONE": "p",
    "EMAIL": "e",
    "CASE_NUMBER": "cj",
    "ACT": "a",
    "WEB": "w",
    "MONEY": "m"
}

OMITTED_TAGS = [
    TAGS["DATE"],
    TAGS["ACT"],
    TAGS["MONEY"]
]



# "LLama 3.3 70b" # Currently not using OpenRouter
# "LLama 4 Scout"
# "LLama 4 Maverick"
# "Deepseek R1 distill Qwen 32b"
# "Deepseek V3 0324"
# "Gemini 2.5 Pro Experimental"
# "Gemini 2.5 Flash"

# "Mistral Small 3.1 24b"
# "Gemma 3 27b"
# "Phi 4"

# "Groq LLama 3.3 70b" # Currently just "LLama 3.3 70b" even in GROQ_MODELS
# "Groq LLama 4 Scout"
# "Groq LLama 4 Maverick"


# -----------------------------------------------------------------------

CHOSEN_MODEL = "LLama 3.3 70b"
TEMPERATURE = 0.4 # 0.4 # 1.0

TEXT_CHUNK_WORD_OVERLAP_TOL = 4

# -----------------------------------------------------------------------

OUTPUT_LOGS_FOLDER = r"" # <Cesta ke složce pro ukládání výstupních dat a logů>

LOGS_CATEGORY_WORDS = "category_words"
LOGS_CHANGES = "changes.txt"
LOGS_LATEST_POS = "latest_position.txt"
MAIN_OUTPUT = "main_output.txt"



# MODELS = {
#     "LLama 3.3 70b": ,
#     "LLama 4 Scout": ,
#     "LLama 4 Maverick": ,
#     "Deepseek R1 distill LLama 70b": ,
#     "Deepseek R1 distill Qwen 32b": ,
#     "Deepseek R1": ,
#     "Deepseek V3 0324": ,
#     "Gemini 2.5 Pro Experimental": ,
#     "Gemini 2.5 Flash": ,

#     "Mistral Small 3.1 24b": ,
#     "Gemma 3 27b": ,
#     "Phi 4": ,

#     "Groq LLama 3.3 70b": ,
#     "Groq LLama 4 Scout": ,
#     "Groq LLama 4 Maverick": ,
#     "Groq Deepseek R1 distill LLama 70b": ,
# }



GROQ_MODELS = {
    "LLama 3.3 70b": "llama-3.3-70b-versatile",
    #"Groq LLama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    #"Groq LLama 4 Maverick": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "Groq Deepseek R1 distill LLama 70b": "deepseek-r1-distill-llama-70b",
}
CHOSEN_GROQ_MODEL = GROQ_MODELS.get(CHOSEN_MODEL, None)
GROQ_API = {
    "keys": [
        # <API klíč pro platformu Groq>
    ],
    "model": CHOSEN_GROQ_MODEL,
    "base_url": "https://api.groq.com/openai/v1"
}


OPENROUTER_MODELS = {
    "LLama 3.3 70b": "meta-llama/llama-3.3-70b-instruct:free",
    #"LLama 4 Scout": "meta-llama/llama-4-scout:free",
    #"LLama 4 Maverick": "meta-llama/llama-4-maverick:free",
    "Deepseek R1 distill LLama 70b": "deepseek/deepseek-r1-distill-llama-70b:free",
    "Deepseek R1 distill Qwen 32b": "deepseek/deepseek-r1-distill-qwen-32b:free",
    "Deepseek R1": "deepseek/deepseek-r1:free",
    "Deepseek V3 0324": "deepseek/deepseek-chat-v3-0324:free",
    "Mistral Small 3.1 24b": "mistralai/mistral-small-3.1-24b-instruct",
    "Gemma 3 27b": "google/gemma-3-27b-it",
    "Phi 4": "microsoft/phi-4"
}
CHOSEN_OPENROUTER_MODEL = OPENROUTER_MODELS.get(CHOSEN_MODEL, None)
OPENROUTER_API = {
    "keys": [
        # <API klíč pro platformu OpenRouter>
    ],
    "model": CHOSEN_OPENROUTER_MODEL,
    "base_url": "https://openrouter.ai/api/v1"
}


FIREWORKS_MODELS = {
    "LLama 3.3 70b": "accounts/fireworks/models/llama-v3p3-70b-instruct",
    #"LLama 4 Scout": "accounts/fireworks/models/llama4-scout-instruct-basic",
    #"LLama 4 Maverick": "accounts/fireworks/models/llama4-maverick-instruct-basic",
    "Deepseek R1": "accounts/fireworks/models/deepseek-r1-basic",
    "Deepseek V3 0324": "accounts/fireworks/models/deepseek-v3-0324"
}
CHOSEN_FIREWORKS_MODEL = FIREWORKS_MODELS.get(CHOSEN_MODEL, None)
FIREWORKS_API = {
    "keys": [
        # <API klíč pro platformu Fireworks AI>
    ],
    "model": CHOSEN_FIREWORKS_MODEL,
    "base_url": "https://api.fireworks.ai/inference/v1"
}


TOGETHER_MODELS = {
    "LLama 3.3 70b": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    #"LLama 4 Scout": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    #"LLama 4 Maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "Deepseek R1 distill LLama 70b": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    "Deepseek R1": "deepseek-ai/DeepSeek-R1",
    "Deepseek V3 0324": "deepseek-ai/DeepSeek-V3"
}
CHOSEN_TOGETHER_MODEL = TOGETHER_MODELS.get(CHOSEN_MODEL, None)
TOGETHER_API = {
    "keys": [
        # <API klíč pro platformu Together AI>
    ],
    "model": CHOSEN_TOGETHER_MODEL,
    "base_url": "https://api.together.xyz/v1"
}


SAMBANOVA_MODELS = {
    "LLama 3.3 70b": "Meta-Llama-3.3-70B-Instruct",
    #"LLama 4 Scout": "Llama-4-Scout-17B-16E-Instruct",
    #"LLama 4 Maverick": "Llama-4-Maverick-17B-128E-Instruct",
    "Deepseek R1 distill LLama 70b": "DeepSeek-R1-Distill-Llama-70B",
    "Deepseek R1": "DeepSeek-R1",
    "Deepseek V3 0324": "DeepSeek-V3-0324"
}
CHOSEN_SAMBANOVA_MODEL = SAMBANOVA_MODELS.get(CHOSEN_MODEL, None)
SAMBANOVA_API = {
    "keys": [
        # <API klíč pro platformu SambaNova>
    ],
    "model": CHOSEN_SAMBANOVA_MODEL,
    "base_url": "https://api.sambanova.ai/v1"
}


GOOGLE_AI_STUDIO_MODELS = {
    "Gemini 2.5 Pro Experimental": "gemini-2.5-pro-exp-03-25",
    "Gemini 2.5 Flash": "models/gemini-2.5-flash-preview-04-17"
}
CHOSEN_GOOGLE_AI_STUDIO_MODEL = GOOGLE_AI_STUDIO_MODELS.get(CHOSEN_MODEL, None)
GOOGLE_AI_STUDIO_API = {
    "keys": [
        # <API klíč pro platformu Google AI Studio>
    ],
    "model": CHOSEN_GOOGLE_AI_STUDIO_MODEL,
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"
}


METACENTRUM_MODELS = {
    "LLama 3.3 70b": "llama3.3:latest",
    #"LLama 4 Scout": "llama-4-scout-17b-16e-instruct",
    "Deepseek R1 distill Qwen 32b": "deepseek-r1:32b-qwen-distill-fp16",
    "Mistral Small 3.1 24b": "mistral-small3.1:24b-instruct-2503-q8_0",
    "Gemma 3 27b": "gemma3:27b-it-fp16",
    "Phi 4": "phi4:14b-q8_0"
}
CHOSEN_METACENTRUM_MODEL = METACENTRUM_MODELS.get(CHOSEN_MODEL, None)
METACENTRUM_API = {
    "keys": [
        # <API klíč pro platformu Open WebUI e-infra.cz>
    ],
    "model": CHOSEN_METACENTRUM_MODEL,
    "base_url": "https://chat.ai.e-infra.cz/api"
}





API_INFO_TEMP = \
    [GROQ_API, OPENROUTER_API, TOGETHER_API, FIREWORKS_API, \
     SAMBANOVA_API, GOOGLE_AI_STUDIO_API, METACENTRUM_API ]

API_INFO = []

for ai in API_INFO_TEMP:
    if ai.get("model"):
        API_INFO.append(ai)
