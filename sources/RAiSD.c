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

void RSD_init (void);

int setIndexValid; // this is used for selecting a single set to process
double StartTime;
double FinishTime;
double MemoryFootprint;
FILE * RAiSD_Info_FP;
FILE * RAiSD_SiteReport_FP;
FILE * RAiSD_ReportList_FP;
struct timespec requestStart;
struct timespec requestEnd;

#ifdef _PTIMES
struct timespec requestStartMu;
struct timespec requestEndMu;
double TotalMuTime;
#endif

void RSD_header (FILE * fpOut)
{
	if(fpOut==NULL)
		return;

	printRAiSD (fpOut);

	fprintf(fpOut, "\n");
#ifdef _RSDAI	
	fprintf(fpOut, " RAiSD-AI, Raised Accuracy in Sweep Detection using AI (version %d.%d, released in %s %d)\n", MAJOR_VERSION, MINOR_VERSION, RELEASE_MONTH, RELEASE_YEAR);
#else
	fprintf(fpOut, " RAiSD, Raised Accuracy in Sweep Detection (version %d.%d, released in %s %d)\n", MAJOR_VERSION, MINOR_VERSION, RELEASE_MONTH, RELEASE_YEAR);
#endif
	//fprintf(fpOut, " This is version %d.%d (released in %s %d)\n\n", MAJOR_VERSION, MINOR_VERSION, RELEASE_MONTH, RELEASE_YEAR);

	fprintf(fpOut, " Copyright (C) 2017-2024, and GNU GPL'd, by Nikolaos Alachiotis and Pavlos Pavlidis\n");
	fprintf(fpOut, " Contact: n.alachiotis@utwente.nl and pavlidisp@gmail.com\n");
#ifdef _RSDAI
	fprintf(fpOut, " Code contributions: Sjoerd van den Belt and Hanqing Zhao\n");
#endif

	fprintf(fpOut, "\n \t\t\t\t    * * * * *\n\n");
}

void RSD_init (void)
{
	clock_gettime(CLOCK_REALTIME, &requestStart);
	//StartTime = gettime();

	FinishTime = 0.0;
	MemoryFootprint = 0.0;

	RAiSD_Info_FP = NULL;
	RAiSD_SiteReport_FP = NULL;
	RAiSD_ReportList_FP = NULL;

	setIndexValid = -1;

#ifndef _INTRINSIC_POPCOUNT
	popcount_u64_init();
#endif	

	srand((unsigned int)time(NULL)); // if no seed given

#ifdef _PTIMES
	TotalOoCTime = 0.0;
	TotalMuTime = 0.0;
#endif

}

