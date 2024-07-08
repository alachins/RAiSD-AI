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

uint32_t sampleBitCount (RSDImage_t * RSDImage, int8_t * data, int sampleIndex)
{	
	assert(RSDImage!=NULL);
	assert(sampleIndex>=0);
	assert(sampleIndex<RSDImage->height);
	
	int i;
	uint32_t cnt = 0ull;
	for(i=0;i<RSDImage->width;i++)
		cnt+=data[sampleIndex*RSDImage->width+i];
		
	return cnt;
}

uint64_t snpBitCount (RSDImage_t * RSDImage, int8_t * data, int snpIndex)
{	
	assert(RSDImage!=NULL);
	assert(snpIndex>=0);
	assert(snpIndex<RSDImage->width);
	
	int i;
	uint64_t cnt = 0ull;
	for(i=0;i<RSDImage->height;i++)
		cnt+=data[i*RSDImage->width+snpIndex];
		
	return cnt;
}

RSDImage_t * RSDImage_new (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if((RSDCommandLine->opCode!=OP_CREATE_IMAGES)&&(RSDCommandLine->opCode!=OP_USE_CNN))
		return NULL;
		
	RSDImage_t * RSDImage = NULL;
	
	RSDImage = (RSDImage_t *)malloc(sizeof(RSDImage_t));
	assert(RSDImage!=NULL);
	
	RSDImage->width=-1; 
	RSDImage->height=-1;
	RSDImage->snpLengthInBytes=-1; 	
	RSDImage->firstSNPIndex=-1ll;
	RSDImage->lastSNPIndex=-1ll;	
	RSDImage->firstSNPPosition=0ull; 
	RSDImage->lastSNPPosition=0ull;
	strncpy(RSDImage->destinationPath, "\0", STRING_SIZE);
	RSDImage->remainingSetImages=0ull;
	RSDImage->generatedSetImages=0ull;
	RSDImage->totalGeneratedImages=0ull;
	RSDImage->data=NULL;
	RSDImage->compressedData=NULL;
	RSDImage->dataT=NULL;
	RSDImage->incomingSNP=NULL;
	RSDImage->rowSortScore=NULL;
	RSDImage->rowSorter=RSDSort_new(RSDCommandLine);
	RSDImage->colSortScore=NULL;
	RSDImage->colSorter=RSDSort_new(RSDCommandLine);
	RSDImage->nextSNPDistance=NULL;
	//RSDImage->byteBuffer = NULL;
	RSDImage->derivedAlleleFrequency = NULL;
	RSDImage->sitePosition = 0.0;
	
	return RSDImage;
}

void RSDImage_setSitePosition (RSDImage_t * RSDImage, double sitePosition)
{
	assert(RSDImage!=NULL);
	RSDImage->sitePosition = sitePosition;
}

void RSDImage_makeDirectory (RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDImage==NULL)
		return;
		
	if(RSDCommandLine->opCode!=OP_CREATE_IMAGES)
		return;
		
	assert(RSDImage!=NULL);
	
	char tstring [STRING_SIZE];
	int ret = 0;
	
	if(RSDCommandLine->forceRemove)
	{
		strcpy(tstring, "rm -r ");
		strcat(tstring, "RAiSD_Images."); 
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, " 2>/dev/null");
		
		ret = system(tstring);
		assert(ret!=-1);
	}
		
	strcpy(tstring, "mkdir ");
	strcat(tstring, "RAiSD_Images.");
	strcat(tstring, RSDCommandLine->runName);
	strcat(tstring, " 2>/dev/null");
	
	ret = system(tstring);
	assert(ret!=-1);
	
	strcpy(tstring, "mkdir ");
	strcat(tstring, "RAiSD_Images.");
	strcat(tstring, RSDCommandLine->runName);
	strcat(tstring, "/");
	strcat(tstring, RSDCommandLine->imageClassLabel);
	strcat(tstring, " 2>/dev/null");
	
	ret = system(tstring);
	assert(ret!=-1);
	
	strncpy(RSDImage->destinationPath, "\0", STRING_SIZE);
	strcat(RSDImage->destinationPath, "RAiSD_Images.");
	strcat(RSDImage->destinationPath, RSDCommandLine->runName);
	strcat(RSDImage->destinationPath, "/");
	strcat(RSDImage->destinationPath, RSDCommandLine->imageClassLabel);
	strcat(RSDImage->destinationPath, "/");	
}

