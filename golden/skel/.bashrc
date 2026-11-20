# Interactive shell defaults for disposable learning environments.
case $- in *i*) ;; *) return ;; esac
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend checkwinsize
case "$TERM" in
  xterm*|screen*|tmux*) PS1='\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]\$ ' ;;
  *) PS1='\u@\h:\w\$ ' ;;
esac
if [[ -r /usr/share/bash-completion/bash_completion ]]; then
  . /usr/share/bash-completion/bash_completion
fi
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias ll='ls -alF'
