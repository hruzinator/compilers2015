echo "\nToken types"
echo "-----------"
grep -E -o '\b[A-Z]+\b' terminals.txt | sort | uniq

echo "\nADDOPS"
echo "-----------"
grep -E '\bADDOP\b' terminals.txt | sort | uniq

echo "\nMULTOPS"
echo "-----------"
grep -E '\bMULTOP\b' terminals.txt | sort | uniq

echo "\nASSIGNOP"
echo "-----------"
grep -E '\bASSIGNOP\b' terminals.txt | sort | uniq

echo "\nRELOPS"
echo "-----------"
grep -E '\bRELOP\b' terminals.txt | sort | uniq

echo "\nIDENTIFIER"
echo "-----------"
grep -E '\bIDENTIFIER\b' terminals.txt | sort | uniq

echo "\nSYMBOLS"
echo "-----------"
grep -E '\bSYMBOL\b' terminals.txt | sort | uniq

echo "\nNUMBERS"
echo "-----------"
grep -E '\bNUMBER\b' terminals.txt | sort | uniq

echo "\nKEYWORDS"
echo "-----------"
grep -E '\bKEYWORD\b' terminals.txt | sort | uniq

echo ""
