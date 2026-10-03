"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print(f"Prompt inválido: {prompt_name}")
        for error in errors:
            print(f"   - {error}")
        return False

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ])
        techniques = prompt_data.get("techniques_applied", [])
        prompt.metadata = {
            "version": prompt_data["version"],
            "techniques_applied": techniques,
        }
        tags = list(dict.fromkeys(prompt_data.get("tags", []) + techniques))
        readme = f"{prompt_data['description']}\n\nVersão: {prompt_data['version']}"
        if techniques:
            readme += "\n\nTécnicas aplicadas:\n" + "\n".join(
                f"- {technique}" for technique in techniques
            )
        url = hub.push(
            prompt_name,
            prompt,
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=os.getenv("LANGSMITH_ENDPOINT"),
            new_repo_is_public=True,
            new_repo_description=prompt_data["description"],
            readme=readme,
            tags=tags,
        )
        print(f"Prompt publicado: {prompt_name}\n   {url}")
        return True
    except Exception as error:
        print(f"Erro ao publicar '{prompt_name}': {error}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    if not isinstance(prompt_data, dict):
        return False, ["Os dados do prompt devem ser um mapeamento YAML."]

    errors = []
    for field in ("description", "system_prompt", "user_prompt", "version"):
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Campo '{field}' deve ser um texto não vazio.")

    for field in ("tags", "techniques_applied"):
        value = prompt_data.get(field, [])
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            errors.append(f"Campo '{field}' deve ser uma lista de textos não vazios.")

    for field in ("system_prompt", "user_prompt"):
        value = prompt_data.get(field)
        if isinstance(value, str) and "TODO" in value:
            errors.append(f"Campo '{field}' ainda contém TODOs.")

    if not errors:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_data["system_prompt"]),
                ("human", prompt_data["user_prompt"]),
            ])
            if set(prompt.input_variables) != {"bug_report"}:
                errors.append("O template deve usar somente a variável {bug_report}.")
        except (ValueError, TypeError) as error:
            errors.append(f"Template inválido: {error}")

    return not errors, errors


def main():
    """Função principal"""
    print_section_header("PUBLICAÇÃO DE PROMPTS NO LANGSMITH HUB")
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.environ["USERNAME_LANGSMITH_HUB"].strip()
    if not username or any(char in username for char in "/:@") or any(char.isspace() for char in username):
        print("USERNAME_LANGSMITH_HUB deve conter o identificador público (handle) do Hub.")
        print("O e-mail usado para entrar no LangSmith não é esse identificador.")
        print("Acesse https://smith.langchain.com/prompts e inicie a criação de um prompt público")
        print("para cadastrar seu handle, caso ainda não tenha um.")
        print("Depois configure no .env: USERNAME_LANGSMITH_HUB=seu_handle_cadastrado")
        return 1

    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    prompts = load_yaml(str(prompt_path))
    if not isinstance(prompts, dict) or not prompts:
        print("O arquivo deve conter um mapeamento não vazio de prompts.")
        return 1

    # Validar tudo antes de iniciar qualquer publicação.
    valid = True
    for name, data in prompts.items():
        is_valid, errors = validate_prompt(data)
        if not isinstance(name, str) or name.split("/")[-1] != "bug_to_user_story_v2":
            errors.append("O nome do prompt deve terminar em 'bug_to_user_story_v2'.")
        if isinstance(data, dict) and data.get("version") != "v2":
            errors.append("O campo 'version' deve ser 'v2'.")
        if not is_valid or errors:
            valid = False
            print(f"Prompt inválido: {name}")
            for error in errors:
                print(f"   - {error}")
    if not valid:
        return 1
    if len(prompts) != 1:
        print("O arquivo deve conter apenas um prompt bug_to_user_story_v2.")
        return 1

    destination = f"{username}/bug_to_user_story_v2"
    print(f"Destino público: {destination}")
    success = push_prompt_to_langsmith(destination, next(iter(prompts.values())))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
