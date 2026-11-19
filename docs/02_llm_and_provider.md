# 2. LLM and provider

| Component | Selection |
|---|---|
| **Model** | Llama 3.3 70B Instruct |
| **Provider/runtime** | Ollama, running locally |
| **Model tag** | `llama3.3` (70B instruction-tuned model) |
| **Agent framework** | LlamaIndex `AgentWorkflow` |
| **Tool use** | The model selects typed Python function tools; demo code validates and executes them |

## Why this choice

- Ollama provides a local model-serving workflow, keeping the model interaction on the clinic-controlled environment when deployed locally.
- Llama 3.3 70B Instruct is the model specified for this assignment. Ollama lists the `llama3.3` model with tool support.
- LlamaIndex's Ollama integration connects the model to `AgentWorkflow` while keeping the agent code provider-specific only at initialization.
- Keeping the provider behind a local runtime leaves room to change the model without changing the clinic tool contracts.

## Deployment considerations

- The listed default `llama3.3` quantization is about 43 GB. A 70B model has substantial memory and compute requirements; confirm the deployment hardware can run the selected quantization at an acceptable speed.
- Confirm the exact model tag and tool-calling behavior against the Ollama version and model package used by the deployment.
- Local inference does not by itself provide access control, encryption, audit logging, or compliance. Those controls belong in the surrounding clinic application and infrastructure.
- Do not send real patient information to an unapproved hosted model provider.

## LlamaIndex setup

Install `llama-index-core` and `llama-index-llms-ollama`, import `Ollama` from `llama_index.llms.ollama`, and pass typed tools to `AgentWorkflow.from_tools_or_functions`. This follows the local-model and agent examples in the [LlamaIndex local-model guide](https://developers.llamaindex.ai/python/framework/getting_started/starter_example_local/) and [agent guide](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/).

