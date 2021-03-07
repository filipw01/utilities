OLD_IFS=$IFS
IFS=$'\n'
FILES_TO_COMPRESS=($(find . -iname "*.mov" -or -iname "*.mp4" -or -iname "*.avi" -or -iname "*.mkv" -or -iname "*.mpg" -or -iname "*.mpeg" -or -iname "*.vob"))
IFS=$OLD_IFS
FILES_COUNT=${#FILES_TO_COMPRESS[@]}
CURRENT_FILE=1
SCRIPT_ROOT=$(pwd)
for ((i = 0; i < ${FILES_COUNT}; i++)); do
    FILENAME=$(basename "${FILES_TO_COMPRESS[$i]}")
    DIRNAME=$(dirname "${FILES_TO_COMPRESS[$i]}")
    mkdir -p "compressed/$DIRNAME"
    cd "$DIRNAME"
    ffmpeg -i "$FILENAME" -vf scale=iw:ih -c:v libx264 -preset fast -crf 20 "$SCRIPT_ROOT/compressed/$DIRNAME/$FILENAME"
    echo "Finished ${FILES_TO_COMPRESS[$i]} $CURRENT_FILE/$FILES_COUNT"
    CURRENT_FILE=$(($CURRENT_FILE + 1))
    cd "$SCRIPT_ROOT"
done
