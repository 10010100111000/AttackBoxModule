# Worker sessions do not have a PAM login to unlock a desktop keyring.
# Password saving is disabled by managed policy; browser state stays local
# to the learner's disposable sandbox rather than waiting for an unlock UI.
export CHROMIUM_FLAGS="${CHROMIUM_FLAGS:-} --password-store=basic"
