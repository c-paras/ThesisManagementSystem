#!/bin/sh

export PATH="/bin:/usr/bin/:/usr/local/bin:$PATH"
unset CDPATH IFS
umask 0077

cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh

export PATH="/bin:/usr/bin:/usr/local/bin:$PATH"
unset CDPATH IFS

# abort if nothing to commit
git status |
tail -1 |
egrep -q 'nothing to commit|nothing added to commit' && exit 0

# run linters
fail=1
jinjalint -c .jinja-config || fail=0
pep8 . || fail=0

test $fail -ne 0 && exit 0

cat <<eof

Aborting commit due to linting errors.
Fix errors and try again.
eof
exit 1
EOF
chmod 700 .git/hooks/pre-commit
