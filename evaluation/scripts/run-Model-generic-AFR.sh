#!/bin/bash

exec=RAiSD-AI

model=AFR216-FSTRNNG

arc="FASTER-NN-G" # FASTER-NN-G

#=====================================================================================#
# DATA PREPARATION PARAMETERS 

GENERATE=false

length=2000000 # This is used in Scan as well
target=1000000 # This is used in Scan as well
window=(400) 

datasetTrainNeutral=runsAFR216/neutral_dataset5000.out 
datasetTrainSelSweep=runsAFR216/sweep_dataset5000.out 
ips1=(10)

datasetTestNeutral=runsAFR216/neutral_dataset1000.out 
datasetTestSelSweep=runsAFR216/sweep_dataset1000.out 
ips2=(1)

#-------------#
[[ "$arc" == "FASTER-NN-G" ]] && type=0 || type=1

#=====================================================================================#
# TRAINING PARAMETERS 

TRAIN=true

epochs=100
groups=108
gpuTrain=yes

iters=9 # This is used in Test and Scan as well

MAX_PARALLEL_RUNS=3  # This is used in Test and Scan as well

#-------------#
argGroups=()
[[ "$arc" == "FASTER-NN-G" ]] && argGroups+=("-g" "$groups")
[[ "$gpuTrain" == "yes" ]] && gpuTrainString="-gpu" || gpuTrainString=""

#=====================================================================================#
# MODEL TEST PARAMETERS 

TEST=true

gpuTest=yes

#-------------#
[[ "$gpuTest" == "yes" ]] && gpuTestString="-gpu" || gpuTestString=""

#=====================================================================================#
# SCAN TEST PARAMETERS 

SCAN=true

gpuScan=yes

grid=250

#-------------#
[[ "$gpuScan" == "yes" ]] && gpuScanString="-gpu" || gpuScanString=""
#=====================================================================================#


#*************************************************************************************#
# 			      DO NOT EDIT BELOW THIS LINE 			      #
#*************************************************************************************#

#=====================================================================================#
# --------------------------------- DATA PREPARATION ---------------------------------#
#=====================================================================================#
if $GENERATE; then

	for wi in "${window[@]}"; do
		# Training data
		for ip in "${ips1[@]}"; do
		    curnameTrain=TrainingData-${model}-win${wi}-ips${ip}
		    rm -r RAiSD_Images.${curnameTrain}

		    $exec -n ${curnameTrain} -I "$datasetTrainNeutral" -L "$length" -its "$target" -op IMG-GEN -icl neutral -f -bin -typ "$type" -w "$wi" -iws 1 -ips "$ip" -frm &
		    sleep 5

		    $exec -n ${curnameTrain} -I "$datasetTrainSelSweep" -L "$length" -its "$target" -op IMG-GEN -icl selsweep -f -bin -typ "$type" -w "$wi" -iws 1 -ips "$ip" &
		done

		# Test data
		for ip in "${ips2[@]}"; do
		    curnameTest=TestData-${model}-win${wi}-ips${ip}
		    rm -r RAiSD_Images.${curnameTest}

		    $exec -n ${curnameTest} -I "$datasetTestNeutral" -L "$length" -its "$target" -op IMG-GEN -icl neutral -f -bin -typ "$type" -w "$wi" -iws 1 -ips "$ip" -frm &
		    sleep 5

		    $exec -n ${curnameTest} -I "$datasetTestSelSweep" -L "$length" -its "$target" -op IMG-GEN -icl selsweep -f -bin -typ "$type" -w "$wi" -iws 1 -ips "$ip" &
		done
	done

	wait
	
fi

#=====================================================================================#
# ------------------------------------- TRAINING -------------------------------------#
#=====================================================================================#
if $TRAIN; then

	running=0

	for wi in "${window[@]}"; do
		
		for ip in "${ips1[@]}"; do
			
			curnameModel=${model}-win${wi}-ips${ip}
			
			for ((iter=1; iter<=iters; iter++)); do	

				$exec -n ${curnameModel}-iter${iter} -I RAiSD_Images.TrainingData-${curnameModel} -f -op MDL-GEN -O -frm -e "$epochs" -arc "$arc" "${argGroups[@]}" "$gpuTrainString" & 

				((running++))	
				
				if (( running >= MAX_PARALLEL_RUNS )); then
				    wait -n 
				    ((running--))
				fi
			done
		done
	done
	
	wait	
	
fi

