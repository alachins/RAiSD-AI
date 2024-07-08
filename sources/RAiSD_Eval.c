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

void (*RSDEval_calculateDetectionMetrics) (RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults);

RSDEval_t * RSDEval_new	(RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
		
	if(RSDCommandLine->opCode!=OP_DEF && RSDCommandLine->opCode!=OP_USE_CNN)
		return NULL;
				
	if(!(RSDCommandLine->selectionTarget!=0ull || 
	   RSDCommandLine->selectionTargetDThreshold!=0ull ||
	   RSDCommandLine->fprLoc!=0.0 ||
	   RSDCommandLine->tprThresMuVar!=0.0 ||
	   RSDCommandLine->tprThresMuSfs!=0.0 ||
	   RSDCommandLine->tprThresMuLd!=0.0 ||
	   RSDCommandLine->tprThresMu!=0.0 ||
	   RSDCommandLine->tprThresNnPositiveClass0!=0.0 ||
	   RSDCommandLine->tprThresNnPositiveClass1!=0.0))
		return NULL;	
		
	RSDEval_t * RSDEval = (RSDEval_t *)rsd_malloc(sizeof(RSDEval_t));
	assert(RSDEval!=NULL);
	
	RSDEval->selectionTarget = 0ull;
	RSDEval->muVarAccum = 0.0;
	RSDEval->muSfsAccum = 0.0;
	RSDEval->muLdAccum = 0.0;
	RSDEval->muAccum = 0.0;
	RSDEval->nnPositiveClass0Accum = 0.0;
	RSDEval->nnPositiveClass1Accum = 0.0;
	RSDEval->selectionTargetDThreshold = 0ull;
	RSDEval->muVarSuccess = 0.0;
	RSDEval->muSfsSuccess = 0.0;
	RSDEval->muLdSuccess = 0.0;
	RSDEval->muSuccess = 0.0;
	RSDEval->nnPositiveClass0Success = 0.0;
	RSDEval->nnPositiveClass1Success= 0.0;
	RSDEval->fprLoc = 0.0;
	
	RSDEval->muVarSortVecSz = 0;
	RSDEval->muSfsSortVecSz = 0;
	RSDEval->muLdSortVecSz = 0;	
	RSDEval->muSortVecSz = 0;
	RSDEval->nnPositiveClass0SortVecSz = 0;
	RSDEval->nnPositiveClass1SortVecSz = 0;	
	RSDEval->muVarSortVec = NULL;
	RSDEval->muSfsSortVec = NULL;
	RSDEval->muLdSortVec = NULL;	
	RSDEval->muSortVec = NULL;
	RSDEval->nnPositiveClass0SortVec = NULL;
	RSDEval->nnPositiveClass1SortVec = NULL;	
	
	RSDEval->tprThresMuVar = 0.0;
	RSDEval->tprThresMuSfs = 0.0;
	RSDEval->tprThresMuLd = 0.0;
	RSDEval->tprThresMu = 0.0;
	RSDEval->tprThresNnPositiveClass0 = 0.0;
	RSDEval->tprThresNnPositiveClass1 = 0.0;
	RSDEval->tprScrMuVar = 0.0;
	RSDEval->tprScrMuSfs = 0.0;
	RSDEval->tprScrMuLd = 0.0;
	RSDEval->tprScrMu = 0.0;
	RSDEval->tprScrNnPositiveClass0 = 0.0;
	RSDEval->tprScrNnPositiveClass1 = 0.0;			
	
	return RSDEval;
}

void RSDEval_free (RSDEval_t * RSDEval)
{
	if(RSDEval==NULL)
		return;
	
	if(RSDEval->muVarSortVec!=NULL)
		free(RSDEval->muVarSortVec);
		
	if(RSDEval->muSfsSortVec!=NULL)
		free(RSDEval->muSfsSortVec);
		
	if(RSDEval->muLdSortVec!=NULL)
		free(RSDEval->muLdSortVec);
		
	if(RSDEval->muSortVec!=NULL)
		free(RSDEval->muSortVec);
		
	if(RSDEval->nnPositiveClass0SortVec!=NULL)
		free(RSDEval->nnPositiveClass0SortVec);
		
	if(RSDEval->nnPositiveClass1SortVec!=NULL)
		free(RSDEval->nnPositiveClass1SortVec);
				
	free(RSDEval);	
	RSDEval=NULL;
}

