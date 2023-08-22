import openai
import os
import platform
import sys
from colorama import Fore, init

openai.api_key = os.environ.get('OPENAI_API_KEY')
init(autoreset=True)

def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def choose_prompt(prompts):
    print("Would you like to use one of the default prompts, or enter your own?")
    choice = input("Enter 'd' for default, 'c' for custom: ").lower()
    if choice == 'c':
        return input("Enter your custom prompt: ")
    elif choice == 'd':
        return display_system_prompts(prompts)
    else:
        print("Invalid choice, defaulting to first system prompt.")
        return prompts[0]

def display_system_prompts(prompts):
    print("Select a system prompt:")
    for idx, prompt in enumerate(prompts, 1):
        print(f"{idx}. {prompt}")
    choice = int(input("\nEnter your choice (number): "))
    return prompts[choice - 1]

def estimate_tokens(conversation):
    return sum(len(message["content"].split()) + sum(c in ',.?!:;' for c in message["content"]) for message in conversation)

def stream_gpt(prompt, conversation):
    conversation.append({"role": "user", "content": prompt})
    token_count = estimate_tokens(conversation)
    print(f"{Fore.RED}Tokens used: {token_count}/4096\n")

    if token_count >= 4090:
        print(f"{Fore.YELLOW}Warning: Approaching token limit. The conversation may end soon.\n")

    r = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    response_text = r["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": response_text})
    token_count = estimate_tokens(conversation)
    print(response_text)
    print(f"{Fore.RED}Tokens used after response: {token_count}/4096\n")

    return conversation

system_prompts = [
    "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.",
    "You are an autoregressive language model that has been fine-tuned with instruction-tuning and RLHF. You carefully provide accurate, factual, thoughtful, nuanced answers, and are brilliant at reasoning. If you think there might not be a correct answer, you say so.",
]

if len(sys.argv) < 2:
    clear_screen()
    selected_prompt = choose_prompt(system_prompts)
    conversation = [{"role": "system", "content": selected_prompt}]
    print(f"{Fore.BLUE}Type 'exit' to quit conversation.{Fore.RESET}")

    continuation_prompt = "How can I help:"
    continuation_prompt_color = Fore.GREEN  # Always green for both prompts

    while True:
        prompt = input(f"{continuation_prompt_color}{continuation_prompt}{Fore.YELLOW} ")  # User text color is Fore.MAGENTA
        if prompt.lower() in ['exit', 'quit']:
            break

        conversation = stream_gpt(prompt, conversation)
        continuation_prompt = "What else do you need?"

else:
    prompt = ' '.join(sys.argv[1:])
    conversation = [{"role": "system", "content": prompt}, {"role": "user", "content": prompt}]
    response = stream_gpt(prompt, conversation)
    print("\n" + response + "\n")