void RSDImage_checkDimensions (RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDImage!=NULL);
	assert(RSDCommandLine!=NULL);

	char tstring[STRING_SIZE], format[STRING_SIZE];	

	if(RSDCommandLine->opCode==OP_USE_CNN)
	{
		strncpy(tstring, "RAiSD_Grid.", STRING_SIZE); 
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, "/info.txt");  
	}
	else
	{
		strncpy(tstring, "RAiSD_Images.", STRING_SIZE); 
		strcat(tstring, RSDCommandLine->runName);
		strcat(tstring, "/info.txt");
	}	

	FILE * fp = fopen(tstring, "r");
	
	if(fp==NULL)
	{
		fp = fopen(tstring, "w");

		fprintf(fp, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n");
		fprintf(fp, "%d\n", RSDImage->width);
		fprintf(fp, "%d\n", RSDImage->height);
		fprintf(fp, "%s\n", RSDCommandLine->enBinFormat==1?"bin":"2D");
		fprintf(fp, "%d\n", RSDCommandLine->imgDataType);
		fprintf(fp, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***");   
	}
	else
	{
		int height=-1, width=-1, type=-1;
		
		int rcnt = fscanf(fp, "%s %d %d %s %d", tstring, &width, &height, format, &type);
		assert(rcnt==5);
		
		if((height!=RSDImage->height)||(width!=RSDImage->width))
		{
		
			if(RSDCommandLine->opCode==OP_USE_CNN)
				fprintf(stderr, "\nERROR: Image dimension mismatch between input sets in directory RAiSD_Grid.%s\n       (width x height in file RAiSD_Grid.%s/info.txt: %d x %d, current: %d x %d)\n\n",RSDCommandLine->runName, RSDCommandLine->runName, width, height, RSDImage->width, RSDImage->height);
			else
				fprintf(stderr, "\nERROR: Image dimension mismatch between class folders in directory RAiSD_Images.%s\n       (width x height in file RAiSD_Images.%s/info.txt: %d x %d, current: %d x %d)\n\n",RSDCommandLine->runName, RSDCommandLine->runName, width, height, RSDImage->width, RSDImage->height);
				
			exit(0);			
		}
		
		if((RSDCommandLine->enBinFormat==0 && (!strcmp(format, "bin")))||(RSDCommandLine->enBinFormat==1 && (!strcmp(format, "2D"))))
		{
			fprintf(stderr, "\nERROR: Data format mismatch between class folders in directory RAiSD_Images.%s\n       (data format in file RAiSD_Images.%s/info.txt: %s, current: %s)\n\n",RSDCommandLine->runName, RSDCommandLine->runName, format, RSDCommandLine->enBinFormat==1?"bin":"2D");
			
			exit(0);
		}
		
		if(RSDCommandLine->imgDataType!= type)
		{
			fprintf(stderr, "\nERROR: Data-type code mismatch between class folders in directory RAiSD_Images.%s\n       (data-type code in file RAiSD_Images.%s/info.txt: %d, current: %d)\n\n", RSDCommandLine->runName, RSDCommandLine->runName, type, RSDCommandLine->imgDataType);
			
			exit(0);
		}	
	}
	
	fclose(fp);
	fp=NULL;
}

void RSDImage_print (RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDImage==NULL)
		return;
		
	if(RSDCommandLine->opCode!=OP_CREATE_IMAGES)
		return;
		
	assert(RSDImage!=NULL);
	assert(fpOut);
	
	fprintf(fpOut, " Target position     :\t%lu\n", RSDCommandLine->imageTargetSite);
	fprintf(fpOut, " Image step          :\t%d\n", RSDCommandLine->imageWindowStep);
	
	
	fprintf(fpOut, " File format\t     :\t%s\n", RSDCommandLine->enBinFormat==1?"binary":"PNG");
	
	char imgFormat [STRING_SIZE];
	
	if(RSDCommandLine->enBinFormat==1)
		strcpy(imgFormat, "bin");
	else
		strcpy(imgFormat, "PNG");
	
	fprintf(fpOut, " Data type\t     :\t%s\n", getDataType_string (imgFormat, RSDCommandLine->imgDataType));	
	
	//if(RSDCommandLine->imageReorderOpt)
	//	fprintf(fpOut, " Pixel rearrangement :\tON\n");
	//else
	//	fprintf(fpOut, " Pixel rearrangement :\tOFF\n");
}