void RSDEval_init (RSDEval_t * RSDEval, RSDCommandLine_t * RSDCommandLine)
{
	if(RSDEval==NULL)
		return;
		
	assert(RSDEval!=NULL);
	assert(RSDCommandLine!=NULL);
	
	RSDEval->selectionTarget = RSDCommandLine->selectionTarget;
	RSDEval->selectionTargetDThreshold = RSDCommandLine->selectionTargetDThreshold;
	RSDEval->fprLoc = RSDCommandLine->fprLoc;	
	
	RSDEval->tprThresMuVar = RSDCommandLine->tprThresMuVar;
	RSDEval->tprThresMuSfs = RSDCommandLine->tprThresMuSfs;
	RSDEval->tprThresMuLd = RSDCommandLine->tprThresMuLd;
	RSDEval->tprThresMu = RSDCommandLine->tprThresMu;
	RSDEval->tprThresNnPositiveClass0 = RSDCommandLine->tprThresNnPositiveClass0;
	RSDEval->tprThresNnPositiveClass1 = RSDCommandLine->tprThresNnPositiveClass1;

	assert(RSDEval->selectionTarget>=1);
	assert(RSDEval->selectionTargetDThreshold>=1);
	
	if(RSDCommandLine->regionLength!=0ull)
	{
		assert(RSDEval->selectionTarget<=RSDCommandLine->regionLength);
		assert(RSDEval->selectionTargetDThreshold<=RSDCommandLine->regionLength);
	}
}

void RSDEval_calcAccumSuccess (RSDEval_t * RSDEval, double * Accum, double * Success, double scoreMaxLoc)
{
	assert(RSDEval!=NULL);
	assert(Accum!=NULL);
	assert(Success!=NULL);
	
	double dist = DIST (scoreMaxLoc, (double)RSDEval->selectionTarget);
	
	(*Accum) += dist;
	
	if(RSDEval->selectionTargetDThreshold!=0ull)
	{
		if(dist<=RSDEval->selectionTargetDThreshold)
			(*Success) += 1.0;
	}
}

void RSDEval_calcTprScrSum (double tprThres, double * tprScr, float scrMax)
{
	if(tprThres>0.0)
		if(scrMax>=(float)tprThres)
			(*tprScr) += 1.0;
}

void RSDEval_calculateDetectionMetricsSlidingWindow (RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults)
{
	if(RSDEval==NULL)
		return;
		
	assert(RSDEval!=NULL);
	assert(RSDMuStat_or_RSDResults!=NULL);
	
	RSDMuStat_t * RSDMuStat = (RSDMuStat_t *)RSDMuStat_or_RSDResults;
	
	// SUCCESS RATE and DETECTION ACCURACY	
	if(RSDEval->selectionTarget!=0ull)
	{
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muVarAccum), &(RSDEval->muVarSuccess), RSDMuStat->muVarMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muSfsAccum), &(RSDEval->muSfsSuccess), RSDMuStat->muSfsMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muLdAccum), &(RSDEval->muLdSuccess), RSDMuStat->muLdMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muAccum), &(RSDEval->muSuccess), RSDMuStat->muMaxLoc);
	}
	
	// FPR
	if(RSDEval->fprLoc>0.0)
	{
		RSDEval->muVarSortVec = putInSortVector(&(RSDEval->muVarSortVecSz), RSDEval->muVarSortVec, RSDMuStat->muVarMax);
		RSDEval->muSfsSortVec = putInSortVector(&(RSDEval->muSfsSortVecSz), RSDEval->muSfsSortVec, RSDMuStat->muSfsMax);
		RSDEval->muLdSortVec = putInSortVector(&(RSDEval->muLdSortVecSz), RSDEval->muLdSortVec, RSDMuStat->muLdMax);
		RSDEval->muSortVec = putInSortVector(&(RSDEval->muSortVecSz), RSDEval->muSortVec, RSDMuStat->muMax);
	}
	
	//TPR
	RSDEval_calcTprScrSum (RSDEval->tprThresMuVar, &(RSDEval->tprScrMuVar), RSDMuStat->muVarMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMuSfs, &(RSDEval->tprScrMuSfs), RSDMuStat->muSfsMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMuLd, &(RSDEval->tprScrMuLd), RSDMuStat->muLdMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMu, &(RSDEval->tprScrMu), RSDMuStat->muMax);
}

