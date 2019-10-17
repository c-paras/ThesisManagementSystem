#!/bin/sh

export PATH="/bin:/usr/bin/:/usr/local/bin:$PATH"
unset CDPATH IFS
umask 0077

cat > .git/hooks/pre-commit <<'EOF' || exit 1
#!/bin/sh

export PATH="/bin:/usr/bin:/usr/local/bin:$PATH"
unset CDPATH IFS

# abort if nothing to commit
git status |
tail -1 |
egrep -q 'nothing to commit|nothing added to commit' && exit 0

# check if linters exist
for linter in jinjalint pycodestyle jshint
do
    which $linter > /dev/null 2>&1 ||
    { echo "Linter \`$linter' not found. Aborting commit."; exit 1; }
done

# run linters
fail=1
jinjalint -c .jinjarc templates/ || fail=0
pycodestyle . || fail=0
jshint static/js/ --exclude static/js/vendor || fail=0

test $fail -ne 0 && exit 0

cat <<eof

Aborting commit due to linting errors.
Fix errors and try again.
eof
exit 1
EOF

chmod 700 .git/hooks/pre-commit || exit 1
echo "Setup complete"
