#批量测试

newname="specAug"
for testSet in test-2580  test-3650 test-9890; do
#for testSet in  test-2580; do
	echo $testSet
	tail=${testSet#*-}
        #date=`date +"%Y%m%d%H"`
        date=`date +"%Y%m%d"`
        outdir=data-out/"$date"_"$newname"-biglm-discount_$tail
	echo $outdir
        python3 examples/batch_wavfile.py data/$testSet  $outdir/result.txt	
	python3 compute-cer/run_cer.py  data/$testSet/text  $outdir/result.txt  > $outdir/per_utt
	tail -n 1 $outdir/per_utt
	echo $testSet"  finish "
done