void RSDEval_calculateDetectionMetricsGrid (RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults)
{
	if(RSDEval==NULL)
		return;
		
	assert(RSDEval!=NULL);
	assert(RSDMuStat_or_RSDResults!=NULL);
	
	RSDResults_t * RSDResults = (RSDResults_t *)RSDMuStat_or_RSDResults; 	
	
	// SUCCESS RATE and DETECTION ACCURACY	
	if(RSDEval->selectionTarget!=0ull)
	{
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muVarAccum), &(RSDEval->muVarSuccess), RSDResults->muVarMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muSfsAccum), &(RSDEval->muSfsSuccess), RSDResults->muSfsMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muLdAccum), &(RSDEval->muLdSuccess), RSDResults->muLdMaxLoc);
		RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->muAccum), &(RSDEval->muSuccess), RSDResults->muMaxLoc);
		
		if(RSDResults->nnPositiveClass0MaxLoc!=-1.0) // equivalent to: RSDCommandLine->opCode == OP_USE_CNN
		{
			RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->nnPositiveClass0Accum), &(RSDEval->nnPositiveClass0Success), RSDResults->nnPositiveClass0MaxLoc);
			RSDEval_calcAccumSuccess (RSDEval, &(RSDEval->nnPositiveClass1Accum), &(RSDEval->nnPositiveClass1Success), RSDResults->nnPositiveClass1MaxLoc);
		}
	}
	
	// FPR
	if(RSDEval->fprLoc>0.0)
	{
		RSDEval->muVarSortVec = putInSortVector(&(RSDEval->muVarSortVecSz), RSDEval->muVarSortVec, RSDResults->muVarMax);
		RSDEval->muSfsSortVec = putInSortVector(&(RSDEval->muSfsSortVecSz), RSDEval->muSfsSortVec, RSDResults->muSfsMax);
		RSDEval->muLdSortVec = putInSortVector(&(RSDEval->muLdSortVecSz), RSDEval->muLdSortVec, RSDResults->muLdMax);
		RSDEval->muSortVec = putInSortVector(&(RSDEval->muSortVecSz), RSDEval->muSortVec, RSDResults->muMax);
		
		if(RSDResults->nnPositiveClass0MaxLoc!=-1.0) // equivalent to: RSDCommandLine->opCode == OP_USE_CNN
		{
			RSDEval->nnPositiveClass0SortVec = putInSortVector(&(RSDEval->nnPositiveClass0SortVecSz), RSDEval->nnPositiveClass0SortVec, RSDResults->nnPositiveClass0Max);
			RSDEval->nnPositiveClass1SortVec = putInSortVector(&(RSDEval->nnPositiveClass1SortVecSz), RSDEval->nnPositiveClass1SortVec, RSDResults->nnPositiveClass1Max);
		}
	}
	
	//TPR
	RSDEval_calcTprScrSum (RSDEval->tprThresMuVar, &(RSDEval->tprScrMuVar), RSDResults->muVarMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMuSfs, &(RSDEval->tprScrMuSfs), RSDResults->muSfsMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMuLd, &(RSDEval->tprScrMuLd), RSDResults->muLdMax);
	RSDEval_calcTprScrSum (RSDEval->tprThresMu, &(RSDEval->tprScrMu), RSDResults->muMax);
					
	if(RSDResults->nnPositiveClass0MaxLoc!=-1.0) // equivalent to: RSDCommandLine->opCode == OP_USE_CNN
	{				
		RSDEval_calcTprScrSum (RSDEval->tprThresNnPositiveClass0, &(RSDEval->tprScrNnPositiveClass0),RSDResults->nnPositiveClass0Max);
		RSDEval_calcTprScrSum (RSDEval->tprThresNnPositiveClass1, &(RSDEval->tprScrNnPositiveClass1),RSDResults->nnPositiveClass1Max);		
	}					
}

void RSDEval_calculateDetectionMetricsConfigure (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);	
	
	if(RSDCommandLine->gridSize==-1)
		RSDEval_calculateDetectionMetrics = &RSDEval_calculateDetectionMetricsSlidingWindow;
	else
		RSDEval_calculateDetectionMetrics = &RSDEval_calculateDetectionMetricsGrid; 

}

