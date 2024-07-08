/*  
 *  RAiSD, Raised Accuracy in Sweep Detection
 *
 *  Copyright January 2017 by Nikolaos Alachiotis and Pavlos Pavlidis
 *
 *  This program is free software; you may redistribute it and/or modify its
 *  under the terms of the GNU General Public License as published by the Free
 *  Software Foundation; either version 2 of the License, or (at your option)
 *  any later version.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 *  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 *  for more details.
 *
 *  For any other enquiries send an email to
 *  Nikolaos Alachiotis (n.alachiotis@gmail.com)
 *  Pavlos Pavlidis (pavlidisp@gmail.com)  
 *  
 */
 
#ifdef _RSDAI

#include "RAiSD.h"

RSDResults_t * RSDResults_new (RSDCommandLine_t * RSDCommandLine)
{
	// RSDResults is only used for grid-based scans (mu-stat or mu-stat+CNN)
			
	if(RSDCommandLine->gridSize==-1)
		return NULL;
		
	RSDResults_t * RSDResults = (RSDResults_t *)rsd_malloc(sizeof(RSDResults_t));
	assert(RSDResults!=NULL);
	
	RSDResults->setsTotal = 0;
	RSDResults->setID = NULL;
	RSDResults->setGridSize = -1; 
	RSDResults->gridPointSize = NULL;
	RSDResults->gridPointData = NULL;	
	RSDResults->muVarMax = 0.0f; 
	RSDResults->muSfsMax = 0.0f; 
	RSDResults->muLdMax = 0.0f; 
	RSDResults->muMax = 0.0f;
	RSDResults->nnPositiveClass0Max = 0.0f;
	RSDResults->nnPositiveClass1Max = 0.0f;	
	RSDResults->muVarMaxLoc = -1.0;
	RSDResults->muSfsMaxLoc = -1.0;
	RSDResults->muLdMaxLoc = -1.0; 
	RSDResults->muMaxLoc = -1.0;
	RSDResults->nnPositiveClass0MaxLoc = -1.0;
	RSDResults->nnPositiveClass1MaxLoc = -1.0;
		
	return RSDResults;
}

void RSDResults_setGridSize (RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine)
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDCommandLine!=NULL);
	
	RSDResults->setGridSize = RSDCommandLine->gridSize;
	
	assert(RSDResults->setGridSize>=1);
}

void RSDResults_incrementSetCounter (RSDResults_t * RSDResults)
{
	if(RSDResults==NULL)
		return;
	
	RSDResults->setsTotal++;
	
	RSDResults->setID = rsd_realloc (RSDResults->setID, sizeof(char*)*((unsigned long)RSDResults->setsTotal));
	RSDResults->setID[RSDResults->setsTotal-1] = rsd_malloc (sizeof(char)*STRING_SIZE);
	RSDResults->gridPointSize = rsd_realloc(RSDResults->gridPointSize, sizeof(int64_t)*((size_t)RSDResults->setsTotal*RSDResults->setGridSize));
	RSDResults->gridPointData = rsd_realloc(RSDResults->gridPointData, sizeof(RSDGridPoint_t*)*((unsigned long)RSDResults->setsTotal*RSDResults->setGridSize));
		
	assert(RSDResults->gridPointSize!=NULL);
	assert(RSDResults->gridPointData!=NULL);
	
	int64_t i=-1;
	int64_t sta = (RSDResults->setsTotal-1)*RSDResults->setGridSize;
	int64_t sto = sta + RSDResults->setGridSize - 1; 
	
	for(i=sta;i<=sto;i++)
	{
		RSDResults->gridPointSize[i]=-1;
		RSDResults->gridPointData[i]=NULL;
	}			
}

