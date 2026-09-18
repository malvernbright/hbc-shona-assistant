from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
import os

app = FastAPI(
    title="Shona Heritage-Based Curriculum (HBC) Assistant API",
    version="1.0.0",
    description="Local RAG & Tutoring backend powered by Morena 1.5B Instruct and Vulkan acceleration."
)

# Define the path to your downloaded local GGUF model
# Update the filename if it differs slightly based on your 'hf download' output
MODEL_PATH = "./morena-1.5b-instruct-Q4_K_M.gguf"

if not os.path.exists(MODEL_PATH):
    # Fallback search for any gguf file in directory if name varies
    gguf_files = [f for f in os.listdir(".") if f.endswith(".gguf")]
    if gguf_files:
        MODEL_PATH = gguf_files[0]
    else:
        raise RuntimeError(f"Model file not found in directory. Please ensure the GGUF file is present.")

# Initialize the local LlamaCpp engine (leveraging Vulkan offload)
print(f"Loading local model from {MODEL_PATH}...")
llm = LlamaCpp(
    model_path=MODEL_PATH,
    temperature=0.3,
    max_tokens=512,
    n_ctx=2048,
    n_gpu_layers=99,  # Offloads all layers to your NVIDIA 950M via Vulkan
    verbose=False
)

# Define request schema using Pydantic
class StudentQueryRequest(BaseModel):
    query: str = Field(..., description="The student's question or prompt in Shona or English.")
    student_level: str = Field(..., description="Level: 'Primary', 'ZJC-O-Level', or 'A-Level'")
    project_stage: int = Field(..., ge=1, le=6, description="SBP Stage from 1 to 6")
    context: str = Field("", description="Retrieved curriculum document chunks from vector store.")

class AssistantResponse(BaseModel):
    response: str
    student_level: str
    project_stage: int

# HBC System Prompt Template
hbc_prompt_template = """Iwe uri mudzidzisi weChiShona akangwara anotevedzera bumbiro idzva reHeritage-Based Curriculum (HBC) muZimbabwe.

Level yeMudzidzi: {student_level}
SBP Stage: {project_stage} (1: Problem ID, 2: Investigation, 3: Idea Generation, 4: Development, 5: Presentation, 6: Evaluation)

Mitemo Yekutungamirira (Rules):
1. Kana mudzidzi ari paPrimary, shandisa mutauro wakajeka, wakareruka, uye unokurudzira.
2. Kana mudzidzi ari paSecondary kana A-Level, shandisa mutauro wakadzama, tsumo, nemadimikira akakodzera.
3. USAPE mudzidzi mhinduro yakakwana ye project. Mutungamirire kuti afunge uye aite tsvakiridzo oga (Guide them, don't do it for them).
4. Tsigira mhinduro yako neruzivo rwezvidzidzo izvi (Context): {context}

Mubvunzo wemudzidzi: {query}
Mhinduro:"""

prompt = PromptTemplate(
    input_variables=["student_level", "project_stage", "context", "query"],
    template=hbc_prompt_template
)

# Chain the prompt to the local LLM
chain = prompt | llm

@app.post("/api/v1/tutor", response_model=AssistantResponse)
def generate_tutor_response(payload: StudentQueryRequest):
    try:
        # Format and invoke the local model chain
        formatted_prompt = prompt.format(
            student_level=payload.student_level,
            project_stage=payload.project_stage,
            context=payload.context if payload.context else " Hapana ruzivo rwekunze rwakapihwa.",
            query=payload.query
        )
        
        raw_output = llm.invoke(formatted_prompt)
        
        # Clean up text output if needed
        clean_response = raw_output.strip()

        return AssistantResponse(
            response=clean_response,
            student_level=payload.student_level,
            project_stage=payload.project_stage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "online", "model": MODEL_PATH, "backend": "Vulkan/LlamaCpp"}