void RSDEval_print (RSDEval_t * RSDEval, void * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, int sets, FILE * fpOut)
{
	if(RSDEval==NULL)
		return;

	assert(RSDEval!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);
	assert(sets>=1);
	
	char nnPositiveClass0Label[STRING_SIZE], nnPositiveClass1Label[STRING_SIZE];
	nnPositiveClass0Label[0]='\0';
	nnPositiveClass1Label[0]='\0'; 
	
	int slen = 21, slen1=7, slen2 = 0, sortedVecIndex = -1;
	
	char muVar[STRING_SIZE] = "muVar";
	char muSFS[STRING_SIZE] = "muSFS";
	char muLD[STRING_SIZE] = "muLD";
	char mu[STRING_SIZE] = "mu";	
	
	if(RSDNeuralNetwork!=NULL)
	{
		RSDNeuralNetwork_getColumnHeaders ((RSDNeuralNetwork_t *)RSDNeuralNetwork, RSDCommandLine, nnPositiveClass0Label, nnPositiveClass1Label);
		
		slen=getStringLengthString (slen, nnPositiveClass0Label);
		slen=getStringLengthString (slen, nnPositiveClass1Label);  	
	}
			
	if(RSDEval->selectionTarget!=0ull)
	{		
		fprintf(fpOut, "\n");
		fprintf(fpOut, " Average distance from target site position %lu \n\n",  RSDEval->selectionTarget);
		
		slen1=getStringLengthDouble1 (slen1, RSDEval->muVarAccum/sets);
		slen1=getStringLengthDouble1 (slen1, RSDEval->muSfsAccum/sets);
		slen1=getStringLengthDouble1 (slen1, RSDEval->muLdAccum/sets);
		slen1=getStringLengthDouble1 (slen1, RSDEval->muAccum/sets);
		
		if(RSDNeuralNetwork!=NULL)
		{
			slen1=getStringLengthDouble1 (slen1, RSDEval->nnPositiveClass0Accum/sets);
			slen1=getStringLengthDouble1 (slen1, RSDEval->nnPositiveClass1Accum/sets);
		} 
		
		fprintf(fpOut, " %-*s:\t%*.1f\n", slen, muVar, slen1, RSDEval->muVarAccum/sets);
		fprintf(fpOut, " %-*s:\t%*.1f\n", slen, muSFS, slen1, RSDEval->muSfsAccum/sets);
		fprintf(fpOut, " %-*s:\t%*.1f\n", slen, muLD, slen1, RSDEval->muLdAccum/sets);
		fprintf(fpOut, " %-*s:\t%*.1f\n", slen, mu, slen1, RSDEval->muAccum/sets);
				
		if(RSDNeuralNetwork!=NULL)
		{				
			fprintf(fpOut, " %-*s:\t%*.1f\n", slen, nnPositiveClass0Label, slen1, RSDEval->nnPositiveClass0Accum/sets);
			fprintf(fpOut, " %-*s:\t%*.1f\n", slen, nnPositiveClass1Label, slen1, RSDEval->nnPositiveClass1Accum/sets);				
		}				
						
		if(RSDEval->selectionTargetDThreshold!=0ull)
		{
			fprintf(fpOut, "\n");
			fprintf(fpOut, " Success rate based on max distance of %lu from target site \n\n", RSDEval->selectionTargetDThreshold); 
			
			fprintf(fpOut, " %-*s:\t%*.5f\n", slen, muVar, slen1, RSDEval->muVarSuccess/sets);
			fprintf(fpOut, " %-*s:\t%*.5f\n", slen, muSFS, slen1, RSDEval->muSfsSuccess/sets);
			fprintf(fpOut, " %-*s:\t%*.5f\n", slen, muLD, slen1, RSDEval->muLdSuccess/sets);
			fprintf(fpOut, " %-*s:\t%*.5f\n", slen, mu, slen1, RSDEval->muSuccess/sets);
					
			if(RSDNeuralNetwork!=NULL)
			{				
				fprintf(fpOut, " %-*s:\t%*.5f\n", slen, nnPositiveClass0Label, slen1, RSDEval->nnPositiveClass0Success/sets);
				fprintf(fpOut, " %-*s:\t%*.5f\n", slen, nnPositiveClass1Label, slen1, RSDEval->nnPositiveClass1Success/sets);
			}
		}
	}
	
	if(RSDEval->fprLoc>0.0)
	{	
		assert((RSDEval->muVarSortVecSz == RSDEval->muSfsSortVecSz) == (RSDEval->muLdSortVecSz == RSDEval->muSortVecSz));
		
		sortedVecIndex = (int)(RSDEval->muVarSortVecSz*RSDEval->fprLoc);
		
		slen2=getStringLengthDouble5 (slen2, RSDEval->muVarSortVec[sortedVecIndex]); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->muSfsSortVec[sortedVecIndex]); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->muLdSortVec[sortedVecIndex]); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->muSortVec[sortedVecIndex]); 

		if(RSDNeuralNetwork!=NULL)
		{
			assert(RSDEval->muVarSortVecSz == (RSDEval->nnPositiveClass0SortVecSz == RSDEval->nnPositiveClass1SortVecSz));
			slen2=getStringLengthDouble5 (slen2, RSDEval->nnPositiveClass0SortVec[sortedVecIndex]); 
			slen2=getStringLengthDouble5 (slen2, RSDEval->nnPositiveClass1SortVec[sortedVecIndex]);
		}
					
		fprintf(fpOut, "\n");
		fprintf(fpOut, " FPR threshold for FPR %f (sorted vector index %d) \n\n", RSDEval->fprLoc, sortedVecIndex);

		fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, muVar, slen2, (double)RSDEval->muVarSortVec[sortedVecIndex], 
											    (double)RSDEval->muVarSortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->muVarSortVec[0]);
											
		fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, muSFS, slen2, (double)RSDEval->muSfsSortVec[sortedVecIndex], 
											    (double)RSDEval->muSfsSortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->muSfsSortVec[0]);
		
		fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, muLD, slen2, (double)RSDEval->muLdSortVec[sortedVecIndex], 
											   (double)RSDEval->muLdSortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->muLdSortVec[0]);
											
		fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, mu, slen2, (double)RSDEval->muSortVec[sortedVecIndex], 
											 (double)RSDEval->muSortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->muSortVec[0]);
			
		if(RSDNeuralNetwork!=NULL)
		{								
			fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, nnPositiveClass0Label, slen2, (double)RSDEval->nnPositiveClass0SortVec[sortedVecIndex], 
										(double)RSDEval->nnPositiveClass0SortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->nnPositiveClass0SortVec[0]);
		
			fprintf(fpOut, " %-*s:\t%-*.5f (min %.5f, max %.5f)\n", slen, nnPositiveClass1Label, slen2, (double)RSDEval->nnPositiveClass1SortVec[sortedVecIndex], 
										(double)RSDEval->nnPositiveClass1SortVec[RSDEval->muVarSortVecSz-1], (double)RSDEval->nnPositiveClass1SortVec[0]);						
		}					
	}
	
	if(RSDEval->tprThresMuVar>0.0 || RSDEval->tprThresMuSfs>0.0 || RSDEval->tprThresMuLd>0.0 || RSDEval->tprThresMu>0.0 || 
	   RSDEval->tprThresNnPositiveClass0>0.0 || RSDEval->tprThresNnPositiveClass1>0.0)
	{
		RSDEval->tprScrMuVar /= sets;
		RSDEval->tprScrMuSfs /= sets;
		RSDEval->tprScrMuLd /= sets;
		RSDEval->tprScrMu /= sets;
		
		slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrMuVar); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrMuSfs); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrMuLd); 
		slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrMu); 
	
		if(RSDNeuralNetwork!=NULL)
		{
			RSDEval->tprScrNnPositiveClass0 /= sets;
			RSDEval->tprScrNnPositiveClass1 /= sets;
		
			slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrNnPositiveClass0); 
			slen2=getStringLengthDouble5 (slen2, RSDEval->tprScrNnPositiveClass1);
		}
					
		fprintf(fpOut, "\n");
		fprintf(fpOut, " TPR score(s) for FPR threshold(s)\n\n");
		
		if(RSDEval->tprThresMuVar>0.0)
			fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, muVar, slen2, RSDEval->tprScrMuVar, RSDEval->tprThresMuVar);
		
		if(RSDEval->tprThresMuSfs>0.0)
			fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, muSFS, slen2, RSDEval->tprScrMuSfs, RSDEval->tprThresMuSfs);			
			
		if(RSDEval->tprThresMuLd>0.0)
			fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, muLD, slen2, RSDEval->tprScrMuLd, RSDEval->tprThresMuLd);			
			
		if(RSDEval->tprThresMu>0.0)
			fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, mu, slen2, RSDEval->tprScrMu, RSDEval->tprThresMu);
		
		if(RSDNeuralNetwork!=NULL)
		{	
			if(RSDEval->tprThresNnPositiveClass0>0.0)
				fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, nnPositiveClass0Label, slen2, RSDEval->tprScrNnPositiveClass0, RSDEval->tprThresNnPositiveClass0);
				
			if(RSDEval->tprThresNnPositiveClass1>0.0)
				fprintf(fpOut, " %-*s:\t%-*.5f (FPR threshold %.5f)\n", slen, nnPositiveClass1Label, slen2, RSDEval->tprScrNnPositiveClass1, RSDEval->tprThresNnPositiveClass1);		
		}
	}
}
