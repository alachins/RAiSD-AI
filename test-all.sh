#!/bin/bash

exec=$1

case "$exec" in
  "RAiSD-AI")
  	echo "RUNNING RAiSD-AI"
  ;;
  "RAiSD-AI-ZLIB")
  	echo "RUNNING RAiSD-AI-ZLIB"
  ;;
  *)
  	echo "ERROR: The first argument must be either RAiSD-AI or RAiSD-AI-ZLIB"
    ;;
esac

mode=$2

epochs=10

TRAINING_NEUTRAL=datasets/train/msneutral1_100sims.out
TRAINING_SWEEP=datasets/train/msselection1_100sims.out

TEST_NEUTRAL=datasets/test/msneutral1_10sims.out
TEST_SWEEP=datasets/test/msselection1_10sims.out

TRAINING_NEUTRAL1=datasets/train/msneutral1_100sims.out
TRAINING_SWEEP1=datasets/train/msselection1_100sims.out
TRAINING_NEUTRAL2=datasets/train/msneutral1_100sims.out
TRAINING_SWEEP2=datasets/train/msselection1_100sims.out

TEST_NEUTRAL1=datasets/test/msneutral1_10sims.out
TEST_SWEEP1=datasets/test/msselection1_10sims.out
TEST_NEUTRAL2=datasets/test/msneutral1_10sims.out
TEST_SWEEP2=datasets/test/msselection1_10sims.out

TEST_SWEEP_DATASET=datasets/train/msselection1_100sims.out


