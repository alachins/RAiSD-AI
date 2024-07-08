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

void (*RSDGridPoint_write2File) (RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat);

RSDGridPoint_t * RSDGridPoint_new (void)
{
	RSDGridPoint_t * RSDGridPoint = (RSDGridPoint_t *) rsd_malloc (sizeof(RSDGridPoint_t));
	assert(RSDGridPoint!=NULL);
	
	RSDGridPoint->size=0;
	RSDGridPoint->position = NULL;
	
	RSDGridPoint->nnPositiveClass0 = NULL;
	RSDGridPoint->nnPositiveClass1 = NULL;
	RSDGridPoint->nnScores2 = NULL;
	RSDGridPoint->nnScores3 = NULL;
	RSDGridPoint->muVar = NULL;
	RSDGridPoint->muSfs = NULL;
	RSDGridPoint->muLd = NULL;
	RSDGridPoint->mu = NULL;
	
	RSDGridPoint->nnPositiveClass0Reduced = 0.0;
	RSDGridPoint->nnPositiveClass1Reduced = 0.0;
	RSDGridPoint->nnScore2Final = 0.0;
	RSDGridPoint->nnScore3Final = 0.0;
	RSDGridPoint->muVarReduced = 0.0;
	RSDGridPoint->muSfsReduced = 0.0;
	RSDGridPoint->muLdReduced = 0.0;
	RSDGridPoint->muReduced = 0.0;
	
	RSDGridPoint->positionReduced = -1.0;

	RSDGridPoint->finalRegionCenter = -1.0;
	RSDGridPoint->finalRegionStart = -1.0;
	RSDGridPoint->finalRegionEnd = -1.0;
	RSDGridPoint->finalRegionScore = 0.0f;
	
	return RSDGridPoint;		
}

