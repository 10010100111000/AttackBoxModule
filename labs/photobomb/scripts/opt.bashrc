PATH=$(printf '%s' "$PATH" | sed 's|:/snap/bin||')
# Disable the Bash builtin so PATH lookup is used for "[".
enable -n [ # ]
