#!/bin/bash

# Save the current clipboard

cd /Users/isaac.cissna/isaac_repos/convert-math-homework-to-latex/

source /Users/isaac.cissna/.venv/bin/activate

python3 process_pdf.py

deactivate

# Close the specific Terminal window in the background
(
    sleep 0.8
    osascript -e 'tell application "Terminal" to close (every window whose name contains "handwriting2latex.command")'
) &

exit 0
