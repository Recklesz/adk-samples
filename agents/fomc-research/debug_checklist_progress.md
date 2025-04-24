# Debug Checklist Progress

## 1. Verify the plumbing between ADK ↔ tools
- [x] Tools are FunctionTool instances
- [x] Docstrings follow ADK "effective tool" rules
- [x] Signature shows the parameters the model must supply

## 2. Teach the LLM how to call the tools in the prompt
- [x] Add explicit recipe to the prompt

## 3. Lemlist API quirks that break the request
- [x] Fix HTTP 400 – "invalid filterId" (use current_exp_company_name)
- [x] Fix HTTP 401 (use Bearer auth)
- [x] Fix empty 200 response (pass multiple titles in one filter)

## 4. State keys that the tool expects but the agent never writes
- [x] Ensure store_state_tool writes necessary keys
