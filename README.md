# HBC Shona Tutor

## Download the model
```
hf download vamboai/morena-1.5b-instruct-gguf morena-1.5b-instruct-Q4_K_M.gguf --local-dir . 
```

## -ngl 99 tells it to offload all layers to the GPU
## -m specifies our smaller 4-bit model
llama-cli -m morena-1.5b-instruct-Q4_K_M.gguf -ngl 99 -p "Mhoro, ndinoda kudzidza chiShona."

```
uv add chromadb sentence-transformers pypdf langchain-chroma
```
```
uv add streamlit requests
```

### 1. Run local ingestion once to create the chroma_db volume directory
```
uv run python src/ingest.py
```

### 2. Build and launch the containerized app
```
docker compose up --build -d
```