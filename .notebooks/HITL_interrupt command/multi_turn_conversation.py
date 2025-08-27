from langgraph.graph import add_messages, StateGraph, START
from langgraph.types import Command, interrupt
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant")

class State(TypedDict):
    linkedin_topic: str
    generated_post: Annotated[List[str], add_messages]
    human_feedback: Annotated[List[str], add_messages]
    
def model(state: State):
    "Here , we're using the LLM to generate linkedin post with human feedback incorporated"
    
    print("[model] Generating Content...")
    linkedin_topic = state["linkedin_topic"]
    feedback = state["human_feedback"] if "human_feedback" in state else ["No feedback yet"]
    
    prompt = f"""
        LinkedIn Topic: {linkedin_topic}
        Human Feedback: {feedback[-1] if feedback else "No feedback yet"}

        Generate a structured and well-written LinkedIn post based on the given topic.
        Consider previous human feedback to refine the reponse.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are an expert LinkedIn content creator"),
        HumanMessage(content=prompt)
    ])
    
    generated_linkedin_post = response.content
    print(f"[model_node] Generated post: \n {generated_linkedin_post} \n")
    
    return {
        "generated_post": [AIMessage(content=generated_linkedin_post)],
        "human_feedback": feedback
    }
    
def human_node(state: State):
    """Human intervention node: Loop back to model unless input is done."""
    
    generated_post = state["generated_post"]
    user_feedback = interrupt(
        {
            "generated_post": generated_post,
            "message": "Provide feedback or type 'done' to finish"
        }
    )
    print(f"[human_node] Recieved human feedback: {user_feedback}")
    
    if user_feedback.lower() == "done":
        return Command(
            update={
                "human_feedback": state["human_feedback"] + ["Finalised"]
            },
            goto="end_node"
        )
        
    return Command(
            update={
                "human_feedback": state["human_feedback"] + [user_feedback]
            },
            goto="model"
        )
    
def end_node(state: State): 
    """Final Node"""
    print("\n [end_node] Process finished")
    print("Final Generated Post: ", state["generated_post"][-1])
    print("Final Human feedback: ", state["human_feedback"][-1])
    return {
        "generated_post": state["generated_post"],
        "human_feedback": state["human_feedback"],
    }
    
graph = StateGraph(State)
graph.add_node("model", model)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("model")
graph.add_edge(START, "model")
graph.add_edge("model", "human_node")
graph.set_finish_point("end_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
app.get_graph().print_ascii()

configs = {
    "configurable": {
        "thread_id": uuid.uuid4()
        }   
    }

linkedin_topic = input("Enter your linkedin topic:")

initial_state = {
    "linkedin_topic": linkedin_topic,
    "generated_post": [],
    "human_feedback": []
}

## Change in production -> Use websockets to have human feedback event based.
for chunk in app.stream(initial_state, config=configs):
    for node_id, value in chunk.items():
        ###### If we reach an interrupt, continuously ask human feedback #####
        if node_id == "__interrupt__":
            while True:
                user_feedback = input("Provide feedback (or type 'done' when finished): ")
                app.invoke(Command(resume=user_feedback), config=configs)
                if user_feedback.lower() == 'done':
                    break
                

