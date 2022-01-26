echo "---------CESM submit script ----------"
echo "$0" in $PWD

cd $(dirname $0)

echo now in $PWD

#./preview_run 
if [[ -f case.build ]]
then
./case.build  # quick in view of the clone.
./case.submit 
else
	echo "no build file"
fi