void RSDResults_free (RSDResults_t * RSDResults)
{
	if(RSDResults==NULL)
		return;
			
	int i;
	
	if(RSDResults->setID!=NULL)
	{
		for(i=0;i<RSDResults->setsTotal;i++)
		{
			if(RSDResults->setID[i]!=NULL)
			{
				free(RSDResults->setID[i]);
				RSDResults->setID[i] = NULL;
			}
		}
		
		free(RSDResults->setID);
		RSDResults->setID=NULL;
	}
	
	if(RSDResults->gridPointSize!=NULL)
	{
		free(RSDResults->gridPointSize);
		RSDResults->gridPointSize=NULL;
	}	
	
	if(RSDResults->gridPointData!=NULL)
	{
		for(i=0;i<RSDResults->setsTotal*RSDResults->setGridSize;i++)
		{
			RSDGridPoint_free(RSDResults->gridPointData[i]);
		}
		free(RSDResults->gridPointData);
		RSDResults->gridPointData=NULL; 
	}		

	free(RSDResults);
	RSDResults = NULL;
}

void RSDResults_saveSetID (RSDResults_t * RSDResults, RSDDataset_t * RSDDataset)
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDDataset!=NULL);
	
	strcpy(RSDResults->setID[RSDResults->setsTotal-1], RSDDataset->setID);
}

void RSDResults_setGridPointSize (RSDResults_t * RSDResults, int64_t gridPointIndex, int64_t gridPointSize)
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDResults->gridPointSize!=NULL);
	assert(RSDResults->setsTotal*RSDResults->setGridSize>gridPointIndex);
	assert(gridPointIndex>=0);
	
	assert(RSDResults->gridPointSize[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex]==-1);

	RSDResults->gridPointSize[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex] = gridPointSize;		
}

void RSDResults_setGridPoint (RSDResults_t * RSDResults, int64_t gridPointIndex, RSDGridPoint_t * RSDGridPoint)
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDResults->gridPointSize!=NULL);
	assert(RSDResults->gridPointData!=NULL);
	assert(gridPointIndex<RSDResults->setsTotal*RSDResults->setGridSize);
	assert(gridPointIndex>=0);
	
	assert(RSDResults->gridPointSize[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex]==-1);
	assert(RSDResults->gridPointData[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex]==NULL);
	
	if(RSDGridPoint==NULL)
	{
		RSDGridPoint_t * RSDGridPointInv = RSDGridPoint_new ();
		RSDResults->gridPointSize[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex] = RSDGridPointInv->size;
		RSDResults->gridPointData[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex] = RSDGridPointInv;
	}
	else
	{
		RSDResults->gridPointSize[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex] = RSDGridPoint->size;
		RSDResults->gridPointData[(RSDResults->setsTotal-1)*RSDResults->setGridSize+gridPointIndex] = RSDGridPoint;
	}		
}

void RSDResults_load (RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine) 
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDCommandLine!=NULL);
	
	char reportPath[STRING_SIZE], rline[STRING_SIZE]; 	

	strncpy(reportPath, "tempOutputFolder/PredResults.txt", STRING_SIZE);
	
	FILE * fp = fopen(reportPath, "r");
	assert(fp!=NULL);
	    		
    	int setIndex=-1, gridPointIndex=-1, gridPointDataIndex=-1;
    		
	while(fgets(rline, STRING_SIZE, fp)!=NULL) 
	{
    		char * imgName = strtok(rline, " ");
    		char * imgClass = strtok(NULL, " ");
    		assert(imgClass!=NULL);
    		
    		char * imgProb0 = strtok(NULL, " "); // class 0
    		assert(imgProb0!=NULL);
    		char * imgProb1 = strtok(NULL, " "); // class 1
    		
    		getIndicesFromImageName(imgName, &setIndex, &gridPointIndex, &gridPointDataIndex);
    		    		
    		RSDGridPoint_t * RSDGridPoint = RSDResults->gridPointData[setIndex*RSDResults->setGridSize+gridPointIndex];
    		
    		int positiveClassIndex = RSDCommandLine->positiveClassIndex[0]; 
    		
    		RSDGridPoint->nnPositiveClass0[gridPointDataIndex] = positiveClassIndex==0?(float)atof(imgProb0):(float)atof(imgProb1);
    		assert(RSDGridPoint->nnPositiveClass0[gridPointDataIndex]>=0.0 && RSDGridPoint->nnPositiveClass0[gridPointDataIndex]<=1.0);
    		
    		RSDGridPoint_calcCompositeScore (RSDGridPoint, gridPointDataIndex); // stores in nnPositiveClass1
	}
	
	fclose(fp);	
	
	exec_command ("rm -r tempOutputFolder");
}

