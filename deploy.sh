# FinSathi AI - IBM Cloud Code Engine Deployment
# Run each command in order from: C:\Users\Dishu\Downloads\bob_html\FinSathi-AI\
# Replace placeholder values before running this script.

# STEP 1: Target region
ibmcloud target -r us-south -g Default

# STEP 2: Create Code Engine project
ibmcloud ce project create --name finsathi-ai

# STEP 3: Select the project
ibmcloud ce project select --name finsathi-ai

# STEP 4: Create a build config (points to your local source + ICR)
ibmcloud ce build create --name finsathi-build \
  --build-type local \
  --image us.icr.io/finsathi/finsathi-ai:latest \
  --registry-secret icr-secret \
  --dockerfile Dockerfile

# STEP 5: Create ICR registry secret for Code Engine
ibmcloud ce secret create --name icr-secret \
  --format registry \
  --server us.icr.io \
  --username iamapikey \
  --password YOUR_IBM_CLOUD_API_KEY

# STEP 6: Submit the build run (uploads source + builds on IBM Cloud)
ibmcloud ce buildrun submit --build finsathi-build --name finsathi-build-run-1

# STEP 7: Watch build logs (wait until "Build completed")
ibmcloud ce buildrun logs --buildrun finsathi-build-run-1 --follow

# STEP 8: Deploy the application
ibmcloud ce application create \
  --name finsathi-ai \
  --image us.icr.io/finsathi/finsathi-ai:latest \
  --registry-secret icr-secret \
  --port 8000 \
  --cpu 1 \
  --memory 4G \
  --env IBM_API_KEY=YOUR_IBM_API_KEY \
  --env IBM_PROJECT_ID=YOUR_IBM_PROJECT_ID \
  --env IBM_URL=https://us-south.ml.cloud.ibm.com \
  --min-scale 1 \
  --max-scale 2

# STEP 9: Get your live URL
ibmcloud ce application get --name finsathi-ai --output url
