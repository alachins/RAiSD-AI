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

RSDSort_t * RSDSort_new (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if((RSDCommandLine->opCode!=OP_CREATE_IMAGES)&&(RSDCommandLine->opCode!=OP_USE_CNN))
		return NULL;
		
	if(RSDCommandLine->imageReorderOpt!=PIXEL_REORDERING_ENABLED)
		return NULL;
		
	RSDSort_t * RSDSort = NULL;
	
	RSDSort = (RSDSort_t *)malloc(sizeof(RSDSort_t));
	assert(RSDSort!=NULL);
	
	RSDSort->maxListSize = -1;
	RSDSort->curListSize = -1;
	RSDSort->scoreList = NULL;
	RSDSort->indexList = NULL;
	
	return RSDSort;
}

void RSDSort_rst (RSDSort_t * RSDSort)
{
	assert(RSDSort!=NULL);
	
	int i=-1;
	
	for(i=0;i<RSDSort->maxListSize;i++)
	{
		RSDSort->scoreList[i] = 0ull;
		RSDSort->indexList[i] = -1ull;
	}
	
	RSDSort->curListSize=0;	
}

void RSDSort_init (RSDSort_t * RSDSort, int size) 
{
	if(RSDSort==NULL)
		return;
		
	assert(RSDSort!=NULL);
	assert(size>=2);
	
	RSDSort->maxListSize = size;

	RSDSort->scoreList = (uint64_t *)malloc(sizeof(uint64_t)*RSDSort->maxListSize);
	assert(RSDSort->scoreList!=NULL);
	
	RSDSort->indexList = (int64_t *)malloc(sizeof(int64_t)*RSDSort->maxListSize);
	assert(RSDSort->indexList!=NULL);
	
	RSDSort_rst (RSDSort);	
}

void RSDSort_free (RSDSort_t * RSDSort)
{
	if(RSDSort==NULL)
		return;
	
	assert(RSDSort!=NULL);
		
	if(RSDSort->scoreList!=NULL)
	{
		free(RSDSort->scoreList);
		RSDSort->scoreList=NULL;
	}
	
	if(RSDSort->indexList!=NULL)
	{
		free(RSDSort->indexList);
		RSDSort->indexList=NULL;
	}
	
	free(RSDSort);
	RSDSort=NULL;
}

void RSDSort_appendScore (RSDSort_t * RSDSort, uint64_t score, int64_t index)
{
	assert(RSDSort!=NULL);
	assert(index>=0);
	
	if(RSDSort->curListSize==0)
	{
		RSDSort->curListSize++;
		RSDSort->scoreList[RSDSort->curListSize-1] = score;
		RSDSort->indexList[RSDSort->curListSize-1] = index;
		
		return;		
	}
	
	int i=-1, j=-1;
	
	for(i=0;i<RSDSort->curListSize;i++)
	{
		if(score>RSDSort->scoreList[i])
			break;
	}
	
	for(j=RSDSort->curListSize-1;j>=i;j--)
	{
		RSDSort->scoreList[j+1] = RSDSort->scoreList[j];
		RSDSort->indexList[j+1] = RSDSort->indexList[j]; 
	}
	
	RSDSort->scoreList[j+1] = score;
	RSDSort->indexList[j+1] = index;
	
	RSDSort->curListSize++;	
}

void RSDSort_appendScores (RSDSort_t * RSDSort, void * RSDImage, int mode)
{
	assert(RSDSort!=NULL);
	assert(RSDImage!=NULL);
	assert(mode==SORT_ROWS || mode==SORT_COLUMNS);
	
	RSDSort_rst (RSDSort);
	
	RSDImage_t * RSDImageL = (RSDImage_t *) RSDImage;
	
	int i=-1;
	
	if(mode==SORT_ROWS)
	{
		assert(RSDImageL->height<=RSDSort->maxListSize);
		
		for(i=0;i<RSDImageL->height;i++)
			RSDSort_appendScore (RSDSort, RSDImageL->rowSortScore[i], i);	
	}
	else //SORT_COLUMNS
	{
		assert(RSDImageL->width<=RSDSort->maxListSize);
		
		for(i=0;i<RSDImageL->width;i++)
			RSDSort_appendScore (RSDSort, RSDImageL->colSortScore[i], i);	
	}
}
#endif