int main (int argc, char ** argv)
{
	RSD_init();

	RSDCommandLine_t * RSDCommandLine = RSDCommandLine_new();
	RSDCommandLine_init(RSDCommandLine);
	RSDCommandLine_load(RSDCommandLine, argc, argv);
	
	RSD_header(stdout);
	RSD_header(RAiSD_Info_FP);
	RSD_header(RAiSD_SiteReport_FP);

	RSDCommandLine_print(argc, argv, stdout);
	RSDCommandLine_print(argc, argv, RAiSD_Info_FP);
	RSDCommandLine_print(argc, argv, RAiSD_SiteReport_FP);
	RSDCommandLine_printInfo(RSDCommandLine, stdout);
	RSDCommandLine_printInfo(RSDCommandLine, RAiSD_Info_FP);

	RSDEval_t * RSDEval = RSDEval_new (RSDCommandLine);
	RSDEval_init (RSDEval, RSDCommandLine);
	RSDEval_calculateDetectionMetricsConfigure (RSDCommandLine);
			
#ifdef _RSDAI
	RSDNeuralNetwork_t * RSDNeuralNetwork = RSDNeuralNetwork_new (RSDCommandLine);
	RSDNeuralNetwork_init (RSDNeuralNetwork, RSDCommandLine, RAiSD_Info_FP);
	RSDNeuralNetwork_train (RSDNeuralNetwork, RSDCommandLine, RAiSD_Info_FP);
	RSDNeuralNetwork_test (RSDNeuralNetwork, RSDCommandLine, RAiSD_Info_FP);
	
	if(RSDCommandLine->opCode==OP_TRAIN_CNN)
	{
		if(RSDNeuralNetwork_modelExists(RSDNeuralNetwork->modelPath)!=1)
		{
			char trainCommand[STRING_SIZE];
			RSDNeuralNetwork_createTrainCommand (RSDNeuralNetwork, RSDCommandLine, trainCommand, 1);

			fprintf(RAiSD_Info_FP, "\nERROR: Model generation failed. The CNN did not train correctly.\n\nUse this command to see Python errors: %s\n\n", trainCommand);
			fprintf(stderr, "\nERROR: Model generation failed. The CNN did not train correctly.\n\nUse this command to see Python errors: %s\n\n", trainCommand);
			exit(0);
		}		
	
		fprintf(stdout, "\n");
		fprintf(stdout, " Output directory    :\t%s\n", RSDNeuralNetwork->modelPath);
				
		fprintf(RAiSD_Info_FP, "\n");
		fprintf(RAiSD_Info_FP, " Output directory: %s\n", RSDNeuralNetwork->modelPath);
	}		
	
	if(RSDCommandLine->opCode==OP_TRAIN_CNN || RSDCommandLine->opCode==OP_TEST_CNN)
	{
		RSD_printTime(stdout, RAiSD_Info_FP);
		RSD_printMemory(stdout, RAiSD_Info_FP);
		fclose(RAiSD_Info_FP);
		
		RSDCommandLine_free(RSDCommandLine);
		RSDNeuralNetwork_free(RSDNeuralNetwork);
		
		return 0;
	}	
#endif	

	RSDPlot_generateRscript(RSDCommandLine, RSDPLOT_BASIC_MU);

	RSDCommonOutliers_t * RSDCommonOutliers = RSDCommonOutliers_new ();
	RSDCommonOutliers_init (RSDCommonOutliers, RSDCommandLine);
	RSDCommonOutliers_process (RSDCommonOutliers, RSDCommandLine);

	if(strcmp(RSDCommonOutliers->reportFilenameRAiSD, "\0"))
	{
		RSDCommonOutliers_free (RSDCommonOutliers);
		RSDCommandLine_free (RSDCommandLine);

		RSD_printTime(stdout, RAiSD_Info_FP);
		RSD_printMemory(stdout, RAiSD_Info_FP);

		fclose(RAiSD_Info_FP);
		
		return 0;
	}	

	RSD_printSiteReportLegend(RAiSD_SiteReport_FP, RSDCommandLine->imputePerSNP, RSDCommandLine->createPatternPoolMask);

	RSDDataset_t * RSDDataset = RSDDataset_new();
	RSDDataset_init(RSDDataset, RSDCommandLine, RAiSD_Info_FP); 
	RSDDataset_print(RSDDataset, RSDCommandLine, stdout);
	RSDDataset_print(RSDDataset, RSDCommandLine, RAiSD_Info_FP);
	
	RSDCommandLine_printExponents (RSDCommandLine, stdout);
	RSDCommandLine_printExponents (RSDCommandLine, RAiSD_Info_FP);

	RSDPlot_printRscriptVersion (RSDCommandLine, stdout);
	RSDPlot_printRscriptVersion (RSDCommandLine, RAiSD_Info_FP);
	
#ifdef _RSDAI
	RSDImage_t * RSDImage = RSDImage_new (RSDCommandLine);	
	RSDImage_makeDirectory (RSDImage, RSDCommandLine);
	
	RSDImage_print (RSDImage, RSDCommandLine, stdout);
	RSDImage_print (RSDImage, RSDCommandLine, RAiSD_Info_FP); 
		
	RSDGrid_t * RSDGrid = RSDGrid_new (RSDCommandLine);
	RSDGrid_makeDirectory (RSDGrid, RSDCommandLine, RSDImage); 
	
	RSDResults_t * RSDResults = RSDResults_new (RSDCommandLine);
	RSDResults_setGridSize (RSDResults, RSDCommandLine);
	
	RSDGridPoint_write2FileConfigure (RSDCommandLine);
#endif	

	RSDCommandLine_printWarnings (RSDCommandLine, argc, argv, (void*)RSDDataset, stdout);
	RSDCommandLine_printWarnings (RSDCommandLine, argc, argv, (void*)RSDDataset, RAiSD_Info_FP);
	
	RSDPatternPool_t * RSDPatternPool = RSDPatternPool_new(RSDCommandLine); // RSDCommandLine here only for vcf2ms conversion
	RSDPatternPool_init(RSDPatternPool, RSDCommandLine, RSDDataset->numberOfSamples);
	RSDPatternPool_print(RSDPatternPool, stdout);
	RSDPatternPool_print(RSDPatternPool, RAiSD_Info_FP);	

	RSDChunk_t * RSDChunk = RSDChunk_new();
	RSDChunk_init(RSDChunk, RSDCommandLine, RSDDataset->numberOfSamples);
	
	RSDMuStat_t * RSDMuStat = RSDMuStat_new();	
	RSDMuStat_setReportName (RSDMuStat, RSDCommandLine, RAiSD_Info_FP);	
	RSDMuStat_loadExcludeTable (RSDMuStat, RSDCommandLine);	
	
	RSDVcf2ms_t * RSDVcf2ms = RSDVcf2ms_new (RSDCommandLine);	

	int setIndex = -1, validSetIndex = -1, setDone = 0, setsProcessedTotal=0; // validsetindex is used with the RSDResults_t struct
			
#ifdef _RSDAI
	int warningMsgEn=1;
#endif	
	
	// Set processing
	while(RSDDataset_goToNextSet(RSDDataset)!=EOF) 
	{
		RSDDataset_setPosition (RSDDataset, &setIndex);

		RSDMuStat->currentScoreIndex=-1;

		if(setIndexValid!=-1 && setIndex!=setIndexValid)
		{
			char tchar = (char)fgetc(RSDDataset->inputFilePtr); // Note: this might generate a segfault with MakefileZLIB
			tchar = tchar - tchar;
			assert(tchar==0);
		}

		if(setIndexValid==-1 || setIndex == setIndexValid)
		{
		
#if _RSDAI
			validSetIndex++;
			
			RSDResults_incrementSetCounter (RSDResults);
			RSDResults_saveSetID (RSDResults, RSDDataset);
						
			if(RSDCommandLine->opCode==OP_DEF)
			{
				RSDMuStat_setReportNamePerSet (RSDMuStat, RSDCommandLine, RAiSD_Info_FP, RSDDataset, RSDCommonOutliers);
				
				assert(RSDMuStat->reportFP!=NULL);
			
				if(RSDCommandLine->setSeparator)
					fprintf(RSDMuStat->reportFP, "// %s\n", RSDDataset->setID);
			
			}
#else
			RSDMuStat_setReportNamePerSet (RSDMuStat, RSDCommandLine, RAiSD_Info_FP, RSDDataset, RSDCommonOutliers);
			
			if(RSDCommandLine->setSeparator)
				fprintf(RSDMuStat->reportFP, "// %s\n", RSDDataset->setID);
#endif				

			RSDMuStat_init (RSDMuStat, RSDCommandLine);
			RSDMuStat_excludeRegion (RSDMuStat, RSDDataset);

			setDone = 0;

			RSDChunk->chunkID = -1;	
			RSDChunk_reset(RSDChunk, RSDCommandLine);

			RSDPatternPool_reset(RSDPatternPool, RSDDataset->numberOfSamples, RSDDataset->setSamples, RSDChunk, RSDCommandLine);	

			setDone = RSDDataset_getFirstSNP(RSDDataset, RSDPatternPool, RSDChunk, RSDCommandLine, RSDCommandLine->regionLength, RSDCommandLine->maf, RAiSD_Info_FP);
#if _RSDAI
			if(RSDCommandLine->opCode==OP_USE_CNN && RSDNeuralNetwork->imageHeight!=RSDDataset->numberOfSamples)
			{
				if(RSDNeuralNetwork->dataFormat==1 && RSDNeuralNetwork->dataType==1 && warningMsgEn==1)
				{
					warningMsgEn = 0;
					
					fprintf(RAiSD_Info_FP, "\nWARNING: Mismatch between the sample size (%d) and the trained model (height %d)! Classification accuracy might be negatively affected! \n\n", RSDDataset->numberOfSamples, RSDNeuralNetwork->imageHeight);		
					fprintf(stderr, "\nWARNING: Mismatch between the sample size (%d) and the trained model (height %d)! Classification accuracy might be negatively affected!\n\n", RSDDataset->numberOfSamples, RSDNeuralNetwork->imageHeight);
				}
				else
				{
					if(!(RSDNeuralNetwork->dataFormat==1 && RSDNeuralNetwork->dataType==1))
					{
						fprintf(RAiSD_Info_FP, "\nERROR: Set %s sample size (%d) is incompatible with the trained model (expected %d)!\n\n",RSDDataset->setID, RSDDataset->numberOfSamples, RSDNeuralNetwork->imageHeight);		
						fprintf(stderr, "\nERROR: Set %s sample size (%d) is incompatible with the trained model (expected %d)!\n\n",RSDDataset->setID, RSDDataset->numberOfSamples, RSDNeuralNetwork->imageHeight);
		
						exit(0);
					}
				}
			}	
#endif			
			if(setDone)
			{
		      		RSDDataset_writeOutput (RSDDataset, setIndex, RAiSD_Info_FP);
		      		
		      		if(RSDCommandLine->displayProgress==1)	
					RSDDataset_writeOutput (RSDDataset, setIndex, stdout);										      

				if(RSDCommandLine->displayDiscardedReport==1)
					RSDDataset_printSiteReport (RSDDataset, RAiSD_SiteReport_FP, setIndex, RSDCommandLine->imputePerSNP, RSDCommandLine->createPatternPoolMask);

				RSDDataset_resetSiteCounters (RSDDataset);	

				continue;
			}
			RSDPatternPool_resize (RSDPatternPool, RSDDataset->setSamples, RAiSD_Info_FP);
#ifdef _HM
			RSDHashMap_free(RSDPatternPool->hashMap);
			RSDPatternPool->hashMap = RSDHashMap_new();
			RSDHashMap_init (RSDPatternPool->hashMap, RSDDataset->setSamples, RSDPatternPool->maxSize, RSDPatternPool->patternSize);
#endif
#ifdef _LM
			RSDLutMap_free(RSDPatternPool->lutMap);
			RSDPatternPool->lutMap =  RSDLutMap_new();
			RSDLutMap_init (RSDPatternPool->lutMap, RSDDataset->setSamples);
#endif
			RSDPatternPool_pushSNP (RSDPatternPool, RSDChunk, RSDDataset->setSamples, RSDCommandLine, (void*)RSDVcf2ms);

			//int sitesloaded = 0;
			//int patternsloaded = 0;
			
			// Chunk processing
			while(!setDone) 
			{
				RSDChunk->chunkID++;

				if(RSDCommandLine->vcf2msExtra == VCF2MS_CONVERT && RSDChunk->chunkID!=0)
				{
					fprintf(stderr, "\nERROR: Insufficient memory size provided through -Q for VCF-to-ms conversion!\n\n");
					exit(0);
				}

				int poolFull = 0;

				// SNP processing
				while(!poolFull && !setDone) 
				{
					setDone = RSDDataset_getNextSNP(RSDDataset, RSDPatternPool, RSDChunk, RSDCommandLine, RSDDataset->setRegionLength, RSDCommandLine->maf, RAiSD_Info_FP);
					poolFull = RSDPatternPool_pushSNP (RSDPatternPool, RSDChunk, RSDDataset->setSamples, RSDCommandLine, (void*)RSDVcf2ms); 
				}
	
				RSDPatternPool_assessMissing (RSDPatternPool, RSDDataset->setSamples);

				// version 2.4, for ms
				if(!strcmp(RSDDataset->inputFileFormat, "ms"))
				{
					//printf("%d - %d vs %d\n", RSDChunk->chunkID, (int)RSDDataset->setSNPs, (int)RSDDataset->preLoadedsetSNPs);
					//fflush(stdout);

					assert((uint64_t)RSDDataset->setSNPs==RSDDataset->preLoadedsetSNPs); // Fails when ms contains monomorphic sites
				}

#ifdef _PTIMES
				clock_gettime(CLOCK_REALTIME, &requestStartMu);
#endif

#ifdef _RSDAI				
				switch(RSDCommandLine->opCode)
				{
					case OP_CREATE_IMAGES:								
						RSDImage_init (RSDImage, RSDDataset, RSDMuStat, RSDPatternPool, RSDCommandLine, RSDChunk, validSetIndex, RAiSD_Info_FP);
						
						RSDImage_generateFullFrame (RSDImage, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RAiSD_Info_FP, RSDImage->destinationPath, 0, validSetIndex);		
						
						if((RSDCommandLine->fullFrame==0) && (RSDImage->generatedSetImages != RSDCommandLine->imagesPerSimulation))
						{
						 	RSDGridPoint_t * RSDGridPoint = RSDGridPoint_compute((void*)RSDImage, RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, 
						 										   RSDCommandLine, 
						 										   RAiSD_Info_FP, 
						 										   RSDCommandLine->imageTargetSite, 
						 										   RSDImage->destinationPath, 
						 										   0, validSetIndex); 		
							RSDGridPoint_free(RSDGridPoint);
						}												
						break;
												
					case OP_USE_CNN:
						RSDImage_init (RSDImage, RSDDataset, RSDMuStat, RSDPatternPool, RSDCommandLine, RSDChunk, validSetIndex, RAiSD_Info_FP);					
						RSDGrid_init (RSDGrid, RSDDataset, RSDChunk, RSDMuStat, RSDCommandLine, setDone);
						RSDGrid_processChunk (RSDGrid, RSDImage, RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RSDResults);
						break;
					
					default: // OP_DEF 
						if(RSDCommandLine->gridSize==-1)
						{	
							// sliding-window mu
							RSDMuStat_scanChunk (RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RAiSD_Info_FP); 			
						}
						else
						{
							// grid-based mu
							RSDGrid_init (RSDGrid, RSDDataset, RSDChunk, RSDMuStat, RSDCommandLine, setDone);
							int firstGridPointIndexInChunk =  RSDMuStat->currentScoreIndex+1;
							// RSDGrid_processChunk stores scores in both RSDResults and RSDMuStat for backwards compatibility 													
							RSDGrid_processChunk (RSDGrid, RSDImage, RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RSDResults);	
							RSDResults_processSet (RSDResults, RSDCommandLine, RSDMuStat, validSetIndex, RSDGrid->size, firstGridPointIndexInChunk); 
						}
						break;
				}
#else
				// Compute Mu statistic
				RSDMuStat_scanChunk (RSDMuStat, RSDChunk, RSDPatternPool, RSDDataset, RSDCommandLine, RAiSD_Info_FP);
#endif			
#ifdef _PTIMES
				clock_gettime(CLOCK_REALTIME, &requestEndMu);
				double MuTime = (requestEndMu.tv_sec-requestStartMu.tv_sec)+ (requestEndMu.tv_nsec-requestStartMu.tv_nsec) / BILLION;
				TotalMuTime += MuTime;
#endif
				//sitesloaded+=RSDChunk->chunkSize;
				//patternsloaded += RSDPatternPool->dataSize;

				RSDChunk_reset(RSDChunk, RSDCommandLine);
				RSDPatternPool_reset(RSDPatternPool, RSDDataset->numberOfSamples, RSDDataset->setSamples, RSDChunk, RSDCommandLine);
			}
			
			if(RSDCommandLine->opCode==OP_DEF && RSDCommandLine->createPlot==1) 
				RSDPlot_createPlot (RSDCommandLine, RSDDataset, RSDMuStat, RSDCommonOutliers, RSDPLOT_BASIC_MU, NULL);
				
			if(RSDCommandLine->displayDiscardedReport==1)
				RSDDataset_printSiteReport (RSDDataset, RAiSD_SiteReport_FP, setIndex, RSDCommandLine->imputePerSNP, RSDCommandLine->createPatternPoolMask);

			RSDDataset_resetSiteCounters (RSDDataset);
			
			// VCF2MS
			if(RSDCommandLine->vcf2msExtra == VCF2MS_CONVERT)
			{
				if(RSDVcf2ms->status==0)
				{
					RSDVcf2ms->status=1;
					RSDVcf2ms_printHeader (RSDVcf2ms);
				}

				RSDVcf2ms_printSegsitesAndPositions (RSDVcf2ms);
				RSDVcf2ms_printSNPData (RSDVcf2ms);

				RSDVcf2ms_reset (RSDVcf2ms);
			}
			
			// PRINT MAX SCORES OR IMAGE COUNT TO INFO FILE
			if(RSDCommandLine->opCode==OP_CREATE_IMAGES || RSDCommandLine->opCode==OP_USE_CNN)
				RSDImage_writeOutput (RSDImage, RSDCommandLine, RSDDataset, setIndex, RAiSD_Info_FP);
			else			
				RSDMuStat_writeOutput (RSDMuStat, RSDDataset, setIndex, RAiSD_Info_FP);
				
			// EVALUATION (for standard sliding-window and grid without CNN)
			if(RSDCommandLine->opCode==OP_DEF)
			{
				if(RSDCommandLine->gridSize==-1)
					RSDEval_calculateDetectionMetrics (RSDEval, (void*)RSDMuStat);
				else
					RSDEval_calculateDetectionMetrics (RSDEval, (void*)RSDResults);
			}

			// PRINT MAX SCORES OR IMAGE COUNT TO STDOUT
			if(RSDCommandLine->displayProgress==1)
			{			
				if(RSDCommandLine->opCode==OP_CREATE_IMAGES || RSDCommandLine->opCode==OP_USE_CNN)
					RSDImage_writeOutput (RSDImage, RSDCommandLine, RSDDataset, setIndex, stdout);
				else			
					RSDMuStat_writeOutput (RSDMuStat, RSDDataset, setIndex, stdout);
			}
			
			setsProcessedTotal++;			

			if(setIndex == setIndexValid)
				break;	
		}		
	}	
			
#ifdef _RSDAI
	if(RSDCommandLine->opCode==OP_USE_CNN)
	{
		RSDNeutralNetwork_run (RSDNeuralNetwork, RSDCommandLine, (void*)RSDGrid, RAiSD_Info_FP);
		
		if(!strcmp(RSDNeuralNetwork->networkArchitecture, ARC_SWEEPNETRECOMB))
			RSDResults_load_2x2 (RSDResults, RSDCommandLine);
		else
			RSDResults_load (RSDResults, RSDCommandLine);			

		/* this function processes all sets - USE-CNN only*/	
		RSDResults_process (RSDResults, RSDNeuralNetwork, RSDCommandLine, RSDDataset, RSDMuStat, RSDCommonOutliers, RSDEval); 
	}	
#endif	

	fprintf(stdout, "\n");
	fprintf(stdout, " Sets (total)         :\t%d\n", setIndex+1);
	fprintf(stdout, " Sets (processed)     :\t%d\n", setsProcessedTotal);
	fprintf(stdout, " Sets (not processed) :\t%d\n", setIndex+1-setsProcessedTotal);

	fprintf(RAiSD_Info_FP, "\n");
	fprintf(RAiSD_Info_FP, " Sets (total)         :\t%d\n", setIndex+1);
	fprintf(RAiSD_Info_FP, " Sets (processed)     :\t%d\n", setsProcessedTotal);
	fprintf(RAiSD_Info_FP, " Sets (not processed) :\t%d\n", setIndex+1-setsProcessedTotal);
	
#ifdef _RSDAI
	switch(RSDCommandLine->opCode)
	{
		case OP_CREATE_IMAGES:
		
			fprintf(stdout, "\n");
			fprintf(stdout, " Output directory     :\t%s\n", RSDImage->destinationPath);
			fprintf(stdout, " Data information     :\tRAiSD_Images.%s/info.txt\n", RSDCommandLine->runName); 
			fprintf(stdout, " Images (total)       :\t%lu\n", RSDImage->totalGeneratedImages);
			
			fprintf(RAiSD_Info_FP, "\n");
			fprintf(RAiSD_Info_FP, " Output directory     :\t%s\n", RSDImage->destinationPath);
			fprintf(RAiSD_Info_FP, " Data information     :\tRAiSD_Images.%s/info.txt\n", RSDCommandLine->runName);
			fprintf(RAiSD_Info_FP, " Images (total)       :\t%lu\n", RSDImage->totalGeneratedImages);
			
			break;
		default:
			break;
	}		
#endif

	fflush(stdout);
	fflush(RAiSD_Info_FP);

	RSDEval_print (RSDEval, (void*)RSDNeuralNetwork, RSDCommandLine, setsProcessedTotal, stdout);
	RSDEval_print (RSDEval, (void*)RSDNeuralNetwork, RSDCommandLine, setsProcessedTotal, RAiSD_Info_FP);	

	RSDVcf2ms_free (RSDVcf2ms, RSDCommandLine);

	RSDPlot_removeRscript(RSDCommandLine, RSDPLOT_BASIC_MU);

	if(RSDCommandLine->createMPlot==1)
	{
		RSDPlot_generateRscript(RSDCommandLine, RSDPLOT_MANHATTAN);
		RSDPlot_createPlot (RSDCommandLine, RSDDataset, RSDMuStat, RSDCommonOutliers, RSDPLOT_MANHATTAN, NULL);		
		RSDPlot_removeRscript(RSDCommandLine, RSDPLOT_MANHATTAN);
	}

	if(RSDCommandLine->createCOPlot==1)
		RSDCommonOutliers_process (RSDCommonOutliers, RSDCommandLine);
	
#ifdef _RSDAI
	RSDImage_free (RSDImage);
	RSDNeuralNetwork_free(RSDNeuralNetwork);
	RSDGrid_free (RSDGrid);
	RSDResults_free (RSDResults);
	RSDEval_free (RSDEval);
#endif

	RSDCommonOutliers_free (RSDCommonOutliers);
	RSDCommandLine_free(RSDCommandLine);
	RSDPatternPool_free(RSDPatternPool);
	RSDChunk_free(RSDChunk);
	RSDDataset_free(RSDDataset);
	RSDMuStat_free(RSDMuStat);
	
	RSD_printTime(stdout, RAiSD_Info_FP);
	RSD_printMemory(stdout, RAiSD_Info_FP);

	fclose(RAiSD_Info_FP);

	if(RAiSD_SiteReport_FP!=NULL)
		fclose(RAiSD_SiteReport_FP);	

	return 0;
}