void RSDImage_initGeneratedSetImages (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	
	if(RSDChunk->chunkID==0)
		RSDImage->generatedSetImages = 0ull;
}

void RSDImage_init (RSDImage_t * RSDImage, RSDDataset_t * RSDDataset, RSDMuStat_t * RSDMuStat, RSDPatternPool_t * RSDPatternPool, RSDCommandLine_t * RSDCommandLine, RSDChunk_t * RSDChunk, int setIndex, FILE * fpOut)
{  
	assert(RSDImage!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDMuStat!=NULL);
	assert(RSDPatternPool!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(RSDChunk!=NULL);
	
	RSDImage_setRemainingSetImages (RSDImage, RSDChunk, RSDCommandLine); // only if chunkID==0
	RSDImage_initGeneratedSetImages (RSDImage, RSDChunk); // only if chunkID==0
		
	if(!(RSDChunk->chunkID==0 && setIndex==0))
		return;
		
	fprintf(stdout, " Generating images ...\n");

	if(RSDCommandLine->displayProgress==1)
		fprintf(stdout, "\n");
		
	fprintf(fpOut, " Generating images ...\n\n");
	
	fflush(stdout);
		
	RSDImage->width = RSDCommandLine->fullFrame==1?RSDChunk->chunkSize:RSDMuStat->windowSize;
		
	RSDImage->height = RSDDataset->setSamples;
	RSDImage->snpLengthInBytes = (RSDImage->height + (8 - 1)) / 8; 
	
	RSDImage_checkDimensions (RSDImage, RSDCommandLine);
	
	RSDImage->firstSNPIndex = -1;
	RSDImage->lastSNPIndex = -1;
	RSDImage->firstSNPPosition = 0ull;
	RSDImage->lastSNPPosition = 0ull;
	
	assert(RSDImage->width>=1);
	assert(RSDImage->height>=1);
	
	RSDImage->data = (int8_t*)rsd_malloc(sizeof(int8_t)*RSDImage->height*RSDImage->width); 
	assert(RSDImage->data!=NULL);
	
	RSDImage->compressedData = (uint64_t **)rsd_malloc(sizeof(uint64_t*)*RSDImage->width);
	assert(RSDImage->compressedData!=NULL);
	
	RSDImage->dataT = (int8_t*)rsd_malloc(sizeof(int8_t)*RSDImage->height*RSDImage->width); 
	assert(RSDImage->dataT!=NULL);
			
	RSDImage->incomingSNP = (int8_t*)rsd_malloc(sizeof(int8_t)*RSDImage->height);
	assert(RSDImage->incomingSNP);
	
	RSDImage->rowSortScore = NULL;
	RSDImage->colSortScore = NULL;
	
	if(RSDCommandLine->imageReorderOpt==PIXEL_REORDERING_ENABLED)
	{
		assert(0); // not implemented yet
		
		assert(RSDImage->height!=-1);
		assert(RSDImage->width!=-1);
		
		RSDImage->rowSortScore = (uint32_t*)rsd_malloc(sizeof(uint32_t)*RSDImage->height);
		assert(RSDImage->rowSortScore!=NULL);
		
		RSDSort_init (RSDImage->rowSorter, RSDImage->height);
		
		RSDImage->colSortScore = (uint32_t*)rsd_malloc(sizeof(uint32_t)*RSDImage->width);
		assert(RSDImage->colSortScore!=NULL);
		
		RSDSort_init (RSDImage->colSorter, RSDImage->width);
	}
	
	RSDImage->nextSNPDistance = (double*)rsd_malloc(sizeof(double)*RSDImage->width);
	assert(RSDImage->nextSNPDistance);
	
	RSDImage->nextSNPDistance[RSDImage->width-1]=0.0;
	
	if(RSDCommandLine->imgDataType==BIN_DATA_ALLELE_COUNT)
	{
		RSDImage->derivedAlleleFrequency = (float*)rsd_malloc(sizeof(float)*RSDImage->width);
		assert(RSDImage->derivedAlleleFrequency!=NULL);
	}
	
	if(RSDCommandLine->enBinFormat==0)
	{
		RSDImage->bitmap.width = RSDImage->width;
		RSDImage->bitmap.height = RSDImage->height;
		
		RSDImage->bitmap.pixels = calloc (RSDImage->bitmap.width * RSDImage->bitmap.height, sizeof (pixel_t));
		assert(RSDImage->bitmap.pixels!=NULL);	
	}
}

void RSDImage_generateFullFrame (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, char * destinationPath, int scoreIndex, int setIndex)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDPatternPool!=NULL);
	assert(RSDDataset!=NULL);	
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);	
	
	if(RSDCommandLine->fullFrame!=1)
		return;	
	
	RSDImage_setRange (RSDImage, RSDChunk, (int64_t) 0, (int64_t)RSDChunk->chunkSize-1);
	RSDImage_getData (RSDImage, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine);
	double windowCenter = (RSDChunk->sitePosition[(int64_t)RSDChunk->chunkSize-1]+RSDChunk->sitePosition[(int64_t)RSDChunk->chunkSize-1])*0.5;
	RSDImage_setSitePosition (RSDImage, windowCenter);		
	//RSDImage_reorderData (RSDImage, RSDCommandLine);
										
	if(RSDCommandLine->enBinFormat==0)
		RSDImage_savePNG (RSDImage, RSDChunk, RSDDataset, RSDCommandLine, 0, RSDImage->data, destinationPath, 1.0, scoreIndex, setIndex, 1, fpOut);
	else // pytorch only
		RSDImage_saveBIN (RSDImage, RSDChunk, RSDDataset, RSDPatternPool, RSDCommandLine, 0, RSDImage->data, destinationPath, scoreIndex, setIndex, 1, windowCenter, fpOut);			

}

