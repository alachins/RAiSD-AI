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

#include "RAiSD.h"

RSDVcf2ms_t * RSDVcf2ms_new (RSDCommandLine_t * RSDCommandLine)
{
	if(RSDCommandLine->vcf2msExtra != VCF2MS_CONVERT)
		return NULL;

	RSDVcf2ms_t * RSDVcf2ms = (RSDVcf2ms_t*)malloc(sizeof(RSDVcf2ms_t));
	assert(RSDVcf2ms!=NULL);

	char fileNameNew[STRING_SIZE];
	strncpy(fileNameNew, RSDCommandLine->inputFileName, STRING_SIZE);
	strcat(fileNameNew, ".ms");

	RSDVcf2ms->outputFilePtr = fopen(fileNameNew, "w");
	assert(RSDVcf2ms->outputFilePtr!=NULL);

	RSDVcf2ms->memSz = POSITIONLIST_MEMSIZE_AND_INCREMENT;

	RSDVcf2ms->segsites=0;
	RSDVcf2ms->positionList=NULL;

	RSDVcf2ms->samples=-1;
	RSDVcf2ms->data=NULL;

	RSDVcf2ms->status=0;

	return RSDVcf2ms;	
}

void RSDVcf2ms_printHeader (RSDVcf2ms_t * RSDVcf2ms)
{
	assert(RSDVcf2ms->outputFilePtr!=NULL);
	fprintf(RSDVcf2ms->outputFilePtr, "ms %d 1 -s %d\n1 2 3\n", (int)RSDVcf2ms->samples, (int)RSDVcf2ms->segsites);
}

void RSDVcf2ms_printSegsitesAndPositions (RSDVcf2ms_t * RSDVcf2ms)
{
	assert(RSDVcf2ms->outputFilePtr!=NULL);

	fprintf(RSDVcf2ms->outputFilePtr, "\n//\nsegsites: %d\npositions:", (int)RSDVcf2ms->segsites);

	int64_t i;
	for(i=0;i<RSDVcf2ms->segsites;i++)
		fprintf(RSDVcf2ms->outputFilePtr, " %f", RSDVcf2ms->positionList[i]);

	fprintf(RSDVcf2ms->outputFilePtr, "\n");
}

void RSDVcf2ms_printSNPData (RSDVcf2ms_t * RSDVcf2ms)
{
	int64_t i, j;
	for(i=0;i<RSDVcf2ms->samples;i++)
	{
		for(j=0;j<RSDVcf2ms->segsites;j++)
			fprintf(RSDVcf2ms->outputFilePtr, "%c", RSDVcf2ms->data[j][i]);
		
		fprintf(RSDVcf2ms->outputFilePtr, "\n");
	}
	fprintf(RSDVcf2ms->outputFilePtr, "\n");
}

void RSDVcf2ms_reset (RSDVcf2ms_t * RSDVcf2ms)
{
	RSDVcf2ms->segsites=0;
}

