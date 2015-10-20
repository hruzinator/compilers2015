echo "Token types"
echo "-----------"
grep -E -o '\b[A-Z]+\b' terminals.txt | sort | uniq
