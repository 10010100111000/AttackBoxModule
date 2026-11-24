import sys
import markdown
text=sys.stdin.read(200000)
# Real Python-Markdown parser; HTML passthrough is intentionally enabled.
sys.stdout.write(markdown.markdown(text, extensions=["extra", "sane_lists"]))
