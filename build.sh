#!/usr/bin/env bash
# Render build script — builds React and copies into backend/static/
set -e

echo ">>> Installing frontend dependencies..."
cd frontend
npm install --silent
npm run build
echo ">>> React build done."

echo ">>> Copying build to backend/static/..."
cd ..
rm -rf backend/static
cp -r frontend/build backend/static
echo ">>> Done. backend/static is ready."

echo ">>> Installing Python dependencies..."
cd backend
pip install -r requirements.txt
echo ">>> All done!"
