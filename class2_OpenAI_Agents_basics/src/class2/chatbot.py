import chainlit as cl 
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent


load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
# print(gemini_api_key)

provider = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client= provider,
)

run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True,
)

agent: Agent = Agent(
    name= "Assistant",
    instructions= "You are a Python Programming expert and only respond to programming questions",   
    model= model
)

# result = Runner.run_sync(
#     input= "Explain recursion in two sentences to a 5th grader",
#     run_config= run_config,
#     starting_agent= agent
# )

# print(result.final_output)

# # Case1: In normal scenario with no streaming and message history
# @cl.on_message
# async def handle_message(message: cl.Message):
#     result = Runner.run_sync(
#         agent,
#         input = message.content,
#         run_config = run_config
#     )
#     await cl.Message(
#         content = result.final_output
#     ).send()
    
   
# # Case2: In streaming scenario with no message history 
# @cl.on_message
# async def handle_message(message: cl.Message):    
#     result = Runner.run_streamed(
#         agent,
#         input = message.content,
#         run_config = run_config
#     )

#     msg = cl.Message(content="")

#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             await msg.stream_token(event.data.delta)
    
   
# # Case3: In normal scenaio with message history but no streaming 

# @cl.on_chat_start
# async def handle_chat_start():
#     cl.user_session.set("history", [])
#     await cl.Message(
#         content = "Hello! I am Python Programming expert and I shall assist you with any questions related to programming. How may I help you?"
#     ).send()

# @cl.on_message
# async def handle_message(message: cl.Message):
#     history = cl.user_session.get("history")
    
#     history.append({
#         "role": "user",
#         "content": message.content
#     })
    
#     result = await Runner.run(
#         agent,
#         input = history,
#         run_config = run_config
#     )
    
#     history.append({
#         "role": "assistant",
#         "content": result.final_output
#     })
    
#     cl.user_session.set("history", history)
    
#     await cl.Message(
#         content = result.final_output
#     ).send()
        
    
# # Case4: In streaming scenario with message history

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content = "Hello! I am Python Programming expert and I shall assist you with any questions related to programming. How may I help you?"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    
    history.append({
        "role": "user",
        "content": message.content
    })
    
    result = Runner.run_streamed(
        agent,
        input = history,
        run_config = run_config
    )
    
    msg = cl.Message(content="")

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    
    
    history.append({
        "role": "assistant",
        "content": result.final_output
    })
    
    cl.user_session.set("history", history)
    
    