void RSDResults_load_2x2 (RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine)
{
	if(RSDResults==NULL)
		return;
		
	assert(RSDCommandLine!=NULL);
	
	char reportPath[STRING_SIZE], rline[STRING_SIZE];
	char * imgProb[CLA_SWEEPNETRECOMB]; 
	
	int i=-1, setIndex=-1, gridPointIndex=-1, gridPointDataIndex=-1;

	strncpy(reportPath, "tempOutputFolder/PredResults.txt", STRING_SIZE);
	
	FILE * fp = fopen(reportPath, "r");
	assert(fp!=NULL);
	
	while(fgets(rline, STRING_SIZE, fp)!=NULL) 
	{
    		char * imgName = strtok(rline, " ");	    		
    		char * imgClassRows = strtok(NULL, " ");
    		assert(imgClassRows!=NULL);
	
    		char * imgClassCols = strtok(NULL, " ");
    		assert(imgClassCols!=NULL);
    		
    		for(i=0;i<CLA_SWEEPNETRECOMB;i++)
    		{
    			imgProb[i] = strtok(NULL, " ");
	    		assert(imgProb[i]!=NULL);     		
    		}      		

    		getIndicesFromImageName(imgName, &setIndex, &gridPointIndex, &gridPointDataIndex);
    		
    		RSDGridPoint_t * RSDGridPoint = RSDResults->gridPointData[setIndex*RSDResults->setGridSize+gridPointIndex];
    		
    		int positiveClassIndex0 = RSDCommandLine->positiveClassIndex[0];
    		int positiveClassIndex1 = RSDCommandLine->positiveClassIndex[1];    		    		
    		
	    	RSDGridPoint->nnPositiveClass0[gridPointDataIndex] = (float)atof(imgProb[positiveClassIndex0]);	    					
	   	RSDGridPoint->nnPositiveClass1[gridPointDataIndex] = (float)atof(imgProb[positiveClassIndex1]);	  
	}
	
	fclose(fp);	
	
	exec_command ("rm -r tempOutputFolder");
}

void RSDResults_resetMaxScores (RSDResults_t * RSDResults)
{
	assert(RSDResults!=NULL);	
	
	RSDResults->muVarMax = 0.0f; 
	RSDResults->muSfsMax = 0.0f;
	RSDResults->muLdMax = 0.0f; 
	RSDResults->muMax = 0.0f;
	RSDResults->nnPositiveClass0Max = -1.0f;
	RSDResults->nnPositiveClass1Max = -1.0f;	

	RSDResults->muVarMaxLoc = 0.0;
	RSDResults->muSfsMaxLoc = 0.0;
	RSDResults->muLdMaxLoc = 0.0; 
	RSDResults->muMaxLoc = 0.0;
	RSDResults->nnPositiveClass0MaxLoc = 0.0;
	RSDResults->nnPositiveClass1MaxLoc = 0.0;	
}

