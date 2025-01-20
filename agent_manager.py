import time
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from streamlit import session_state

from fetch_seo_data import fetch_seo_data
from manage_email import send_email
from prompt import SYSTEM_PROMPT

# Define available actions
available_actions = {
    "fetch_seo_data": lambda user_input: fetch_seo_data(user_input, session_state=session_state,save_to_file=True),
    "send_email_summary": lambda user_input: send_email(user_input, session_state=session_state)
}


# Initialize tools once
tools = None  # Declare a global variable for tools

def get_tools():
    """
    Retrieves the tools, creating them only once.
    """
    global tools
    if tools is None:
        tools = []
        for action_name, action_func in available_actions.items():
            tools.append(
                Tool(
                    name=action_name,
                    func=action_func,
                    description=f"Action: {action_name}. Executes the corresponding functionality."
                )
            )
    return tools

# Creates and initializes a LangChain agent
def create_agent(api_key: str):
    start_time = time.time()
    llm = ChatOpenAI(temperature=0.8, openai_api_key=api_key,model="gpt-4o-mini")
    print(f"LLM initialization took {time.time() - start_time} seconds.")
       # Initialize memory with the system prompt as the first entry
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    memory.chat_memory.add_user_message(SYSTEM_PROMPT)
    memory.chat_memory.add_ai_message("ok")


    system_prompt = PromptTemplate(template=SYSTEM_PROMPT, input_variables=["chat_history"])

    return initialize_agent(
        tools=get_tools(),  # List of tools for the agent
        llm=llm,  # Language model used by the agent
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # Type of agent
        verbose=True,  # Enable detailed logs
        agent_kwargs={"system_prompt": system_prompt},  # Additional agent arguments
        memory=memory,  # Memory to track conversations
        tags=["SEO_Agent"],  # Tags for traced runs
        handle_parsing_errors=True,  # Handle errors in parsing
    )


# Retrieves an agent instance or creates one if it doesn't exist using session state
def get_agent_with_session(api_key, session_state):
    if session_state['agent'] is None:
        session_state['agent'] = create_agent(api_key)
    return session_state['agent']
