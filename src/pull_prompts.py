
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml,print_section_header

load_dotenv()
PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
    
def pull_prompts_from_langsmith():
    """Função para puxar prompts do LangSmith Hub"""

    # Puxa os prompts do LangSmith Hub
    print_section_header("Puxando prompts do LangSmith Hub...")

    # Cria o cliente do LangSmith
    client = Client()
   

    prompt = client.pull_prompt(PROMPT_NAME)
    formatted_prompt = format_prompt_content(prompt)
    
    # Salva cada prompt em um arquivo YAML separado
    OUTPUT_DIR = Path("prompts")
    prompt_name = PROMPT_NAME.split("/")[-1]
    output_file = OUTPUT_DIR / f"{prompt_name}.yml"    
    save_yaml(formatted_prompt, output_file)    
    print(f"Prompt '{PROMPT_NAME}' salvo em '{output_file}'.")


def main():
    """Função principal"""
    pull_prompts_from_langsmith()


def format_prompt_content(prompt):
    """Função para formatar o conteúdo do prompt"""
    
    # As mensagens já vêm separadas como System e Human/User
    system_prompt = prompt.messages[0].prompt.template
    user_prompt = prompt.messages[1].prompt.template

    prompt_yaml = {
        PROMPT_NAME: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": [
                "bug-analysis",
                "user-story",
                "product-management",
            ],
        }
    }    
    return prompt_yaml

if __name__ == "__main__":
    sys.exit(main())
