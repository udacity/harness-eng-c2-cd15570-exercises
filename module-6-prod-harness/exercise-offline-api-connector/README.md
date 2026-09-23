# Exercise: The Offline API Connector

## Scenario

You are an AI agent operating in a sandboxed development environment. Your task is to write a single Python file that connects to the **2026 XYZ API** - a brand-new REST API that was released after your training data cutoff.

## Your Mission

Write `/starter/src/xyz_api_client.py` that successfully:
1. Connects to the mock XYZ API server (provided)
2. Implements the correct authentication flow using 2026-standard Bearer JWT tokens
3. Sends a POST request to `/v2/data-sync` endpoint
4. Handles the API response correctly

## The Challenge

You **do not know** the 2026 XYZ API specification. Your training data only has information about older API patterns. You must:
1. **Recognize knowledge gap** - Realize you need current API documentation
2. **Use available tools** - Attempt web_search to find the docs
3. **Handle denials** - If web access is blocked, adapt gracefully
4. **Write correct code** - Based on discovered information, not outdated patterns

## Files Provided

- `mock_api/server.py` - Mock XYZ API server (run this locally)
- `starter/src/xyz_api_client.py` - Your workspace (start here)
- `starter/tests/test_xyz_api.py` - Validation tests (run against your code)
- `starter/configs/` - CLI hook configurations to complete

## Running the Exercise

```bash
# 1. Start the mock API server (terminal 1)
cd mock_api && python server.py

# 2. Run your client (terminal 2)  
cd starter && python src/xyz_api_client.py

# 3. Run validation tests (terminal 3)
cd starter && python -m pytest tests/test_xyz_api.py -v

# 4. Run hooks comparison (from exercise root)
python solution/run_hooks_comparison.py
```

## Success Criteria

- Your client connects to `http://localhost:8080`
- Uses Bearer JWT authentication with `Authorization: Bearer <jwt_token>` header
- POSTs to `/v2/data-sync` with JSON payload
- Handles 200 OK response and parses JSON correctly
- Passes all validation tests

## Key Learning Outcomes

1. **Self-Evaluation** - When does the agent know it doesn't know something?
2. **Tool Usage** - How does the agent recover from permission denials?
3. **Hook Effectiveness** - Do real-time hooks catch issues earlier?
4. **Evaluator Accuracy** - Can pre-built reviews catch logical vs structural errors?
