#!/bin/bash
# Prevent Terminal Corruption File Creation
# Add this to your shell profile (~/.bashrc or ~/.zshrc)

# 1. ALWAYS disable pagers for commands that might use them
export PAGER=cat
export GIT_PAGER=cat
export SYSTEMD_PAGER=cat

# 2. Disable psql pager
export PSQL_PAGER=

# 3. Set safer defaults for common commands
alias less='less -R'
alias more='cat'

# 4. Add git config to never use pager
git config --global core.pager cat

# 5. Function to reset terminal when corrupted
fix-terminal() {
    reset
    stty sane
    echo "Terminal reset. Run 'cd /path/to/project' to fix working directory."
}

echo "✅ Terminal corruption prevention configured"
echo "   - Pagers disabled (PAGER=cat)"
echo "   - Run 'fix-terminal' if terminal gets corrupted"
echo "   - Always check 'pwd' before running commands"
