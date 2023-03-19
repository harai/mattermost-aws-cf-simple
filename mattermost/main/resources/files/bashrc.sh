export PS1='\n\[\033[44m\][\t \u@\h \w] Mattermost (${STACK_NAME}) \[\033[49m\]\n\$ '

test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
alias ls='ls --color'
alias grep='grep --color'
alias fgrep='fgrep --color'
alias egrep='egrep --color'

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
