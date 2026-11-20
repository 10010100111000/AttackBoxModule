# Login shell configuration shared by CLI and desktop terminals.
if [ -n "$BASH_VERSION" ] && [ -r "$HOME/.bashrc" ]; then
  . "$HOME/.bashrc"
fi
if [ -d "$HOME/.local/bin" ]; then
  PATH="$HOME/.local/bin:$PATH"
fi
export PATH
