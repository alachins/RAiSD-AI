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

RSDGrid_t * RSDGrid_new (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDCommandLine->gridSize==-1) // && RSDCommandLine->opCode!=OP_CREATE_IMAGES)
		return NULL;
		
	RSDGrid_t * RSDGrid = (RSDGrid_t *)malloc(sizeof(RSDGrid_t));
	assert(RSDGrid!=NULL);
	
	RSDGrid->sizeAcc = 0;
	RSDGrid->size = -1;
	RSDGrid->firstPoint = 0.0;
	RSDGrid->pointOffset = 0.0;	
	strncpy(RSDGrid->destinationPath, "\0", STRING_SIZE);

	return RSDGrid;
}

void RSDGrid_free (RSDGrid_t * RSDGrid)
{
	if(RSDGrid==NULL)
		return;
	
	free(RSDGrid);
	
	RSDGrid=NULL;
}

void RSDGrid_setChunkGridSize (RSDGrid_t * RSDGrid, RSDDataset_t * RSDDataset, RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, int setDone)
{
	assert(RSDGrid!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(setDone==0 || setDone==1); // setDone=1 when the last chunk of the set is processed
	
	assert(RSDDataset->setRegionLength!=0ull); 
	
	double chunkFraction = (RSDChunk->sitePosition[(int)RSDChunk->chunkSize-RSDMuStat->windowSize/2-1] - RSDChunk->sitePosition[RSDMuStat->windowSize/2]) / (double)RSDDataset->setRegionLength; 
	assert(chunkFraction<=1.0); 
		
	int64_t chunkGridSize = chunkFraction * RSDCommandLine->gridSize;
	
	// if many chunks per set and small (set) grid size, several chunks get no point and the last chunk gets many
	if(chunkGridSize==0)
		chunkGridSize=1;
	
	if(RSDChunk->chunkID==0)
		RSDGrid->sizeAcc = 0;
	
	if(setDone==1) 
		chunkGridSize = RSDCommandLine->gridSize - RSDGrid->sizeAcc;			
		
	RSDGrid->size = chunkGridSize;
	RSDGrid->sizeAcc += chunkGridSize;
	
	if(RSDGrid->sizeAcc>RSDCommandLine->gridSize)
	{
		fprintf(stderr, "\nERROR: A grid-size error occurred! Increase the grid size. \n\n"); // this is related to the out-of-core algorithm
		exit(0);	
	}	
	
	assert(RSDGrid->sizeAcc<=RSDCommandLine->gridSize);
	
	if(setDone==1)
		assert(RSDCommandLine->gridSize==RSDGrid->sizeAcc);
}

void RSDGrid_setFirstGridPointPositionAndOffset (RSDGrid_t * RSDGrid, RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDGrid!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDCommandLine!=NULL);
	
	assert(RSDGrid->size!=-1); // this fails if setChunkGridSize is not called before this function	

	int stepsLeft = 0;
	int stepsRight = 0;
	
	RSDGridPoint_getSteps (RSDCommandLine, &stepsLeft, &stepsRight);
		
	int windowStep = RSDCommandLine->imageWindowStep; // grid is applied on bp positions, step refers to snps
	
	int firstValidSNP = stepsLeft * windowStep + (RSDMuStat->windowSize/2);
	int lastValidSNP  = ((int)RSDChunk->chunkSize-1)-(stepsRight*windowStep)-(RSDMuStat->windowSize/2-1);
	
	double firstValidPosition = RSDChunk->sitePosition[firstValidSNP];
	double lastValidPosition  = RSDChunk->sitePosition[lastValidSNP];		

	RSDGrid->pointOffset = (lastValidPosition-firstValidPosition)/((double)RSDGrid->size+1.0);
	RSDGrid->firstPoint  = firstValidPosition;
}