#=====================================================================================#
# ------------------------------------ MODEL TEST ------------------------------------#
#=====================================================================================#
if $TEST; then

	running=0

	for wi in "${window[@]}"; do
		
		for ip in "${ips1[@]}"; do
		
			for ((iter=1; iter<=iters; iter++)); do

				curnameModel=${model}-win${wi}-ips${ip}-iter${iter}
				curnameModelTest=ModelTest-${curnameModel}			

				for ipTe in "${ips2[@]}"; do
					
			    		$exec -n ${curnameModelTest}-ipsTE${ipTe} -I RAiSD_Images.TestData-${model}-win${wi}-ips${ipTe} -op MDL-TST -f -mdl RAiSD_Model.${curnameModel} -clp 2 neutral=neutral selsweep=selsweep "$gpuTestString" &
					
					((running++))	
					
					if (( running >= MAX_PARALLEL_RUNS )); then
					    wait -n 
					    ((running--))
					fi
				
				done
			done		

		done
	done
		
	wait
		
fi

#=====================================================================================#
# ------------------------------------- SCAN TEST ------------------------------------#
#=====================================================================================#
if $SCAN; then

	running=0

	#Neutral runs
	
	for wi in "${window[@]}"; do
		
		for ip in "${ips1[@]}"; do

			for ((iter=1; iter<=iters; iter++)); do
	
				curnameModel=${model}-win${wi}-ips${ip}-iter${iter}
				curnameModelTest=ModelTest-${curnameModel}
				
				rm -r workspace-${curnameModel}
				mkdir workspace-${curnameModel}
				cd workspace-${curnameModel}						

				for ipTe in "${ips2[@]}"; do

					curnameTestRun=ScanTest-${curnameModel}-ipsTE${ipTe}
					
					#Neutral run
					$exec -n ${curnameTestRun}-neut -mdl ../RAiSD_Model.${curnameModel} -f -op SWP-SCN -I ../$datasetTestNeutral -L $length -frm -T $target -d 50000 -G $grid -pci 1 1 -O -k 0.05 "$gpuScanString" &
					
					cd ..
					
					((running++))	
					
					if (( running >= MAX_PARALLEL_RUNS )); then
					    wait -n 
					    ((running--))
					fi
				done
			done		

		done
	done
		
	wait
	
	rm -r workspace-*/RAiSD_Grid.* # TODO check if RAiSD-AI does it now
	
	running=0

	#Sweep runs
	
	for wi in "${window[@]}"; do
		
		for ip in "${ips1[@]}"; do

			for ((iter=1; iter<=iters; iter++)); do
	
				curnameModel=${model}-win${wi}-ips${ip}-iter${iter}
				curnameModelTest=ModelTest-${curnameModel}
				
				cd workspace-${curnameModel}						

				for ipTe in "${ips2[@]}"; do
				
					curnameTestRun=ScanTest-${curnameModel}-ipsTE${ipTe}
					
					neutralRunName=${curnameTestRun}-neut
		
					fprThresholdMU=$(grep " mu " RAiSD_Info.$neutralRunName | grep min | awk -F: '{print $2}' | awk '{print $1}')
					echo $fprThresholdMU
					fprThresholdPCL0=$(grep " selsweep" RAiSD_Info.$neutralRunName | grep min | awk -F: '{print $2}' | awk '{print $1}')
					echo $fprThresholdPCL0
					fprThresholdPCL1=$(grep " muvar^selsweep" RAiSD_Info.$neutralRunName | grep min | awk -F: '{print $2}' | awk '{print $1}')
					echo $fprThresholdPCL1	

		
					$exec -n ${curnameTestRun}-swe -mdl ../RAiSD_Model.${curnameModel} -f -op SWP-SCN -I ../${datasetTestSelSweep} -L ${length} -frm -T ${target} -d 50000 -G ${grid} -pci 1 1 -O -k 0.05 -l 3 mu=${fprThresholdMU} pcl0=${fprThresholdPCL0} pcl1=${fprThresholdPCL1} "$gpuScanString" &
		
					cd ..
					
					((running++))	
					
					if (( running >= MAX_PARALLEL_RUNS )); then
					    wait -n 
					    ((running--))
					fi
				done
			done		

		done
	done
		
	wait
	
	rm -r workspace-*/RAiSD_Grid.* # TODO check if RAiSD-AI does it now
	
fi

#=====================================================================================#
#=====================================================================================#
exit

