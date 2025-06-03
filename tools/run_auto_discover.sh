#!/data/data/com.termux/files/usr/bin/bash

# =========================
# 🔁 Auto-Discover Launcher
# =========================

# Define the base directory explicitly
PROJECT_ROOT_DIR="$HOME/my_ai_project_cortex"
TOOLS_DIR="$PROJECT_ROOT_DIR/brain/tools"
AUTODISCOVER_SCRIPT="$TOOLS_DIR/auto_discover.py"

echo "Attempting to launch Auto-Discover for WordForge..."

# Navigate to the tools directory OR exit if not found
if ! cd "$TOOLS_DIR"; then
  echo "❌ Error: Could not find the required directory: $TOOLS_DIR"
  termux-toast "Auto-discover failed: Directory not found."
  exit 1
fi

echo "🧠 Launching auto_discover.py from: $(pwd)..." # Verify current directory
python3 "$AUTODISCOVER_SCRIPT"

# Capture the exit status of the Python script
PYTHON_EXIT_STATUS=$?

if [ $PYTHON_EXIT_STATUS -eq 0 ]; then
  # Optional: Play a sound or vibrate (Termux specific)
  termux-vibrate -d 150
  termux-toast "WordForge Auto-discover complete!"
  echo "✅ Done! Check your concept entries & index."
else
  echo "❌ Auto-discover.py exited with an error (status: $PYTHON_EXIT_STATUS)."
  termux-toast "Auto-discover failed! Check logs."
  exit "$PYTHON_EXIT_STATUS" # Exit with the same error status as the Python script
fi