void RSDGrid_init (RSDGrid_t * RSDGrid, RSDDataset_t * RSDDataset, RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, int setDone)
{
	assert(RSDGrid!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(setDone==0 || setDone==1);
	
	RSDGrid_setChunkGridSize (RSDGrid, RSDDataset, RSDChunk, RSDMuStat, RSDCommandLine, setDone);
	
	RSDGrid_setFirstGridPointPositionAndOffset (RSDGrid, RSDChunk, RSDMuStat, RSDCommandLine);	
}

void RSDGrid_makeDirectory (RSDGrid_t * RSDGrid, RSDCommandLine_t * RSDCommandLine, RSDImage_t * RSDImage)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDGrid==NULL)
		return;
		
	if((RSDCommandLine->opCode!=OP_USE_CNN) && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
		return;
		
	if(RSDCommandLine->opCode==OP_CREATE_IMAGES)
	{
		if(RSDCommandLine->trnObjDetection!=1)
			return;
	}
	
	assert(RSDCommandLine->opCode==OP_USE_CNN || (RSDCommandLine->opCode==OP_CREATE_IMAGES && RSDCommandLine->trnObjDetection==1));
			
	assert(RSDGrid!=NULL);
	assert(RSDImage!=NULL);
	
	char tstring [STRING_SIZE];
	int ret = 0;
	
	if(RSDCommandLine->opCode==OP_USE_CNN)
	{
		if(RSDCommandLine->forceRemove)
		{
			strcpy(tstring, "rm -r ");
			strcat(tstring, "RAiSD_Grid."); 
			strcat(tstring, RSDCommandLine->runName);
			strcat(tstring, " 2>/dev/null");
			
			ret = system(tstring);
			assert(ret!=-1);
		}
			
		strcpy(tstring, "mkdir ");
		strcat(tstring, "RAiSD_Grid.");
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, " 2>/dev/null");
		
		ret = system(tstring);
		assert(ret!=-1);
		
		//TODO threads
		/**********
		strcpy(tstring, "mkdir ");
		strcat(tstring, "RAiSD_Grid.");
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, "/T0 2>/dev/null");
		
		ret = system(tstring);
		assert(ret!=-1);
		
		strcpy(tstring, "mkdir ");
		strcat(tstring, "RAiSD_Grid.");
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, "/T1 2>/dev/null");
		
		ret = system(tstring);
		assert(ret!=-1);
		**********/	
		
		strncpy(RSDGrid->destinationPath, "\0", STRING_SIZE);
		strcat(RSDGrid->destinationPath, "RAiSD_Grid.");
		strcat(RSDGrid->destinationPath, RSDCommandLine->runName);
		strcat(RSDGrid->destinationPath, "/");
	}
	else
		strncpy(RSDGrid->destinationPath, RSDImage->destinationPath, STRING_SIZE);

}

void RSDGrid_cleanDirectory (RSDGrid_t * RSDGrid, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDGrid!=NULL);
	assert(RSDCommandLine!=NULL);
	
	char tstring [STRING_SIZE];
	int ret = 0;	

	strcpy(tstring, "rm ");
	strcat(tstring, "RAiSD_Grid."); 
	strcat(tstring, RSDCommandLine->runName);
	strcat(tstring, "/* 2>/dev/null");
	
	ret = system(tstring);
	assert(ret!=-1);
}

int validGridPosition (RSDCommandLine_t * RSDCommandLine, uint64_t pos)
{
	assert(RSDCommandLine!=NULL);
	
	int isValid = 0;
	
	if(RSDCommandLine->gridRngLeBor!=0 && RSDCommandLine->gridRngRiBor!=0)
	{
		if(pos>=RSDCommandLine->gridRngLeBor && pos <= RSDCommandLine->gridRngRiBor)
			isValid=1;	
	}
	else
		isValid=1;
		
	return isValid;
}

void RSDGrid_processChunk (RSDGrid_t * RSDGrid, RSDImage_t * RSDImage, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, RSDResults_t * RSDResults)
{
	/* This function is called per chunk, grid points are defined per chunk, score indices are defined per set! */
	
	assert(RSDGrid!=NULL);
	assert(RSDResults!=NULL);
	
	if(RSDGrid->size<1)
		return;		
	
	int i=-1;
	
	RSDMuStat_storeOutputConfigure(RSDCommandLine);
	
	for(i=0;i<RSDGrid->size;i++)
	{
		RSDMuStat->currentScoreIndex++;
		assert(RSDMuStat->currentScoreIndex<RSDCommandLine->gridSize);
		
		uint64_t pos = (uint64_t)RSDGrid->firstPoint+i*RSDGrid->pointOffset;		
		
		if(validGridPosition(RSDCommandLine, pos))
		{		 
			RSDGridPoint_t * RSDGridPoint = RSDGridPoint_compute((void*)RSDImage, RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RAiSD_Info_FP,  
								   	     (double)pos, 
								   	     RSDGrid->destinationPath, 
								   	     RSDMuStat->currentScoreIndex,
								   	     RSDResults->setsTotal-1);

			RSDResults_setGridPoint (RSDResults, RSDMuStat->currentScoreIndex, RSDGridPoint);
		}		 
	}		
}
#endif
