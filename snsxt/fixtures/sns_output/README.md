Example `sns` pipeline analysis output


## Cheatsheet

Make an analysis with empty files

```bash
# delete any git repos
find sns_analysis1 -type d -name ".git" -exec rm -rf {} \;

deltouch () {
    # delete the original file and 'touch' a new empty copy with the same name
    local filename="$1"
    if [ -f "$filename" ]; then
        rm -f "$filename" && touch "$filename" || printf "ERROR: File could not be deleted: %s\n" "$filename" 
    fi
}

find sns_analysis1 -type f | while read item; do
    deltouch "$item"
done


```
