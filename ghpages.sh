
#These might be parameters
SRCDOCS=/home/pbrian/src/rhaptos2.user/docs/_build/html
TMPREPO=/tmp/docs/user

### get the last commit message
cd $SRCDOCS
MSG="Adding gh-pages docs for `git log -1 --pretty=short --abbrev-commit`"

### clear the decks
rm -rf $TMPREPO
mkdir -p -m 0755 $TMPREPO

### checkout gh-pages into TMP
git clone git@github.com:Connexions/rhaptos2.user.git $TMPREPO
cd $TMPREPO
git checkout gh-pages

### cp the docs over and commit
cp -r $SRCDOCS/ $TMPREPO

### gh-pages thinks any _folder is special and sphinx breaks
## no longer rewquired as we add a empty file ".nojekyll" to root
# git mv _static/ static
# find . -iname "*.html" | xargs sed -i "" -e "s/_static/static/g"

git add -A
git commit -m "$MSG" && git push origin gh-pages

#workon vuser
#cd $SRCDOCS/../../
#make clean && make html