void RSDResults_getMaxScores (RSDResults_t * RSDResults, RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDResults!=NULL);
	assert(RSDGridPoint!=NULL);
	assert(RSDCommandLine!=NULL);
	
	// MuVar Max
	if (RSDGridPoint->muVarReduced > RSDResults->muVarMax)
	{
		RSDResults->muVarMax = RSDGridPoint->muVarReduced;
		RSDResults->muVarMaxLoc = RSDGridPoint->positionReduced;
	}
		
	// MuSfs Max
	if (RSDGridPoint->muSfsReduced > RSDResults->muSfsMax)
	{
		RSDResults->muSfsMax = RSDGridPoint->muSfsReduced;
		RSDResults->muSfsMaxLoc = RSDGridPoint->positionReduced;
	}
	
	// MuLd Max
	if (RSDGridPoint->muLdReduced > RSDResults->muLdMax)
	{
		RSDResults->muLdMax = RSDGridPoint->muLdReduced;
		RSDResults->muLdMaxLoc = RSDGridPoint->positionReduced;
	}
	
	// Mu Max
	if (RSDGridPoint->muReduced > RSDResults->muMax)
	{
		RSDResults->muMax = RSDGridPoint->muReduced;
		RSDResults->muMaxLoc = RSDGridPoint->positionReduced;
	}
	
	if(RSDCommandLine->opCode == OP_USE_CNN)
	{
		// nnPositiveClass0 Max
		if (RSDGridPoint->nnPositiveClass0Reduced > RSDResults->nnPositiveClass0Max)
		{
			RSDResults->nnPositiveClass0Max = RSDGridPoint->nnPositiveClass0Reduced;
			RSDResults->nnPositiveClass0MaxLoc = RSDGridPoint->positionReduced;
		}
		
		// nnPositiveClass1 Max
		if (RSDGridPoint->nnPositiveClass1Reduced > RSDResults->nnPositiveClass1Max)
		{
			RSDResults->nnPositiveClass1Max = RSDGridPoint->nnPositiveClass1Reduced;
			RSDResults->nnPositiveClass1MaxLoc = RSDGridPoint->positionReduced;
		}	
	}
}