case "$mode" in
  "0")
    	echo "GENERATING TRAINING DATA"
	
	# Images - SNP data
	./$exec -n TrainingData2DSNP -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -O
	./$exec -n TrainingData2DSNP -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -O

	# Images - SNP data and positions
	./$exec -n TrainingData2DSNPPOS -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -typ 1 -O
	./$exec -n TrainingData2DSNPPOS -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -typ 1 -O

	# Images - SNP data and muVar
	./$exec -n TrainingData2DSNPVAR -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -typ 2 -O
	./$exec -n TrainingData2DSNPVAR -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -typ 2 -O

	# Binary - SNP data and positions
	./$exec -n TrainingDataBINSNPPOS -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -bin -O
	./$exec -n TrainingDataBINSNPPOS -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -bin -O

	# Binary - derived allele frequencies and positions
	./$exec -n TrainingDataBINFRQPOS -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -bin -typ 1 -O
	./$exec -n TrainingDataBINFRQPOS -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -bin -typ 1 -O  
    
    ;;
  "1")
  
        echo "GENERATING TEST DATA"

	# Images - SNP data
	./$exec -n TestData2DSNP -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -O 
	./$exec -n TestData2DSNP -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -O

	# Images - SNP data and positions
	./$exec -n TestData2DSNPPOS -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -typ 1 -O 
	./$exec -n TestData2DSNPPOS -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -typ 1 -O

	# Images - SNP data and muVar
	./$exec -n TestData2DSNPVAR -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -typ 2 -O 
	./$exec -n TestData2DSNPVAR -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -typ 2 -O

	# Binary - SNP data and positions
	./$exec -n TestDataBINSNPPOS -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -bin -O
	./$exec -n TestDataBINSNPPOS -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -bin -O

	# Binary - derived allele frequencies and positions
	./$exec -n TestDataBINFRQPOS -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -bin -typ 1 -O
	./$exec -n TestDataBINFRQPOS -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -bin -typ 1 -O
	
    ;;
  "2")
    	
    	echo "TRAINING AND TESTING SWEEPNET USING TENSORFLOW"
    
    	./$exec -n SweepNetTF-2DSNP -I RAiSD_Images.TrainingData2DSNP -f -op MDL-GEN -O -frm -e $epochs -useTF
    	./$exec -n SweepNetTF-2DSNPPOS -I RAiSD_Images.TrainingData2DSNPPOS -f -op MDL-GEN -O -frm -e $epochs -useTF
    	./$exec -n SweepNetTF-2DSNPVAR -I RAiSD_Images.TrainingData2DSNPVAR -f -op MDL-GEN -O -frm -e $epochs -useTF
    	
    	./$exec -n SweepNetTF-2DSNP-ModelTest -mdl RAiSD_Model.SweepNetTF-2DSNP -f -op MDL-TST -I RAiSD_Images.TestData2DSNP -clp 2 sweepTR=sweepTE neutralTR=neutralTE -useTF 
    	./$exec -n SweepNetTF-2DSNPPOS-ModelTest -mdl RAiSD_Model.SweepNetTF-2DSNPPOS -f -op MDL-TST -I RAiSD_Images.TestData2DSNPPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE -useTF 
    	./$exec -n SweepNetTF-2DSNPVAR-ModelTest -mdl RAiSD_Model.SweepNetTF-2DSNPVAR -f -op MDL-TST -I RAiSD_Images.TestData2DSNPVAR -clp 2 sweepTR=sweepTE neutralTR=neutralTE -useTF 
    	      
    ;;
  "3")
    
    	echo "TRAINING AND TESTING SWEEPNET USING PYTORCH"
    
    	./$exec -n SweepNetPT-2DSNP -I RAiSD_Images.TrainingData2DSNP -f -op MDL-GEN -O -frm -e $epochs -arc SweepNet
    	./$exec -n SweepNetPT-2DSNPPOS -I RAiSD_Images.TrainingData2DSNPPOS -f -op MDL-GEN -O -frm -e $epochs -arc SweepNet
    	./$exec -n SweepNetPT-2DSNPVAR -I RAiSD_Images.TrainingData2DSNPVAR -f -op MDL-GEN -O -frm -e $epochs -arc SweepNet
    	./$exec -n SweepNetPT-BINSNPPOS -I RAiSD_Images.TrainingDataBINSNPPOS -f -op MDL-GEN -O -frm -e $epochs -arc SweepNet
     	
   	./$exec -n SweepNetPT-2DSNP-ModelTest -mdl RAiSD_Model.SweepNetPT-2DSNP -f -op MDL-TST -I RAiSD_Images.TestData2DSNP -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n SweepNetPT-2DSNPPOS-ModelTest -mdl RAiSD_Model.SweepNetPT-2DSNPPOS -f -op MDL-TST -I RAiSD_Images.TestData2DSNPPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n SweepNetPT-2DSNPVAR-ModelTest -mdl RAiSD_Model.SweepNetPT-2DSNPVAR -f -op MDL-TST -I RAiSD_Images.TestData2DSNPVAR -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n SweepNetPT-BINSNPPOS-ModelTest -mdl RAiSD_Model.SweepNetPT-BINSNPPOS -f -op MDL-TST -I RAiSD_Images.TestDataBINSNPPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE
   
    ;;
  "4")
    
    	echo "TRAINING AND TESTING FAST-NN USING PYTORCH"
    
    	./$exec -n FAST-NN-PT-2DSNP -I RAiSD_Images.TrainingData2DSNP -f -op MDL-GEN -O -frm -e $epochs 
    	./$exec -n FAST-NN-PT-2DSNPPOS -I RAiSD_Images.TrainingData2DSNPPOS -f -op MDL-GEN -O -frm -e $epochs 
    	./$exec -n FAST-NN-PT-2DSNPVAR -I RAiSD_Images.TrainingData2DSNPVAR -f -op MDL-GEN -O -frm -e $epochs 
    	./$exec -n FAST-NN-PT-BINSNPPOS -I RAiSD_Images.TrainingDataBINSNPPOS -f -op MDL-GEN -O -frm -e $epochs 
    	./$exec -n FAST-NN-PT-BINFRQPOS -I RAiSD_Images.TrainingDataBINFRQPOS -f -op MDL-GEN -O -frm -e $epochs 
    	
   	./$exec -n FAST-NN-PT-2DSNP-ModelTest -mdl RAiSD_Model.FAST-NN-PT-2DSNP -f -op MDL-TST -I RAiSD_Images.TestData2DSNP -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n FAST-NN-PT-2DSNPPOS-ModelTest -mdl RAiSD_Model.FAST-NN-PT-2DSNPPOS -f -op MDL-TST -I RAiSD_Images.TestData2DSNPPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n FAST-NN-PT-2DSNPVAR-ModelTest -mdl RAiSD_Model.FAST-NN-PT-2DSNPVAR -f -op MDL-TST -I RAiSD_Images.TestData2DSNPVAR -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n FAST-NN-PT-BINSNPPOS-ModelTest -mdl RAiSD_Model.FAST-NN-PT-BINSNPPOS -f -op MDL-TST -I RAiSD_Images.TestDataBINSNPPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE
    	./$exec -n FAST-NN-PT-BINFRQPOS-ModelTest -mdl RAiSD_Model.FAST-NN-PT-BINFRQPOS -f -op MDL-TST -I RAiSD_Images.TestDataBINFRQPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE 
   
    ;;
  "5")
    echo "GENERATING TRAINING DATA FOR SWEEPNETRECOMBINATION"

	# Images - SNP data
	./$exec -n TrainingData2DSNP-4x -I $TRAINING_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR1 -f -frm 
	./$exec -n TrainingData2DSNP-4x -I $TRAINING_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR1 -f
	./$exec -n TrainingData2DSNP-4x -I $TRAINING_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR2 -f
	./$exec -n TrainingData2DSNP-4x -I $TRAINING_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR2 -f

	# Images - SNP data and positions
	./$exec -n TrainingData2DSNPPOS-4x -I $TRAINING_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR1 -f -frm -typ 1 
	./$exec -n TrainingData2DSNPPOS-4x -I $TRAINING_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR1 -f -typ 1
	./$exec -n TrainingData2DSNPPOS-4x -I $TRAINING_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR2 -f -typ 1 
	./$exec -n TrainingData2DSNPPOS-4x -I $TRAINING_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR2 -f -typ 1

	# Images - SNP data and muVar
	./$exec -n TrainingData2DSNPVAR-4x -I $TRAINING_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR1 -f -frm -typ 2 
	./$exec -n TrainingData2DSNPVAR-4x -I $TRAINING_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR1 -f -typ 2
	./$exec -n TrainingData2DSNPVAR-4x -I $TRAINING_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR2 -f -typ 2 
	./$exec -n TrainingData2DSNPVAR-4x -I $TRAINING_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR2 -f -typ 2

	# Binary - SNP data and positions
	./$exec -n TrainingDataBINSNPPOS-4x -I $TRAINING_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR1 -f -frm -bin
	./$exec -n TrainingDataBINSNPPOS-4x -I $TRAINING_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR1 -f -bin
	./$exec -n TrainingDataBINSNPPOS-4x -I $TRAINING_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTR2 -f -bin
	./$exec -n TrainingDataBINSNPPOS-4x -I $TRAINING_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTR2 -f -bin  
    
    ;;
  "6")
    echo "GENERATING TEST DATA FOR SWEEPNETRECOMBINATION"    

	# Images - SNP data
	./$exec -n TestData2DSNP-4x -I $TEST_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE1 -f -frm 
	./$exec -n TestData2DSNP-4x -I $TEST_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE1 -f
	./$exec -n TestData2DSNP-4x -I $TEST_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE2 -f
	./$exec -n TestData2DSNP-4x -I $TEST_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE2 -f

	# Images - SNP data and positions
	./$exec -n TestData2DSNPPOS-4x -I $TEST_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE1 -f -frm -typ 1 
	./$exec -n TestData2DSNPPOS-4x -I $TEST_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE1 -f -typ 1
	./$exec -n TestData2DSNPPOS-4x -I $TEST_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE2 -f -typ 1 
	./$exec -n TestData2DSNPPOS-4x -I $TEST_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE2 -f -typ 1

	# Images - SNP data and muVar
	./$exec -n TestData2DSNPVAR-4x -I $TEST_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE1 -f -frm -typ 2 
	./$exec -n TestData2DSNPVAR-4x -I $TEST_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE1 -f -typ 2
	./$exec -n TestData2DSNPVAR-4x -I $TEST_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE2 -f -typ 2 
	./$exec -n TestData2DSNPVAR-4x -I $TEST_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE2 -f -typ 2

	# Binary - SNP data and positions
	./$exec -n TestDataBINSNPPOS-4x -I $TEST_NEUTRAL1 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE1 -f -frm -bin
	./$exec -n TestDataBINSNPPOS-4x -I $TEST_SWEEP1 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE1 -f -bin
	./$exec -n TestDataBINSNPPOS-4x -I $TEST_NEUTRAL2 -L 100000 -its 50000 -op IMG-GEN -icl neutralTE2 -f -bin
	./$exec -n TestDataBINSNPPOS-4x -I $TEST_SWEEP2 -L 100000 -its 50000 -op IMG-GEN -icl sweepTE2 -f -bin  
    
    ;;
  "7")
    
    	echo "TRAINING AND TESTING SWEEPNETRECOMBINATION (PYTORCH-ONLY)"
    
    	./$exec -n SweepNetPT-2DSNP-4x -I RAiSD_Images.TrainingData2DSNP-4x -f -op MDL-GEN -O -frm -e $epochs -arc SweepNetRecombination -cl4 label00=neutralTR1 label01=sweepTR1 label10=neutralTR2 label11=sweepTR2
    	./$exec -n SweepNetPT-2DSNPPOS-4x -I RAiSD_Images.TrainingData2DSNPPOS-4x -f -op MDL-GEN -O -frm -e $epochs -arc SweepNetRecombination -cl4 label00=neutralTR1 label01=sweepTR1 label10=neutralTR2 label11=sweepTR2
    	./$exec -n SweepNetPT-2DSNPVAR-4x -I RAiSD_Images.TrainingData2DSNPVAR-4x -f -op MDL-GEN -O -frm -e $epochs -arc SweepNetRecombination -cl4 label00=neutralTR1 label01=sweepTR1 label10=neutralTR2 label11=sweepTR2
    	./$exec -n SweepNetPT-BINSNPPOS-4x -I RAiSD_Images.TrainingDataBINSNPPOS-4x -f -op MDL-GEN -O -frm -e $epochs -arc SweepNetRecombination -cl4 label00=neutralTR1 label01=sweepTR1 label10=neutralTR2 label11=sweepTR2
    	
   	./$exec -n SweepNetPT-2DSNP-ModelTest-4x -mdl RAiSD_Model.SweepNetPT-2DSNP-4x -f -op MDL-TST -I RAiSD_Images.TestData2DSNP-4x -clp 4 sweepTR1=sweepTE1 neutralTR1=neutralTE1 sweepTR2=sweepTE2 neutralTR2=neutralTE2
    	./$exec -n SweepNetPT-2DSNPPOS-ModelTest-4x -mdl RAiSD_Model.SweepNetPT-2DSNPPOS-4x -f -op MDL-TST -I RAiSD_Images.TestData2DSNPPOS-4x -clp 4 sweepTR1=sweepTE1 neutralTR1=neutralTE1 sweepTR2=sweepTE2 neutralTR2=neutralTE2
    	./$exec -n SweepNetPT-2DSNPVAR-ModelTest-4x -mdl RAiSD_Model.SweepNetPT-2DSNPVAR-4x -f -op MDL-TST -I RAiSD_Images.TestData2DSNPVAR-4x -clp 4 sweepTR1=sweepTE1 neutralTR1=neutralTE1 sweepTR2=sweepTE2 neutralTR2=neutralTE2
   	./$exec -n SweepNetPT-BINSNPPOS-ModelTest-4x -mdl RAiSD_Model.SweepNetPT-BINSNPPOS-4x -f -op MDL-TST -I RAiSD_Images.TestDataBINSNPPOS-4x -clp 4 sweepTR1=sweepTE1 neutralTR1=neutralTE1 sweepTR2=sweepTE2 neutralTR2=neutralTE2

   
    ;;
    
  "8")
    
    	echo "SCAN WITH SWEEPNET USING TENSORFLOW"
    	
    	TESTING_SWEEP_DATASET=../d1/msselectionNEW2.out
    	
   	./$exec -n SweepNetTF-2DSNP-SCAN -mdl RAiSD_Model.SweepNetTF-2DSNP -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n SweepNetTF-2DSNPPOS-SCAN -mdl RAiSD_Model.SweepNetTF-2DSNPPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n SweepNetTF-2DSNPVAR-SCAN -mdl RAiSD_Model.SweepNetTF-2DSNPVAR -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O   
       
    ;;
    
 "9")
    
    	echo "SCAN WITH SWEEPNET USING PYTORCH"
    	
    	./$exec -n SweepNetPT-2DSNP-SCAN -mdl RAiSD_Model.SweepNetPT-2DSNP -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n SweepNetPT-2DSNPPOS-SCAN -mdl RAiSD_Model.SweepNetPT-2DSNPPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n SweepNetPT-2DSNPVAR-SCAN -mdl RAiSD_Model.SweepNetPT-2DSNPVAR -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n SweepNetPT-BINSNPPOS-SCAN -mdl RAiSD_Model.SweepNetPT-BINSNPPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O 
   
    ;;
    
  "10")
    
    	echo "SCAN WITH FAST-NN USING PYTORCH"
    	
    	./$exec -n FAST-NN-PT-2DSNP-SCAN -mdl RAiSD_Model.FAST-NN-PT-2DSNP -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n FAST-NN-PT-2DSNPPOS-SCAN -mdl RAiSD_Model.FAST-NN-PT-2DSNPPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n FAST-NN-PT-2DSNPVAR-SCAN -mdl RAiSD_Model.FAST-NN-PT-2DSNPVAR -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n FAST-NN-PT-BINSNPPOS-SCAN -mdl RAiSD_Model.FAST-NN-PT-BINSNPPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O
    	./$exec -n FAST-NN-PT-BINFRQPOS-SCAN -mdl RAiSD_Model.FAST-NN-PT-BINFRQPOS -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -P -O 
    
    ;;
    
  "11")
    
    	echo "SCAN WITH SWEEPNETRECOMBINATION USING PYTORCH"
    	
    	./$exec -n SweepNetPT-2DSNP-SCAN-4x -mdl RAiSD_Model.SweepNetPT-2DSNP-4x -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 2 1 3 -P -O
    	./$exec -n SweepNetPT-2DSNPPOS-SCAN-4x -mdl RAiSD_Model.SweepNetPT-2DSNPPOS-4x -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 2 1 3 -P -O
    	./$exec -n SweepNetPT-2DSNPVAR-SCAN-4x -mdl RAiSD_Model.SweepNetPT-2DSNPVAR-4x -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 2 1 3 -P -O
    	./$exec -n SweepNetPT-BINSNPPOS-SCAN-4x -mdl RAiSD_Model.SweepNetPT-BINSNPPOS-4x -f -op SWP-SCN -I $TEST_SWEEP_DATASET -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 2 1 3 -P -O
   
    ;;

  *)
    echo "ERROR: The second argument must be an integer (valid range: 0 - 11)"
    echo "	0 -> Generates training data"
    echo "	1 -> Generates test data"
    echo "	2 -> Trains and tests the TensorFlow implementation of SweepNet"
    echo "	3 -> Trains and tests the PyTorch implementation of SweepNet"
    echo "	4 -> Trains and tests FAST-NN (PyTorch)"
    echo "	5 -> Generates training data for SweepNetRecombination"
    echo "	6 -> Generates test data for SweepNetRecombination"
    echo "	7 -> Trains and tests SweepNetRecombination (PyTorch)"
    echo "	8 -> Full scan using the TensorFlow implementation of SweepNet"
    echo "	9 -> Full scan using the PyTorch implementation of SweepNet"
    echo "       10 -> Full scan using FAST-NN (PyTorch)"  
    echo "       11 -> Full scan using SweepNetRecombination (PyTorch)"
    ;;
esac




