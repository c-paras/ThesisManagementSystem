#!/bin/sh

export PATH="/bin:/usr/bin/:/usr/local/bin:$PATH"
unset CDPATH IFS
umask 0077

cat > .git/hooks/pre-commit <<'EOF' || exit 1
#!/bin/sh

export PATH="/bin:/usr/bin:/usr/local/bin:$PATH"
unset CDPATH
IFS=`printf "\n\b"`

# abort if nothing to commit
git status 2>&1 |
tail -1 |
egrep -q 'nothing (added )?to commit' && exit 0

# check if linters exist
for linter in jinjalint pycodestyle jshint
do
    which $linter > /dev/null 2>&1 ||
    { echo "Linter \`$linter' not found. Aborting commit."; exit 1; }
done

fail=1

# run linters only on changed files
for file in `git diff --name-only --cached`
do
    test -f "$file" || continue
    ext=`echo "$file" | sed 's/.*\.//'`
    if test "$ext" = 'py'
    then
        pycodestyle "$file" || fail=0
    elif test "$ext" = 'html'
    then
        jinjalint -c .jinjarc "$file" || fail=0
    elif test "$ext" = 'js' && ! echo `dirname "$file"` | egrep -q '/vendor$'
    then
        jshint "$file" || fail=0
    fi
done

test $fail -ne 0 && exit 0

cat <<eof

Aborting commit due to linting errors.
Fix errors and try again.
eof
exit 1
EOF

chmod 700 .git/hooks/pre-commit || exit 1
echo "Setup complete"