void RSDResults_processSet (RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine, RSDMuStat_t * RSDMuStat, int setIndex, int gridSize, int gridPointOffset)
{
	assert(RSDResults!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(RSDMuStat!=NULL);
	
	if(gridPointOffset==0) // processing first chunk in set
		RSDResults_resetMaxScores (RSDResults); 	
	
	for(int j=0;j<gridSize;j++) 
	{
		RSDGridPoint_t * RSDGridPoint = RSDResults->gridPointData[setIndex*RSDResults->setGridSize+j+gridPointOffset]; // the gridpointoffset is needed to work per chunk correctly	
		assert(RSDGridPoint!=NULL);	

		RSDGridPoint_reduce (RSDGridPoint, RSDCommandLine, 0 + RSDCommandLine->gridPointReductionMax); //0: avg, 1: max 		
		RSDResults_getMaxScores (RSDResults, RSDGridPoint, RSDCommandLine);		
		RSDGridPoint_write2File (RSDGridPoint, RSDMuStat);
	}
}

void RSDResults_writeOutput (RSDResults_t * RSDResults, RSDDataset_t * RSDDataset, RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, int setIndex, FILE * fpOut)
{
	/* this function prints to stdout and info file when CNN is used */
	
	assert(RSDResults!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(setIndex>=0);
	assert(fpOut!=NULL);	
	
	static int slen[13]={0};	
	char nnPositiveClass0Label[STRING_SIZE], nnPositiveClass1Label[STRING_SIZE]; 
	
	slen[0] = getStringLengthString (slen[0], RSDDataset->setID); 
	slen[1] = getStringLengthDouble0 (slen[1], RSDResults->muVarMaxLoc); 
	slen[2] = getStringLengthExp (slen[2], RSDResults->muVarMax);	
	slen[3] = getStringLengthDouble0 (slen[3], RSDResults->muSfsMaxLoc);
	slen[4] = getStringLengthExp (slen[4], RSDResults->muSfsMax);
	slen[5] = getStringLengthDouble0 (slen[5], RSDResults->muLdMaxLoc);	
	slen[6] = getStringLengthExp (slen[6], RSDResults->muLdMax);
	slen[7] = getStringLengthDouble0 (slen[7], RSDResults->muMaxLoc);
	slen[8] = getStringLengthExp (slen[8], RSDResults->muMax);
	slen[9] = getStringLengthDouble0 (slen[9], RSDResults->nnPositiveClass0MaxLoc); 
	slen[10] = getStringLengthExp (slen[10], RSDResults->nnPositiveClass0Max); 
	slen[11] = getStringLengthDouble0 (slen[11], RSDResults->nnPositiveClass1MaxLoc); 
	slen[12] = getStringLengthExp (slen[12], RSDResults->nnPositiveClass1Max); 
	
	RSDNeuralNetwork_getColumnHeaders (RSDNeuralNetwork, RSDCommandLine, nnPositiveClass0Label, nnPositiveClass1Label);		
	
	fprintf(fpOut, " %d: Set %*s - muVar %*.0f %*.3e | muSFS %*.0f %*.3e | muLD %*.0f %*.3e | mu %*.0f %*.3e | %s %*.0f %*.3e | %s %*.0f %*.3e \n", 
			setIndex, slen[0], RSDDataset->setID, slen[1], (double)RSDResults->muVarMaxLoc, slen[2], (double)RSDResults->muVarMax, 
							      slen[3], (double)RSDResults->muSfsMaxLoc, slen[4], (double)RSDResults->muSfsMax,
							      slen[5], (double)RSDResults->muLdMaxLoc, slen[6], (double)RSDResults->muLdMax,
							      slen[7], (double)RSDResults->muMaxLoc, slen[8], (double)RSDResults->muMax, 
				       			      nnPositiveClass0Label, slen[9], (double)RSDResults->nnPositiveClass0MaxLoc, slen[10], (double)RSDResults->nnPositiveClass0Max,
							      nnPositiveClass1Label, slen[11], (double)RSDResults->nnPositiveClass1MaxLoc, slen[12], (double)RSDResults->nnPositiveClass1Max);
	
	fflush(fpOut);
}

void RSDResults_process (RSDResults_t * RSDResults, RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, RSDDataset_t * RSDDataset, RSDMuStat_t * RSDMuStat, RSDCommonOutliers_t * RSDCommonOutliers, RSDEval_t * RSDEval)
{
	/* this function is only called when a CNN is used for scanning */
	
	assert(RSDResults!=NULL);
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDCommonOutliers!=NULL);
	
	if(RSDCommandLine->gridSize==-1)
		return;
	
	for(int setIndex=0;setIndex<RSDResults->setsTotal;setIndex++)
	{
		strncpy(RSDDataset->setID, RSDResults->setID[setIndex], STRING_SIZE-1);
		
		RSDMuStat_setReportNamePerSet (RSDMuStat, RSDCommandLine, RAiSD_Info_FP, RSDDataset, RSDCommonOutliers);

		assert(RSDMuStat->reportFP!=NULL);

		if(RSDCommandLine->setSeparator)
			fprintf(RSDMuStat->reportFP, "// %s\n", RSDResults->setID[setIndex]);			
			
		RSDResults_processSet (RSDResults, RSDCommandLine, RSDMuStat, setIndex, RSDResults->setGridSize, 0);
		
		RSDPlot_createPlot (RSDCommandLine, RSDDataset, RSDMuStat, RSDCommonOutliers, RSDPLOT_BASIC_MU, (void*)RSDNeuralNetwork);
		
		RSDResults_writeOutput (RSDResults, RSDDataset, RSDNeuralNetwork, RSDCommandLine, setIndex, RAiSD_Info_FP);				

		RSDEval_calculateDetectionMetrics (RSDEval, (void*)RSDResults);
		
		if(RSDCommandLine->displayProgress==1)
			RSDResults_writeOutput (RSDResults, RSDDataset, RSDNeuralNetwork, RSDCommandLine, setIndex, stdout);				
	}
}
#endif