void RSDGridPoint_addNewPosition (RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine, double pos)
{
	if(RSDGridPoint==NULL)
		return;
		
	assert(pos>=0.0);
	
	RSDGridPoint->size++;	
	
	RSDGridPoint->position = rsd_realloc (RSDGridPoint->position, sizeof(double)*RSDGridPoint->size);
	assert(RSDGridPoint->position!=NULL);
	
	RSDGridPoint->muVar = rsd_realloc (RSDGridPoint->muVar, sizeof(float)*RSDGridPoint->size);
	assert(RSDGridPoint->muVar!=NULL);
	
	RSDGridPoint->muSfs = rsd_realloc (RSDGridPoint->muSfs, sizeof(float)*RSDGridPoint->size);
	assert(RSDGridPoint->muSfs!=NULL);
	
	RSDGridPoint->muLd = rsd_realloc (RSDGridPoint->muLd, sizeof(float)*RSDGridPoint->size);
	assert(RSDGridPoint->muLd!=NULL);
	
	RSDGridPoint->mu = rsd_realloc (RSDGridPoint->mu, sizeof(float)*RSDGridPoint->size);
	assert(RSDGridPoint->mu!=NULL);	
	
	RSDGridPoint->position[RSDGridPoint->size-1] = pos;
	RSDGridPoint->muVar[RSDGridPoint->size-1] = 0.0;
	RSDGridPoint->muSfs[RSDGridPoint->size-1] = 0.0;
	RSDGridPoint->muLd[RSDGridPoint->size-1] = 0.0;
	RSDGridPoint->mu[RSDGridPoint->size-1] = 0.0;	
	
	if(RSDCommandLine->opCode == OP_USE_CNN) 
	{
		RSDGridPoint->nnPositiveClass0 = rsd_realloc (RSDGridPoint->nnPositiveClass0, sizeof(float)*RSDGridPoint->size);
		assert(RSDGridPoint->nnPositiveClass0!=NULL);
		
		RSDGridPoint->nnPositiveClass1 = rsd_realloc (RSDGridPoint->nnPositiveClass1, sizeof(float)*RSDGridPoint->size);
		assert(RSDGridPoint->nnPositiveClass1!=NULL);
		
		RSDGridPoint->nnPositiveClass0[RSDGridPoint->size-1] = 0.0;
		RSDGridPoint->nnPositiveClass1[RSDGridPoint->size-1] = 0.0;
		
		if(!strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
		{
			RSDGridPoint->nnScores2 = rsd_realloc (RSDGridPoint->nnScores2, sizeof(float)*RSDGridPoint->size);
			assert(RSDGridPoint->nnScores2!=NULL);
		
			RSDGridPoint->nnScores3 = rsd_realloc (RSDGridPoint->nnScores3, sizeof(float)*RSDGridPoint->size);
			assert(RSDGridPoint->nnScores3!=NULL);
		
			RSDGridPoint->nnScores2[RSDGridPoint->size-1] = 0.0;
			RSDGridPoint->nnScores3[RSDGridPoint->size-1] = 0.0;
		}	
	}
}

void RSDGridPoint_free (RSDGridPoint_t * RSDGridPoint)
{
	if(RSDGridPoint==NULL)
		return;
	
	if(RSDGridPoint->position!=NULL)
	{
		free(RSDGridPoint->position);
		RSDGridPoint->position=NULL;
	}
	
	if(RSDGridPoint->nnPositiveClass0!=NULL)
	{
		free(RSDGridPoint->nnPositiveClass0);
		RSDGridPoint->nnPositiveClass0=NULL;
	}
	
	if(RSDGridPoint->nnPositiveClass1!=NULL)
	{
		free(RSDGridPoint->nnPositiveClass1);
		RSDGridPoint->nnPositiveClass1=NULL;
	}
	
	if(RSDGridPoint->nnScores2!=NULL)
	{
		free(RSDGridPoint->nnScores2);
		RSDGridPoint->nnScores2=NULL;
	}
	
	if(RSDGridPoint->nnScores3!=NULL)
	{
		free(RSDGridPoint->nnScores3);
		RSDGridPoint->nnScores3=NULL;
	}	
	
	if(RSDGridPoint->muVar!=NULL)
	{
		free(RSDGridPoint->muVar);
		RSDGridPoint->muVar=NULL;
	}
	
	if(RSDGridPoint->muSfs!=NULL)
	{
		free(RSDGridPoint->muSfs);
		RSDGridPoint->muSfs=NULL;
	}
	
	if(RSDGridPoint->muLd!=NULL)
	{
		free(RSDGridPoint->muLd);
		RSDGridPoint->muLd=NULL;
	}
	
	if(RSDGridPoint->mu!=NULL)
	{
		free(RSDGridPoint->mu);
		RSDGridPoint->mu=NULL;
	}
	
	free(RSDGridPoint);
	RSDGridPoint = NULL;
}

void RSDGridPoint_resetFinalScores (RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine) 
{
	assert(RSDGridPoint!=NULL);
	assert(RSDCommandLine!=NULL);
	
	RSDGridPoint->muVarReduced = 0.0;
	RSDGridPoint->muSfsReduced = 0.0;
	RSDGridPoint->muLdReduced = 0.0;
	RSDGridPoint->muReduced = 0.0;		

	if(RSDCommandLine->opCode == OP_USE_CNN)
	{	
		RSDGridPoint->nnPositiveClass0Reduced = 0.0;
		RSDGridPoint->nnPositiveClass1Reduced = 0.0;
	}
}

void RSDGridPoint_reduce (RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine, int op) // op=0->avg, op=1->max
{
	assert(RSDGridPoint!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(op==0 || op==1);
	
	RSDGridPoint_resetFinalScores (RSDGridPoint, RSDCommandLine);
	
	if(RSDGridPoint->size==0) // invalid grid point
		return;
	
	assert(RSDGridPoint->position!=NULL);
	
	if(op==0) /* average */
	{
		RSDGridPoint->positionReduced = (double)RSDGridPoint->position[0];
		
		for (int k = 0; k<(int)RSDGridPoint->size;k++)
		{
			assert(RSDGridPoint->positionReduced==(double)RSDGridPoint->position[k]);
			
			RSDGridPoint->muVarReduced += (double)RSDGridPoint->muVar[k];
			RSDGridPoint->muSfsReduced += (double)RSDGridPoint->muSfs[k];
			RSDGridPoint->muLdReduced  += (double)RSDGridPoint->muLd[k];
			RSDGridPoint->muReduced    += (double)RSDGridPoint->mu[k];
			
			if(RSDCommandLine->opCode == OP_USE_CNN)
			{
				RSDGridPoint->nnPositiveClass0Reduced += (double)RSDGridPoint->nnPositiveClass0[k];				
				RSDGridPoint->nnPositiveClass1Reduced += (double)RSDGridPoint->nnPositiveClass1[k];								
			}
		}
		
		RSDGridPoint->muVarReduced /= (double)RSDGridPoint->size;
		RSDGridPoint->muSfsReduced /= (double)RSDGridPoint->size;
		RSDGridPoint->muLdReduced  /= (double)RSDGridPoint->size;
		RSDGridPoint->muReduced    /= (double)RSDGridPoint->size;
		
		if(RSDCommandLine->opCode == OP_USE_CNN)
		{
			RSDGridPoint->nnPositiveClass0Reduced /= (double)RSDGridPoint->size;
			RSDGridPoint->nnPositiveClass1Reduced /= (double)RSDGridPoint->size;
		}
	}
	else /* max */
	{
		RSDGridPoint->positionReduced = (double)RSDGridPoint->position[0];
		
		for (int k = 0; k<(int)RSDGridPoint->size;k++)
		{
			assert(RSDGridPoint->positionReduced==(double)RSDGridPoint->position[k]);			

			RSDGridPoint->muVarReduced = maxd (RSDGridPoint->muVarReduced, (double)RSDGridPoint->muVar[k]);
			RSDGridPoint->muSfsReduced = maxd (RSDGridPoint->muSfsReduced, (double)RSDGridPoint->muSfs[k]);
			RSDGridPoint->muLdReduced  = maxd (RSDGridPoint->muLdReduced, (double)RSDGridPoint->muLd[k]);			
			RSDGridPoint->muReduced    = maxd (RSDGridPoint->muReduced, (double)RSDGridPoint->mu[k]);
			
			if(RSDCommandLine->opCode == OP_USE_CNN)
			{	

				RSDGridPoint->nnPositiveClass0Reduced = maxd (RSDGridPoint->nnPositiveClass0Reduced, (double)RSDGridPoint->nnPositiveClass0[k]);
				RSDGridPoint->nnPositiveClass1Reduced = maxd (RSDGridPoint->nnPositiveClass1Reduced, (double)RSDGridPoint->nnPositiveClass1[k]);
				
				/*
				if((double)RSDGridPoint->nnPositiveClass0[k]>=RSDGridPoint->nnPositiveClass0Reduced)
				{
					RSDGridPoint->nnPositiveClass0Reduced = (double)RSDGridPoint->nnPositiveClass0[k];
					RSDGridPoint->positionReduced = (double)RSDGridPoint->position[k];					
				}
		
				if((double)RSDGridPoint->nnPositiveClass1[k]>=RSDGridPoint->nnPositiveClass1Reduced)
				{
					RSDGridPoint->nnPositiveClass1Reduced = (double)RSDGridPoint->nnPositiveClass1[k];
					RSDGridPoint->positionReduced = (double)RSDGridPoint->position[k];					
				}*/
			}
		}
	}
}

int RSDGridPoint_getTargetSNPIndex (RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, double targetPos)
{
	assert(RSDChunk!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(targetPos>=0.0);
	
	int i = -1, size = (int)RSDChunk->chunkSize, targetSNPIndex = -2, breakFlag = 0, firstTargetSNPIndex = -1, lastTargetSNPIndex = -1;	
	double curDist = -1.0, prvDist = -1.0;
	
	/* Set targetSNPIndex (SNP closest to the target position) */
	
	// valid range in current chunk
	firstTargetSNPIndex = RSDMuStat->windowSize/2;
	lastTargetSNPIndex = size - RSDMuStat->windowSize/2 - 1;
	
	assert(firstTargetSNPIndex>=1);
	
	prvDist = fabs(targetPos - RSDChunk->sitePosition[firstTargetSNPIndex-1]);
	
	// scan valid range in current chunk
	for(i=firstTargetSNPIndex;i<=lastTargetSNPIndex;i++)
	{
		curDist = fabs(targetPos-RSDChunk->sitePosition[i]);
		
		if(curDist<1.0) // there is a SNP at target pos (target pos same as current SNP pos, not using '==' due to floating point)
			return i;

		if(curDist<=prvDist)
			prvDist=curDist;
		else
		{	
			breakFlag=1;
			break;
		}
	}
	
	// scan stops (for-loop breaks) ...  
	if(breakFlag==1)
	{
		if(i==firstTargetSNPIndex) // ... in very first iteration (the target pos before the current chunk) 
			targetSNPIndex = firstTargetSNPIndex;
		else // ... during scan (targetPos in current chunk, right before SNP i)
			targetSNPIndex = i - 1;
	}
	else // scan did not stop (for-loop did not break, targetPost after current chunk)
		return -1; // invalid (continue search in next chunk)
	
	if(RSDChunk->sitePosition[targetSNPIndex]>=targetPos && RSDChunk->sitePosition[targetSNPIndex-1]<targetPos)	
		assert(fabs(targetPos-RSDChunk->sitePosition[targetSNPIndex])<=fabs(targetPos-RSDChunk->sitePosition[targetSNPIndex+1]));
	
	if(RSDChunk->sitePosition[targetSNPIndex]<targetPos && RSDChunk->sitePosition[targetSNPIndex+1]>=targetPos)
		assert(fabs(targetPos-RSDChunk->sitePosition[targetSNPIndex])<=fabs(targetPos-RSDChunk->sitePosition[targetSNPIndex-1]));	
	
	if(RSDCommandLine->imagePositionCenteredEn==1)
	{
		assert(0); // not implemented yet
		
		/* bp-centered window */
		
		// Center first window/image at targetPos
		int snpff = targetSNPIndex;
		int snpll = targetSNPIndex;
			
		while(snpll-snpff<RSDMuStat->windowSize-1)
		{
			if(snpff>=0 && snpll<=size-1)
			{
				if((RSDChunk->sitePosition[snpll]-targetPos)>targetPos-RSDChunk->sitePosition[snpff])
					snpff--;
				else
					snpll++;
			}
			else
				break;	
		}
		
		if(snpff<0)
		{
			snpff=0;
			snpll=RSDMuStat->windowSize-1;
		}
		
		if(snpll>size-1)
		{
			snpll = size-1;
			snpff = snpll-RSDMuStat->windowSize+1;
		}

		assert(snpff>=0);
		assert(snpll<=size-1);		
		assert(snpll-snpff+1==RSDMuStat->windowSize);
			
		targetSNPIndex = snpff + (RSDMuStat->windowSize/2)-1;	
	}	
	
	// validity check	
	if(targetSNPIndex<RSDMuStat->windowSize/2)
		return -1;
		
	if(targetSNPIndex>size-RSDMuStat->windowSize/2)
		return -1;	
		
	return targetSNPIndex;
}

void RSDGridPoint_write2FileFull (RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat)
{
	assert(RSDGridPoint!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDMuStat->reportFP!=NULL);
	
	double windowCenter = RSDGridPoint->positionReduced;
	double windowStart = 0.0;
	double windowEnd = 0.0;
	double muVar = RSDGridPoint->muVarReduced;
	double muSfs = RSDGridPoint->muSfsReduced;
	double muLd = RSDGridPoint->muLdReduced;
	double mu = RSDGridPoint->muReduced;
	
	if(RSDGridPoint->nnPositiveClass0!=NULL && RSDGridPoint->nnPositiveClass1!=NULL)
	{
		double nnPositiveClass0Reduced = RSDGridPoint->nnPositiveClass0Reduced;
		double nnPositiveClass1Reduced = RSDGridPoint->nnPositiveClass1Reduced;
		
		fprintf(RSDMuStat->reportFP, "%.0f\t%.0f\t%.0f\t%.3e\t%.3e\t%.3e\t%.3e\t%.3e\t%.3e\n", windowCenter, windowStart, windowEnd, muVar, muSfs, muLd, mu, 
												       nnPositiveClass0Reduced, nnPositiveClass1Reduced);
	}
	else
		RSDMuStat_output2FileFull (RSDMuStat, windowCenter, windowStart, windowEnd, muVar, muSfs, muLd, mu);
}

void RSDGridPoint_write2FileSimple (RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat)
{
	assert(RSDGridPoint!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDMuStat->reportFP!=NULL);
	
	double windowCenter = RSDGridPoint->positionReduced;
	double windowStart = 0.0;
	double windowEnd = 0.0;
	double muVar = RSDGridPoint->muVarReduced;
	double muSfs = RSDGridPoint->muSfsReduced;
	double muLd = RSDGridPoint->muLdReduced;
	double mu = RSDGridPoint->muReduced;
	
	if(RSDGridPoint->nnPositiveClass0!=NULL && RSDGridPoint->nnPositiveClass1!=NULL)
	{
		double nnPositiveClass0Reduced = RSDGridPoint->nnPositiveClass0Reduced;
		double nnPositiveClass1Reduced = RSDGridPoint->nnPositiveClass1Reduced;
		
		fprintf(RSDMuStat->reportFP, "%.0f\t%.3e\t%.3e\t%.3e\n", windowCenter, mu, nnPositiveClass0Reduced, nnPositiveClass1Reduced);
	}
	else
		RSDMuStat_output2FileSimple (RSDMuStat, windowCenter, windowStart, windowEnd, muVar, muSfs, muLd, mu);
}

void RSDGridPoint_write2FileConfigure (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDCommandLine->fullReport==1)
		RSDGridPoint_write2File = &RSDGridPoint_write2FileFull;
	else
		RSDGridPoint_write2File = &RSDGridPoint_write2FileSimple;
}
void RSDGridPoint_getSteps (RSDCommandLine_t * RSDCommandLine, int * stepsLeft, int * stepsRight)
{
	assert(RSDCommandLine!=NULL);
	assert(RSDCommandLine->imagesPerSimulation>=1);
	assert(stepsLeft!=NULL);
	assert(stepsRight!=NULL);
	
	(*stepsLeft) = RSDCommandLine->imagesPerSimulation / 2 ;
	(*stepsRight) = RSDCommandLine->imagesPerSimulation - (*stepsLeft);
}

int RSDGridPoint_getFirstSNPIndex (int targetSNPIndex, int stepsLeft, int windowStep, int windowSize)
{
	assert(targetSNPIndex>=0);
	assert(stepsLeft>=0);
	assert(windowStep>=1);
	
	int firstSNPIndex = targetSNPIndex - stepsLeft  * windowStep;
	
	if(firstSNPIndex<windowSize/2)
	{
		int stepsLeftMax = (targetSNPIndex-windowSize/2) / windowStep;
		firstSNPIndex = targetSNPIndex - stepsLeftMax  * windowStep;
	}
	
	assert(firstSNPIndex>=windowSize/2);
	
	return firstSNPIndex;
}

int RSDGridPoint_getLastSNPIndex (int targetSNPIndex, int size, int stepsRight, int windowStep, int windowSize)
{
	assert(targetSNPIndex>=0 && size>=0 && targetSNPIndex<size);
	assert(stepsRight>=0);
	assert(windowStep>=1);
	
	int lastSNPIndex = targetSNPIndex + (stepsRight-1) * windowStep;
	
	if(lastSNPIndex>size-windowSize/2)
	{
		int stepsRightMax = (size-windowSize/2+1-targetSNPIndex) / windowStep;
		lastSNPIndex = targetSNPIndex + (stepsRightMax-1)  * windowStep;
	}	

	assert(lastSNPIndex<=size-windowSize/2);
	
	return lastSNPIndex;
}

RSDGridPoint_t * RSDGridPoint_compute (void * RSDImagev, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, 
				       RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, double targetPos, char * destinationPath, int scoreIndex, int setIndex)
{
	assert(RSDMuStat!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDPatternPool!=NULL);
	assert(RSDDataset!=NULL);	
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);	
	assert((int)RSDChunk->chunkSize>=RSDMuStat->windowSize); 
	assert(RSDCommandLine->imageWindowStep>=1);
	
	int i=-1, size = (int)RSDChunk->chunkSize, windowStep = RSDCommandLine->imageWindowStep, stepsLeft = 0, stepsRight = 0;
	
	if(!(RSDChunk->sitePosition[0]<=targetPos && targetPos <= RSDChunk->sitePosition[size-1])) // return if target position is not in the chunk
		return NULL;
	
	int targetSNPIndex = RSDGridPoint_getTargetSNPIndex (RSDChunk, RSDMuStat, RSDCommandLine, targetPos);
		
	if(targetSNPIndex==-1) 
		return NULL;

	RSDGridPoint_getSteps (RSDCommandLine, &stepsLeft, &stepsRight);
	int firstSNPIndex = RSDGridPoint_getFirstSNPIndex (targetSNPIndex, stepsLeft, windowStep, RSDMuStat->windowSize); // reduce steps if too close to chunk borders
	int lastSNPIndex = RSDGridPoint_getLastSNPIndex (targetSNPIndex, size, stepsRight, windowStep, RSDMuStat->windowSize);
	
	assert(firstSNPIndex>=0);
	assert(size>=lastSNPIndex);	
	
	RSDGridPoint_t * RSDGridPoint = RSDGridPoint_new();
			
	int snpf=-1, snpl = -1, winlsnpf = -1, winlsnpl = -1, winrsnpf = -1, winrsnpl = -1;
	float isValid = 0, muVar=0.0f, muSfs=0.0f, muLd=0.0f, mu=0.0f;
	double windowCenter = 0.0, windowStart = 0.0, windowEnd = 0.0;	
	
	for(i=firstSNPIndex;i<=lastSNPIndex;i=i+windowStep)
	{
		/* gridPoint-centered mu statistic */

		snpf = i - RSDMuStat->windowSize/2; // window defined differently than default mu implementation - here i is the window center, not the first snp
		snpl = i + (RSDMuStat->windowSize/2 - 1);    	
		
		assert(snpf>=0);
		assert(snpl<=size-1);
		assert(snpl-snpf+1==RSDMuStat->windowSize);		

		isValid = RSDMuStat_placeWindow (RSDMuStat, RSDChunk, i, &snpf, &snpl, &winlsnpf, &winlsnpl, &winrsnpf, &winrsnpl, &windowCenter, &windowStart, &windowEnd, 1);			
		
		if(RSDCommandLine->gridPointReductionMax==0)
			windowCenter = targetPos;  // using the gridpoint position, comment out to use standard-raisd windowcenter to estimate region extent, 
						   // currently all rsdgridpoint positions are the same, fix reduce function for region estimation

		RSDGridPoint_addNewPosition (RSDGridPoint, RSDCommandLine, windowCenter); 			
		
		muVar=RSDMuStat_calcMuVar (RSDMuStat, RSDDataset, RSDChunk, snpf, snpl);			

		RSDGridPoint->muVar[RSDGridPoint->size-1] = muVar; 		
		
		muSfs = RSDMuStat_calcMuSfsFull (RSDMuStat, RSDDataset, RSDChunk, RSDCommandLine, snpf, snpl);
		RSDGridPoint->muSfs[RSDGridPoint->size-1] = muSfs;
		
		muLd = RSDMuStat_calcMuLd (RSDMuStat, RSDChunk, winlsnpf, winlsnpl, winrsnpf, winrsnpl);		
		RSDGridPoint->muLd[RSDGridPoint->size-1] = muLd;				
		
		mu = RSDMuStat_calcMu (RSDMuStat, RSDCommandLine, muVar, muSfs, muLd, windowCenter, isValid, fpOut);			
		RSDGridPoint->mu[RSDGridPoint->size-1] = mu;	
		
		/* image-generation for CNN inference */
				
		if(RSDCommandLine->opCode == OP_USE_CNN || RSDCommandLine->opCode == OP_CREATE_IMAGES) 
		{
			assert(RSDImagev!=NULL);
			
			RSDImage_t * RSDImage = (RSDImage_t *) RSDImagev;
		
			RSDImage_setRange (RSDImage, RSDChunk, (int64_t) snpf, (int64_t)snpl);
			RSDImage_getData (RSDImage, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine);
			RSDImage_setSitePosition (RSDImage, RSDChunk->sitePosition[targetSNPIndex]);		
			//RSDImage_reorderData (RSDImage, RSDCommandLine);
										
			if(RSDCommandLine->enBinFormat==0)
				RSDImage_savePNG (RSDImage, RSDChunk, RSDDataset, RSDCommandLine, i, RSDImage->data, destinationPath, muVar, scoreIndex, setIndex, RSDGridPoint->size, fpOut);
			else // pytorch only
				RSDImage_saveBIN (RSDImage, RSDChunk, RSDDataset, RSDPatternPool, RSDCommandLine, i, RSDImage->data, destinationPath, scoreIndex, setIndex, RSDGridPoint->size, windowCenter, fpOut);
		}
	}
	
	return RSDGridPoint;
}

void RSDGridPoint_calcCompositeScore (RSDGridPoint_t * RSDGridPoint, int gridPointDataIndex)
{
	assert(RSDGridPoint!=NULL);
	
	// muVar ^ positiveClass
	
    	float muVar = RSDGridPoint->muVar[gridPointDataIndex];
    	RSDGridPoint->nnPositiveClass1[gridPointDataIndex] = powf(muVar, RSDGridPoint->nnPositiveClass0[gridPointDataIndex]);
}
#endif