void RSDImage_free (RSDImage_t * RSDImage)
{
	if(RSDImage==NULL)
		return;		

	if(RSDImage->incomingSNP!=NULL)
	{
		free(RSDImage->incomingSNP);
		RSDImage->incomingSNP = NULL;
	}	
	
	if(RSDImage->data!=NULL)
	{
		free(RSDImage->data);
		RSDImage->data=NULL;
	}
	
	if(RSDImage->dataT!=NULL)
	{
		free(RSDImage->dataT);
		RSDImage->dataT=NULL;
	}
	
	if(RSDImage->rowSortScore!=NULL)
	{
		free(RSDImage->rowSortScore);
		RSDImage->rowSortScore=NULL;
	}
	
	if(RSDImage->colSortScore!=NULL)
	{
		free(RSDImage->colSortScore);
		RSDImage->colSortScore=NULL;
	}
	
	RSDSort_free (RSDImage->rowSorter);
	RSDSort_free (RSDImage->colSorter);
	
	if(RSDImage->nextSNPDistance!=NULL)
	{
		free(RSDImage->nextSNPDistance);
		RSDImage->nextSNPDistance=NULL;
	}
	
	//if(RSDImage->byteBuffer!=NULL)
	//{
	//	free(RSDImage->byteBuffer);
	//	RSDImage->byteBuffer=NULL;
	//}	
		
	if(RSDImage->derivedAlleleFrequency!=NULL)
	{
		free(RSDImage->derivedAlleleFrequency);
		RSDImage->derivedAlleleFrequency=NULL;
	}
	
	if(RSDImage->compressedData!=NULL)
	{
		free(RSDImage->compressedData);
		RSDImage->compressedData=NULL;
	}
	
	if(RSDImage->bitmap.pixels!=NULL)
	{
		free(RSDImage->bitmap.pixels);
		RSDImage->bitmap.pixels=NULL;
	}	
	
	free(RSDImage);
	RSDImage = NULL;
}

