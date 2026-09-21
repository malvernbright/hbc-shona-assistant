from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = str(BASE_DIR / "morena-1.5b-instruct-Q4_K_M.gguf")
DB_DIR = str(BASE_DIR / "chroma_db")

app = FastAPI(title="Shona HBC Assistant API")

print("Loading Embedding Model & Vector Store...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # Retrieve top 2 most relevant chunks

print("Loading Morena 1.5B Model...")
llm = LlamaCpp(
    model_path=MODEL_PATH,
    temperature=0.3,
    max_tokens=350,
    n_ctx=1024,
    n_gpu_layers=12,
    verbose=False
)

class StudentQueryRequest(BaseModel):
    query: str
    student_level: str
    project_stage: int

# Updated prompt to explicitly instruct the model to use the RAG context as a template
hbc_prompt_template = """Iwe uri mudzidzisi weChiShona anotevedzera bumbiro reHeritage-Based Curriculum.
Pazasi pane muenzaniso weprojekiti yakaitwa zvakanaka (Context) yekubatsira mudzidzi.

Level yeMudzidzi: {student_level}
SBP Stage Inodiwa: Stage {project_stage}

Muenzaniso weProjekiti (Context):
{context}

Mitemo:
1. Shandisa muenzaniso uyu kuratidza mudzidzi magadzirirwo eprojekiti yake, asi usamupe mhinduro yekopa.
2. Kana ari paPrimary (Giredhi 6/7), shandisa mutauro uri nyore.
3. Kana ari paSecondary, shandisa mutauro wakadzama.

Mubvunzo wemudzidzi: {query}
Mhinduro Yako:"""

prompt = PromptTemplate(
    input_variables=["student_level", "project_stage", "context", "query"],
    template=hbc_prompt_template
)

@app.post("/api/v1/tutor")
def generate_tutor_response(payload: StudentQueryRequest):
    try:
        # 1. Retrieve relevant SBP examples based on the student's query
        search_query = f"Stage {payload.project_stage} {payload.student_level} {payload.query}"
        docs = retriever.invoke(search_query)
        retrieved_context = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. Format prompt with the retrieved PDFs
        formatted_prompt = prompt.format(
            student_level=payload.student_level,
            project_stage=payload.project_stage,
            context=retrieved_context if retrieved_context else "Hapana muenzaniso wawanikwa.",
            query=payload.query
        )
        
        # 3. Generate response
        response = llm.invoke(formatted_prompt)

        return {
            "response": response.strip(),
            "retrieved_context_used": True if docs else False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))