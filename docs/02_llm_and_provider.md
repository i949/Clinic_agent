# 2. LLM and provider

| Component | Selection |
|---|---|
| **Model** | Llama 3.3 70B Instruct |
| **Provider/runtime** | Ollama, running locally |
| **Model tag** | `llama3.3:70b-instruct` |
| **Tool use** | Model proposes a named tool with structured arguments; the application validates and executes approved tools |

## Why this choice

- Ollama provides a local model-serving workflow, keeping the model interaction on the clinic-controlled environment when deployed locally.
- Llama 3.3 70B Instruct is the model specified for this assignment and is suitable for conversational instruction following and structured tool selection.
- Keeping the provider behind a local runtime leaves room to change the model without changing the clinic tool contracts.

## Deployment considerations

- A 70B model has substantial memory and compute requirements. Confirm that the deployment hardware can run the selected quantization at an acceptable speed before choosing it for a real clinic workflow.
- Confirm the exact model tag and tool-calling behavior against the Ollama version and model package used by the deployment.
- Local inference does not by itself provide access control, encryption, audit logging, or compliance. Those controls belong in the surrounding clinic application and infrastructure.
- Do not send real patient information to an unapproved hosted model provider.