void RSDImage_setRemainingSetImages (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDCommandLine!=NULL);
	
	if(RSDChunk->chunkID==0)
		RSDImage->remainingSetImages = RSDCommandLine->imagesPerSimulation;
}

void RSDImage_resetRemainingSetImages (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDCommandLine!=NULL);
	
	RSDImage->remainingSetImages = RSDCommandLine->imagesPerSimulation;
}

void RSDImage_setRange (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, int64_t firstSNPIndex, int64_t lastSNPIndex)
{
	assert(RSDImage!=NULL);
	
	RSDImage->firstSNPIndex = firstSNPIndex;
	RSDImage->lastSNPIndex = lastSNPIndex;
	RSDImage->firstSNPPosition = (uint64_t)RSDChunk->sitePosition[RSDImage->firstSNPIndex]; 
	RSDImage->lastSNPPosition = (uint64_t)RSDChunk->sitePosition[RSDImage->lastSNPIndex];
	
	//printf("firstsnpindex %li lastsnpindex %li firstpos %lu lastpost %lu chunkid %lu\n", RSDImage->firstSNPIndex,  RSDImage->lastSNPIndex, RSDImage->firstSNPPosition, RSDImage->lastSNPPosition, RSDChunk->chunkID);
		
}

void decompressPattern (uint64_t * pattern, int patternSz, int samples, int8_t * SNP)
{
	assert(pattern!=NULL);
	assert(SNP!=NULL);
	
	int i=-1, j=-1, bit=-1;
	
	uint64_t d = 0;	
	
	for(i=0;i<patternSz-1;i++)
	{
		d = pattern[i];

		for(j=0;j<64;j++)
		{
			bit = (d & 1);
			d=d>>1;
			SNP[(i+1)*64-j-1] = (int8_t)bit;
		}	
	}
	
	d = pattern[i];

	for(j=0;j<samples-(patternSz-1)*64;j++)
	{
		bit = (d & 1);
		d=d>>1;		
		SNP[samples-j-1] = (int8_t)bit;
	}
}

void RSDImage_getData (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDPatternPool!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(RSDImage->firstSNPIndex!=-1);
	assert(RSDImage->lastSNPIndex!=-1);
	
	int i=0, j=0, k=0;	
	
	assert(RSDImage->lastSNPIndex-RSDImage->firstSNPIndex+1==RSDImage->width);
	
	// Raw SNP data
	if(RSDCommandLine->enBinFormat==0) // PNG
	{
		for(i=RSDImage->firstSNPIndex;i<=RSDImage->lastSNPIndex;i++)
		{
			decompressPattern (&(RSDPatternPool->poolData[RSDChunk->patternID[i]*RSDPatternPool->patternSize]), RSDPatternPool->patternSize, RSDDataset->setSamples, RSDImage->incomingSNP);
						
			for(j=0;j<RSDImage->height;j++)
				RSDImage->data[j*RSDImage->width+i-RSDImage->firstSNPIndex] = RSDImage->incomingSNP[j];			
		}
	}
	else // BIN
	{
		for(i=RSDImage->firstSNPIndex;i<=RSDImage->lastSNPIndex;i++)
			RSDImage->compressedData[k++] = &(RSDPatternPool->poolData[RSDChunk->patternID[i]*RSDPatternPool->patternSize]);	
	}

	// Pairwise SNP distances	
	int windowSize = RSDImage->lastSNPIndex - RSDImage->firstSNPIndex + 1;
	for(j=0;j<windowSize-1;j++)
	{
		double d = RSDChunk->sitePosition[RSDImage->firstSNPIndex+j+1]-RSDChunk->sitePosition[RSDImage->firstSNPIndex+j];
		assert(d>=0.0);
		RSDImage->nextSNPDistance[j] = d; 
	}			
}

