"""
FinSathi AI - IBM Granite Connection Test
Run this FIRST to verify your API key and model work correctly.

Usage:
    cd C:\\Users\\Dishu\\Downloads\\bob_html\\FinSathi-AI\\backend
    python test_granite.py
"""

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import IBM_API_KEY, IBM_PROJECT_ID, IBM_URL, GRANITE_MODEL_ID

print("=" * 55)
print("  FinSathi AI - IBM Granite Connection Test")
print("=" * 55)
print("  Region URL : " + IBM_URL)
print("  Project ID : " + IBM_PROJECT_ID[:8] + "..." + IBM_PROJECT_ID[-4:])
print("  Model      : " + GRANITE_MODEL_ID)
print("=" * 55)

# Step 1: Authenticate
print("\n[1/3] Authenticating with IBM Cloud...")
try:
    credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
    client = APIClient(credentials=credentials, project_id=IBM_PROJECT_ID)
    print("      OK - Authentication successful!")
except Exception as e:
    print("      FAILED - Authentication error: " + str(e))
    print("\n  Fix: Check your IBM_API_KEY and IBM_URL in config.py")
    exit(1)

# Step 2: Load model
print("\n[2/3] Loading model '" + GRANITE_MODEL_ID + "'...")
try:
    model = ModelInference(
        model_id=GRANITE_MODEL_ID,
        api_client=client,
        params={
            GenParams.MAX_NEW_TOKENS: 200,
            GenParams.TEMPERATURE: 0.5,
        },
    )
    print("      OK - Model loaded!")
except Exception as e:
    print("      FAILED - Model loading error: " + str(e))
    print("\n  Fix: Check GRANITE_MODEL_ID in config.py")
    print("  Try: ibm/granite-3-8b-instruct or ibm/granite-3-2b-instruct")
    exit(1)

# Step 3: Send test prompt
print("\n[3/3] Sending test prompt to IBM Granite...")
test_prompt = """You are FinSathi AI, a financial literacy assistant for Indian users.
Answer in 2-3 sentences only.

Question: What is UPI in simple words?

Answer:"""

try:
    response = model.generate_text(prompt=test_prompt)
    print("      OK - Response received!\n")
    print("-" * 55)
    print("  IBM Granite says:")
    print("  " + response.strip().replace("\n", "\n  "))
    print("-" * 55)
except Exception as e:
    print("      FAILED - Generation error: " + str(e))
    print("\n  Possible causes:")
    print("  - Token quota exhausted (check watsonx.ai dashboard)")
    print("  - Model not available in your region")
    print("  - Network issue")
    exit(1)

print("\nAll checks passed! IBM Granite setup is working.")
print("Run: uvicorn main:app --reload --port 8000\n")