void RSDVcf2ms_appendSNP (RSDVcf2ms_t * RSDVcf2ms, RSDCommandLine_t * RSDCommandLine, RSDPatternPool_t * RSDPatternPool, int64_t numberOfSamples)
{
	if(RSDCommandLine->vcf2msExtra != VCF2MS_CONVERT)
		return;

	int64_t i;
	
	if(RSDVcf2ms->samples==-1)
	{
		RSDVcf2ms->samples = numberOfSamples;

		RSDVcf2ms->positionList = (double*)rsd_malloc(sizeof(double)*RSDVcf2ms->memSz);
		assert(RSDVcf2ms->positionList!=NULL);

		RSDVcf2ms->data = (char**)rsd_malloc(sizeof(char*)*RSDVcf2ms->memSz);
		assert(RSDVcf2ms->data!=NULL);

		for(i=RSDVcf2ms->memSz-POSITIONLIST_MEMSIZE_AND_INCREMENT;i<RSDVcf2ms->memSz;i++)
		{
			RSDVcf2ms->data[i] = (char*)rsd_malloc(sizeof(char)*RSDVcf2ms->samples);
			assert(RSDVcf2ms->data[i]!=NULL);
		}			
	}

	RSDVcf2ms->segsites++;

	if(RSDVcf2ms->segsites==RSDVcf2ms->memSz)
	{
		RSDVcf2ms->memSz += POSITIONLIST_MEMSIZE_AND_INCREMENT;

		RSDVcf2ms->positionList = (double*)rsd_realloc(RSDVcf2ms->positionList, sizeof(double)*RSDVcf2ms->memSz);
		assert(RSDVcf2ms->positionList!=NULL);

		RSDVcf2ms->data = (char**)rsd_realloc(RSDVcf2ms->data, sizeof(char*)*RSDVcf2ms->memSz);
		assert(RSDVcf2ms->data!=NULL);

		for(i=RSDVcf2ms->memSz-POSITIONLIST_MEMSIZE_AND_INCREMENT;i<RSDVcf2ms->memSz;i++)
		{
			RSDVcf2ms->data[i] = (char*)rsd_malloc(sizeof(char)*RSDVcf2ms->samples);
			assert(RSDVcf2ms->data[i]!=NULL);
		}		
	}

	RSDVcf2ms->positionList [RSDVcf2ms->segsites-1] = ((double) RSDPatternPool->incomingSitePosition)/(double)RSDCommandLine->regionLength;

	for(i=0;i<RSDVcf2ms->samples;i++)
		RSDVcf2ms->data[RSDVcf2ms->segsites-1][i]=RSDPatternPool->incomingSite[i];


/*
	RSDVcf2ms->segsitePositionList = (float*)rsd_realloc(RSDVcf2ms->segsitePositionList, sizeof(float)*RSDVcf2ms->segsites);
	assert(RSDVcf2ms->segsitePositionList!=NULL);

	RSDVcf2ms->segsitePositionList [RSDVcf2ms->segsites-1] = ((float) RSDPatternPool->incomingSitePosition)/(float)RSDCommandLine->regionLength;

	RSDVcf2ms->data = (char**)rsd_realloc(RSDVcf2ms->data, sizeof(char*)*RSDVcf2ms->segsites);
	assert(RSDVcf2ms->data!=NULL);
	
	RSDVcf2ms->data[RSDVcf2ms->segsites-1] = (char*)rsd_malloc(sizeof(char)*RSDVcf2ms->samples);
	assert(RSDVcf2ms->data[RSDVcf2ms->segsites-1]!=NULL);

	int64_t i;
	for(i=0;i<RSDVcf2ms->samples;i++)
		RSDVcf2ms->data[RSDVcf2ms->segsites-1][i]=RSDPatternPool->incomingSite[i];

*/
}

void RSDVcf2ms_free (RSDVcf2ms_t * RSDVcf2ms, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);

	if(RSDCommandLine->vcf2msExtra != VCF2MS_CONVERT)
		return;

	assert(RSDVcf2ms!=NULL);

	int i;	

	if(RSDVcf2ms->outputFilePtr!=NULL)
	{
		fclose(RSDVcf2ms->outputFilePtr);
		RSDVcf2ms->outputFilePtr=NULL;
	}

	if(RSDVcf2ms->positionList!=NULL)
	{
		free(RSDVcf2ms->positionList);
		RSDVcf2ms->positionList=NULL;
	}

	if(RSDVcf2ms->data!=NULL)
	{
		for(i=0;i<RSDVcf2ms->memSz;i++)
		{
			if(RSDVcf2ms->data[i]!=NULL)
			{
				free(RSDVcf2ms->data[i]);
				RSDVcf2ms->data[i]=NULL;
			}
		}

		free(RSDVcf2ms->data);
		RSDVcf2ms->data=NULL;
	}

	free(RSDVcf2ms);
	RSDVcf2ms=NULL;	
}



/*void RSDVcf2ms_createFile (RSDVcf2ms_t * RSDVcf2ms, RSDCommandLine_t * RSDCommandLine)
{
	if(RSDCommandLine->vcf2msExtra != VCF2MS_CONVERT)
		return;

	RSDVcf2ms_printHeader (RSDVcf2ms);

	RSDVcf2ms_printSegsitesAndPositions (RSDVcf2ms);

	RSDVcf2ms_printSNPData (RSDVcf2ms);	

}*/

