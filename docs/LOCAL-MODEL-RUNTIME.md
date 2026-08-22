# Self-hosted Local Model Runtime

## Goal

Run an approved open-weight model behind our `ModelProvider` interface so the Project Factory can execute selected workloads without per-token API billing.

## Important distinction

GitHub stores the model runtime code and configuration. It does not execute the model. The inference process must run on a compute service we control or an approved low-cost hosting environment.

Customers still need only a phone/browser.

## Runtime contract

`OpenAICompatibleLocalProvider` speaks to an OpenAI-compatible `/v1/chat/completions` endpoint. The backend can be implemented by an approved local inference server such as Ollama, llama.cpp server, vLLM, or another compatible runtime.

## Selection policy

1. Prefer local provider when available and within the cost ceiling.
2. Use an approved external provider only when policy allows and the measured cost is acceptable.
3. Never silently exceed the configured cost ceiling.
4. Record provider, model, token usage and estimated cost in evidence.

## First deployment shape

`Project Factory service → private local-model endpoint → isolated project workspace`

The model endpoint must not be public. Authentication/network controls should be added before production exposure.

## Model selection

Start with a small coding-capable open-weight model that fits the selected compute budget. Do not commit multi-gigabyte model weights to Git. Store weights in model storage and pin the model/version in deployment configuration.

## Completion gate

The runtime is production-ready only after a real smoke test demonstrates: request → local model → coding task → tests → verification → evidence → checkpoint.