void RSDImage_getFilename (RSDCommandLine_t * RSDCommandLine, RSDChunk_t * RSDChunk, RSDDataset_t * RSDDataset, char * destinationPath, int scoreIndex, int imgIndex, int setIndex, int gridPointSize, char * filename)
{
	assert(RSDChunk!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(imgIndex>=0 && scoreIndex>=0 && gridPointSize>=1 && setIndex>=0);
	assert(filename!=NULL);
	
	char tstring [STRING_SIZE];

	// filenames in OP_USE_CNN mode are parsed through getIndicesFromImageName()
	// filenames in other modes are not parsed at all 
	
	strncpy(filename, destinationPath, STRING_SIZE-1);
	
	//strcat(filename, RSDDataset->setID);
	sprintf(tstring, "%d", (int)setIndex);
	strcat(filename, tstring);
	
	strcat(filename, "_");
	sprintf(tstring, "%d", (int)scoreIndex);
	strcat(filename, tstring);

	strcat(filename, "_");	
	sprintf(tstring, "%d", gridPointSize-1); // this is the gridpointdata index
	strcat(filename, tstring);
	
	if(RSDCommandLine->enBinFormat==0)
		strcat(filename, ".png");
	else
		strcat(filename, ".snp");
		
}

int RSDImage_savePNG (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, int imgIndex, int8_t * data, char * destinationPath, float muVar, int scoreIndex, int setIndex, int gridPointSize, FILE * fpOut)
{
	assert(RSDImage!=NULL);
	assert(RSDChunk!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(imgIndex>=0 && scoreIndex>=0 && gridPointSize>=1 && setIndex>=0);
	assert(data!=NULL);
	assert(destinationPath!=NULL);
	assert(fpOut);
	
	char imgPath[STRING_SIZE];
	uint64_t x=0, y=0;
	double r_val=0.0;	
	
	RSDImage_getFilename (RSDCommandLine, RSDChunk, RSDDataset, destinationPath, scoreIndex, imgIndex, setIndex, gridPointSize, imgPath);

	for (y = 0; y < RSDImage->bitmap.height; y++) 
	{
		for (x = 0; x < RSDImage->bitmap.width; x++) 
		{
			pixel_t * pixel = getPixel(&(RSDImage->bitmap), x, y);
			
			switch(RSDCommandLine->imgDataType)
			{
				case IMG_DATA_RAW:
					pixel->red = data[y*RSDImage->width+x]*255; 
					pixel->green = data[y*RSDImage->width+x]*255; 
					pixel->blue = data[y*RSDImage->width+x]*255;
					
					break;
					
				case IMG_DATA_PAIRWISE_DISTANCE:
					r_val = round(255*(RSDImage->nextSNPDistance[x]/200.0));
					
					if (r_val > 255.0) 
						pixel->red = 255;
					else
						pixel->red = r_val;
					
					if (r_val > 255.0) 
						pixel->green = 255;
					else
						pixel->green = r_val;
					
					pixel->blue = (data[y*RSDImage->width+x])*255;
									
					break;
					
				case IMG_DATA_MUVAR_SCALED:
					pixel->red = (data[y*RSDImage->width+x])*255; 
				
					if(muVar<=1.475) // two standard deviations
						pixel->green = (data[y*RSDImage->width+x])*255;
					else
						pixel->green = (data[y*RSDImage->width+x])*255/muVar;
			
					if(muVar<=1.475)
						pixel->blue = (data[y*RSDImage->width+x])*255;
					else
						pixel->blue = (data[y*RSDImage->width+x])*255/muVar;
										
					break;
					
				case IMG_DATA_EXPERIMENTAL:
				
					assert(0);
					
					break;
					
				default:
					pixel->red = data[y*RSDImage->width+x]*255; 
					pixel->green = data[y*RSDImage->width+x]*255; 
					pixel->blue = data[y*RSDImage->width+x]*255;
					
					fprintf(fpOut, "\nERROR: Invalid data-type code (-typ %d) in image format (PNG)\n\n",RSDCommandLine->imgDataType);
					fprintf(stderr, "\nERROR: Invalid data-type code (-typ %d) in image format (PNG)\n\n",RSDCommandLine->imgDataType);
					exit(0);
					
				break;			
			}			
		}
	}
	
	RSDImage->generatedSetImages++;
	RSDImage->totalGeneratedImages++;
	
	if (save_png_to_file (&(RSDImage->bitmap), imgPath)) 
	{
		fprintf(fpOut, "\nERROR: Creating file %s failed!\n\n", imgPath);
		fprintf(stderr, "\nERROR: Creating file %s failed!\n\n", imgPath);
		exit(0);					
	}
	
	return 1;	
}

int RSDImage_saveBIN (RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDCommandLine_t * RSDCommandLine, int imgIndex, int8_t * data, char * destinationPath, int scoreIndex, int setIndex, int gridPointSize, double targetPos, FILE * fpOut)
{
	assert(RSDImage!=NULL);
	assert(RSDDataset!=NULL);
	assert(RSDPatternPool!=NULL);
	assert(imgIndex>=0 && scoreIndex>=0 && gridPointSize>=1 && setIndex>=0);
	assert(data!=NULL);
	assert(destinationPath!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(fpOut);
	
	char snpPath[STRING_SIZE];
	uint64_t x=0;	
	
	RSDImage_getFilename (RSDCommandLine, RSDChunk, RSDDataset, destinationPath, scoreIndex, imgIndex, setIndex, gridPointSize, snpPath);
	
	FILE * fp1 = NULL;
	fp1 = fopen(snpPath, "wb");	
	
	if(fp1==NULL)
	{
		fprintf(fpOut, "\nERROR: Creating file %s failed!\n\n", snpPath);
		fprintf(stderr, "\nERROR: Creating file %s failed!\n\n", snpPath);
		exit(0);
	}
	
	assert(fp1!=NULL);			
	
	switch (RSDCommandLine->imgDataType)
	{
		case BIN_DATA_RAW:

			fwrite(&(RSDImage->height), 1, 4, fp1);
			fwrite(&(RSDImage->width), 1, 4, fp1);
			fwrite(&(targetPos), 1, 8, fp1);
			
			for (x = 0; x < (uint64_t)RSDImage->width; x++) 
				fwrite(RSDImage->compressedData[x], sizeof(uint8_t), RSDImage->snpLengthInBytes, fp1);					
			
			fwrite(RSDImage->nextSNPDistance, sizeof(RSDImage->nextSNPDistance[0]), RSDImage->width, fp1);
		break;
		
		case BIN_DATA_ALLELE_COUNT:			
			for(x=0;x<(uint64_t)RSDImage->width;x++)
			{				
				RSDImage->derivedAlleleFrequency[x] = ((float)RSDChunk->derivedAlleleCount[RSDImage->firstSNPIndex+x]) / ((float)RSDImage->height);
				assert(RSDImage->derivedAlleleFrequency[x]>=0.0 && RSDImage->derivedAlleleFrequency[x]<=1.001);		
			}
			
			fwrite(&(RSDImage->width), 1, 4, fp1);
			fwrite(&(targetPos), 1, 8, fp1);
			fwrite(RSDImage->derivedAlleleFrequency, sizeof(RSDImage->derivedAlleleFrequency[0]), RSDImage->width, fp1);
			fwrite(RSDImage->nextSNPDistance, sizeof(RSDImage->nextSNPDistance[0]), RSDImage->width, fp1);
		break;
		
		default:
			fprintf(fpOut, "\nERROR: Invalid data-type code (-typ %d) in binary format (-bin)!\n\n",RSDCommandLine->imgDataType);
			fprintf(stderr, "\nERROR: Invalid data-type code (-typ %d) in binary format (-bin)!\n\n",RSDCommandLine->imgDataType);
			exit(0);
		break;
	}
	
	fclose(fp1);
	
	RSDImage->generatedSetImages++;
	RSDImage->totalGeneratedImages++;
		
	return 1;
}

void RSDImage_rankRows (RSDImage_t * RSDImage)
{
	assert(RSDImage!=NULL);
	
	int i=-1;
	
	for(i=0;i<RSDImage->height;i++)
		RSDImage->rowSortScore[i] = sampleBitCount (RSDImage, RSDImage->data, i);	
		
}

void RSDImage_rankColumns (RSDImage_t * RSDImage)
{
	assert(RSDImage!=NULL);
	
	int i=-1;
	
	for(i=0;i<RSDImage->width;i++)
		RSDImage->colSortScore[i] = snpBitCount (RSDImage, RSDImage->data, i);	
		
}

void RSDImage_rearrangeRowData (RSDImage_t * RSDImage, RSDSort_t * RSDSort)
{
	assert(RSDImage!=NULL);
	assert(RSDSort!=NULL);
	
	int i=-1;
	
	for(i=0;i<RSDImage->height;i++)
		memcpy(&(RSDImage->dataT[i*RSDImage->width]), &(RSDImage->data[RSDSort->indexList[i]*RSDImage->width]), RSDImage->width); 
	
	memcpy(RSDImage->data, RSDImage->dataT, RSDImage->height*RSDImage->width);
}

void RSDImage_rearrangeColumnData (RSDImage_t * RSDImage, RSDSort_t * RSDSort)
{
	assert(RSDImage!=NULL);
	assert(RSDSort!=NULL);
	
	int i=-1, j=-1;
	
	for(i=0;i<RSDImage->width;i++)
		for(j=0;j<RSDImage->height;j++)
			RSDImage->dataT[j*RSDImage->width+i] = RSDImage->data[j*RSDImage->width+RSDSort->indexList[i]]; 
	
	memcpy(RSDImage->data, RSDImage->dataT, RSDImage->height*RSDImage->width);
}


void RSDImage_rearrangeRows (RSDImage_t * RSDImage)
{
	assert(RSDImage!=NULL);
	
	RSDImage_rankRows (RSDImage);
	
	RSDSort_appendScores (RSDImage->rowSorter, (void*)RSDImage, SORT_ROWS);
	
	RSDImage_rearrangeRowData (RSDImage, RSDImage->rowSorter);
}

void RSDImage_rearrangeColumns (RSDImage_t * RSDImage) 
{
	assert(RSDImage!=NULL);
	
	RSDImage_rankColumns (RSDImage);
	
	RSDSort_appendScores (RSDImage->colSorter, (void*)RSDImage, SORT_COLUMNS);
	
	RSDImage_rearrangeColumnData (RSDImage, RSDImage->colSorter);
}

void RSDImage_reorderData (RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDImage!=NULL);
	assert(RSDCommandLine!=NULL);
	
	if(RSDCommandLine->imageReorderOpt==PIXEL_REORDERING_DISABLED)
		return;
		
	RSDImage_rearrangeRows (RSDImage); 
	RSDImage_rearrangeColumns (RSDImage); 
}

void RSDImage_writeOutput (RSDImage_t * RSDImage,  RSDCommandLine_t * RSDCommandLine, RSDDataset_t * RSDDataset, int setIndex, FILE * fpOut)
{
	/* This function prints the number of images per set to stdout and info file */
	
	assert(RSDImage!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(RSDDataset!=NULL);
	assert(setIndex>=0);
	assert(fpOut);
	
	static int slen[5]={0};
	
	slen[0] = getStringLengthString (slen[0], RSDDataset->setID);
	slen[1] = getStringLengthInt (slen[1], RSDDataset->setSize);
	slen[2] = getStringLengthInt (slen[2], RSDDataset->setSNPs); 
	slen[3] = getStringLengthInt (slen[3], (int)RSDImage->generatedSetImages); 
	slen[4] = getStringLengthUint64 (slen[4], RSDDataset->setRegionLength);

	if(RSDCommandLine->opCode==OP_CREATE_IMAGES)
		fprintf(fpOut, " %d: Set %*s | Sites %*d | SNPs %*d | Region %*lu - Images %*lu | Position %.0f\n", setIndex, slen[0], RSDDataset->setID, 
												    		   slen[1], (int)RSDDataset->setSize, 
												    		   slen[2], (int)RSDDataset->setSNPs, 
												    		   slen[4], RSDDataset->setRegionLength, 
												    		   slen[3], RSDImage->generatedSetImages,
												    		   RSDImage->sitePosition);
	else
		fprintf(fpOut, " %d: Set %*s | Sites %*d | SNPs %*d | Region %*lu - Images %*lu\n",  setIndex, slen[0], RSDDataset->setID, 
												    slen[1], (int)RSDDataset->setSize, 
												    slen[2], (int)RSDDataset->setSNPs, 
												    slen[4], RSDDataset->setRegionLength, 
												    slen[3], RSDImage->generatedSetImages);
												    												
	fflush(fpOut);															    
}
#endif

