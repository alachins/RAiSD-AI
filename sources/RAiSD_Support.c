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

void	ignoreLineSpaces	(FILE *fp, char *ent);
int 	flagMatch		(FILE *fp, char flag[], int flaglength, char tmp);
void 	RSD_printTime 		(FILE * fp1, FILE * fp2);
void 	RSD_countMemory 	(size_t newMemSz);
void 	RSD_printMemory 	(FILE * fp1, FILE * fp2);
int 	RSD_Rscript_check	(void);
void 	RSD_Rscript_generate 	(void);
void 	RSD_Rscript_remove 	(void);
inline void *	rsd_malloc	(size_t size);
inline void *	rsd_realloc	(void * p, size_t size);
FILE * 	skipLine 		(FILE * fp);
int	matchChromInList 	(char * newChromName, char ** chromList, int chromListSize);
char ** addChromToList 		(char * newChromName, char ** chromList, int * chromListSize);


char POPCNT_U16_LUT [0x1u << 16];

/*
unsigned long long rdtsc(void)
{
	unsigned a, d;

	__asm__ volatile("rdtsc" : "=a" (a), "=d" (d));

	return ((unsigned long long)a) | (((unsigned long long)d) << 32);
}
*/

#ifndef _INTRINSIC_POPCOUNT
int popcount_u32_iterative (unsigned int n)
{
	int count=0;    
    
	while(n)
	{
		count += n & 0x1u ;    
		n >>= 1 ;
	}
	
	assert(count<=16);
	assert(count>=0);

	return count;
}

void popcount_u64_init (void)
{
	unsigned int i;    
	for (i = 0; i < (0x1u<<16); i++)
	{
		int t = popcount_u32_iterative(i);
		POPCNT_U16_LUT[i] = (char)t;
	}	
	
}
#endif

inline int rsd_popcnt_u64 (uint64_t input)
{
#ifndef _INTRINSIC_POPCOUNT
	return POPCNT_U16_LUT[input & 0xffffu] + POPCNT_U16_LUT[ (input>>16) & 0xffffu] + POPCNT_U16_LUT[ (input>>32) & 0xffffu] + POPCNT_U16_LUT[ (input>>48) & 0xffffu]; 
#else
	return _mm_popcnt_u64(input);
#endif
}

int snpv_cmp (uint64_t * A, uint64_t * B, int size)
{
	assert(A!=NULL);
	assert(B!=NULL);
	assert(size>=1);
	
	int i;
	for(i=0;i!=size;++i)
		if(A[i]!=B[i])
		{	
			return 1;
		}
	
	return 0;
}

int snpv_cmp_cross_masks (uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size)
{
	assert(A!=NULL);
	assert(B!=NULL);
	assert(size>=1);
	
	int i;
	for(i=0;i!=size;++i)
		if((A[i]&mB[i])!=(B[i]&mA[i]))
		{	
			return 1;
		}

	return 0;
}

int isnpv_cmp_cross_masks (uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size)
{	
	assert(A!=NULL);
	assert(B!=NULL);
	assert(size>=1);
	
	int i;
	for(i=0;i!=size;++i)
		if(((~A[i])&mA[i]&mB[i])!=(B[i]&mA[i]))
		{	
			return 1;
		}

	return 0;
}

int isnpv_cmp (uint64_t * A, uint64_t * B, int size, int numberOfSamples)
{
	assert(A!=NULL);
	assert(B!=NULL);
	assert(size>=1);
	
	int i;
	for(i=0;i!=size-1;++i)
	{
		if((~A[i])!=B[i])
		{
			return 1;
		}
	}
	uint64_t temp = ~B[size-1];
	int shiftLast = 64-(numberOfSamples-(size-1)*64);
	temp = temp << shiftLast;
	temp = temp >> shiftLast;
	if(temp!=A[size-1])
		return 1;

	return 0;
}

int isnpv_cmp_with_mask (uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size, int numberOfSamples)
{
	assert(A!=NULL);
	assert(B!=NULL);
	assert(size>=1);
	
	int i;
	for(i=0;i!=size-1;++i)
	{
		if(((~A[i])&mA[i])!=B[i])
		{
			return 1;
		}
	}

	uint64_t temp = (~B[size-1])&mB[size-1];
	int shiftLast = 64-(numberOfSamples-(size-1)*64);
	temp = temp << shiftLast;
	temp = temp >> shiftLast;
	if(temp!=A[size-1])
		return 1;

	return 0;
}

int getGXLocation_vcf (char * string, char * GX)
{
	assert(string!=NULL);
	
	char tstring [STRING_SIZE];
	int Location = 0;
	int i, length = (int)strlen(string);
	int startIndex = 0;
	int endIndex = 0;
	for(i=0;i<length;i++)
	{
		if(string[i]==':')
		{
			endIndex =  i;
			memcpy(tstring, &string[startIndex], (size_t)(endIndex-startIndex));
			tstring[endIndex]='\0';
			if(!strcmp(tstring, GX))
				return Location;
			
			Location++;
			startIndex = i+1;
		}
	}
	endIndex =  i;
	memcpy(tstring, &string[startIndex], (size_t)endIndex);
	tstring[endIndex]='\0';
	if(!strcmp(tstring, GX))
		return Location;

	return -1;	
}

int diploidyCheck(char * data)
{
	unsigned int i, count=0;	
	for(i=0;i<strlen(data);i++)
		count += (data[i]==','? 1:0);
	
	int check = count==2?1:0;
	return check;
}

void getGPProbs (char * data, double *p00, double *p01, double * p11, int isLik)
{
	char tstring[STRING_SIZE];
	unsigned int i;
	int tstr_i=0;
	
	for(i=0;i<strlen(data);i++)
	{
		if(data[i]==',')
		{
			tstring[tstr_i] = '\0';
			tstr_i=0;

			if(*p00<0.0)
				*p00 = atof(tstring);
			else
				*p01 = atof(tstring);			
			
		}
		else
			tstring[tstr_i++] = data[i];
	}

	tstring[tstr_i] = '\0';
	*p11 = atof(tstring);	

	if(isLik==0)
		assert(*p00>=0.0 && *p01>=0.0 && *p11>=0.0);
	else
		assert(*p00<=0.0 && *p01<=0.0 && *p11<=0.0);
}

void reconGT (char * data)
{
	assert(diploidyCheck(data)==1);

	double p00 = -1.0, p01 = -1.0, p11 = -1.0;
	getGPProbs(data, &p00, &p01, &p11, 0);

	double checksum = p00+p01+p11;
	assert(checksum>=0.999 && checksum<=1.001);

	int val = rand();
	double rval = ((double)val) / ((double)RAND_MAX);
	
	if(rval<p00)
		strcpy (data, "0/0");
	else
	{
		if(rval>=p00 && rval<p00+p01)
			strcpy (data, "0/1");
		else
			strcpy (data, "1/1");	
	}
}

int getGXData_vcf (char * string, int location, char * data)
{
	assert(string!=NULL);
	assert(location>=0);
	assert(data!=NULL);	

	int tLocation = 0;
	int i, length = (int)strlen(string);
	int startIndex = 0;
	int endIndex = 0;
	for(i=0;i<length;i++)
	{
		if(string[i]==':')
		{
			endIndex =  i;
			memcpy(data, &string[startIndex], (size_t)(endIndex-startIndex));
			data[endIndex]='\0';

			if(tLocation==location)
				return 1;

			tLocation++;
			startIndex = i+1;
		}
	}
	endIndex =  i;
	memcpy(data, &string[startIndex], (size_t)endIndex);
	data[endIndex]='\0';
	if(tLocation==location)
		return 1;

	return 0;		
}

void getGTData_vcf (char * string, int locationGT, int locationGP, int locationGL, char * data) // from sample
{
	assert(locationGT!=-1 || (locationGP!=-1 && locationGL!=-1));

	if(locationGT!=-1)
	{
		int ret = getGXData_vcf(string, locationGT, data);
		assert(ret==1);
	}
	else
	{
		int ret = getGXData_vcf(string, locationGL, data);
		assert(ret==1);

		double p00 = 0.0, p01 = 0.0, p11 = 0.0; // likelihoods
		getGPProbs(data, &p00, &p01, &p11, 1); 

		if(p00+p01+p11!=0.0)
		{
			ret = getGXData_vcf(string, locationGP, data);
			assert(ret==1);
		
			reconGT (data);	
		}
		else
			strcpy (data, "./.");		
	}
}

void dataShuffleKnuth(char * data, int startIndex, int endIndex)
{
	if(startIndex == endIndex)
		return;

	int i, index;
	char tmp;

	for (i = endIndex; i > startIndex; i--)
	{
		index = startIndex + (rand() % (i - startIndex + 1));

		tmp = data[index];
		data[index] = data[i];
		data[i] = tmp;
	}
}

int getGTAlleles_vcf (char * string, char * stateVector, int statesTotal, char * sampleData, int * derivedAlleleCount, int * totalAlleleCount, int ploidy)
{	
	assert(statesTotal>=2);
	assert(stateVector!=NULL);

	int i, j=0, index=0, start=0, end=0, len = (int)strlen(string), skipSNP=0;
	
	for(i=0;i<len;i++)
	{	
		if(string[i]>=48 && string[i]<=57)
		{
			if(string[i]!='0' && string[i]!='1')
			{
				fprintf(stderr, "\n ERROR: Invalid character (%c) found!\n\n", string[i]);
				exit(0);
			}

			index = string[i]-48;
	
			assert(index==0 || index==1);

			(*totalAlleleCount)++;

			(*derivedAlleleCount)+=index;

			assert(index<statesTotal);

			sampleData[j++] = string[i];			

			sampleData[j] = '\0';
		}
		else
		{
			if(string[i]=='.')
			{
				sampleData[j++] = 'N';
				sampleData[j] = '\0';
				skipSNP=1;
	
				if(ploidy>1 && len==1)
				{
					assert(!strcmp(string, "."));

					int cnt = ploidy-1;
					while(cnt--!=0)
					{
						sampleData[j++] = 'N';
						sampleData[j] = '\0';
					}
				}
			}

			if(string[i]=='/')
			{
				end++;
			}

			if(string[i]=='|')
			{
				dataShuffleKnuth(sampleData, start, end);
				start = j;
				end = j;
			}			
		}
	}

	dataShuffleKnuth(sampleData, start, end);

	return skipSNP;
}

float * putInSortVector(int * size, float * vector, float value)
{
	(*size)++;
	vector = rsd_realloc(vector, sizeof(float)*((size_t)(*size)));
	vector[(*size)-1] = 0.0f;

	if(*size==1)
	{
		vector[0] = value;
		return vector;
	}

	int i;
	for(i=0;i<*size;i++)
	{
		if(value >= vector[i])
		{
			int pos = i;
			for(i=*size-1;i>pos;i--)
				vector[i] = vector[i-1];

			vector[pos] = value;
			i = *size + 1;
		}		
	}

	return vector;
}

double DIST (double a, double b)
{
	if(a>=b)
		return a-b;
	else
		return b-a;
}

double maxd (double a, double b)
{
	if(a>b)
		return a;
		
	return b;
}

char alleleMask_binary (char c, int * isDerived, int * isValid, FILE * fpOut)
{
	*isDerived = 0;
	*isValid = 0;

	switch(c)
	{
		case '0':
			*isDerived = 0;
			*isValid = 1;
			return c;

		case '1':
			*isDerived = 1;
			*isValid = 1;
			return c;
			
		/*case '2': // This was added for Stefan's datasets
			*isDerived = 1;
			*isValid = 1;
			return '1';

		case '3': // This was added for Stefan's datasets
			*isDerived = 1;
			*isValid = 1;
			return '1';
		*/
		/*case '-':
			*isDerived = 0;
			*isValid = 1;
			return 'N';

		case 'N':
			*isDerived = 0;
			*isValid = 1;
			return 'N';*/

		default:
			fprintf(fpOut, "ERROR: Unrecognized character %c\n\n",c);
			fprintf(stderr, "ERROR: Unrecognized character %c\n\n",c);
			exit(0);

	}	
}

/*char alleleMask_fasta (char c, int * isDerived, int *isValid, FILE * fpOut, char outgroupState)
{
	assert(fpOut!=NULL);

	*isDerived = 0;
	*isValid = 0;

	switch(c)
	{
		case '-':
			*isDerived = 0;
			*isValid = 1;
			return 'N';

		case 'N':
			*isDerived = 0;
			*isValid = 1;
			return 'N';

		case 'n':
			*isDerived = 0;
			*isValid = 1;
			return 'N';

		default:
			if(c==outgroupState)
			{
				*isDerived = 0;
				*isValid = 1;
				return '0';
			}
			else
			{
				*isDerived = 1;
				*isValid = 1;
				return '1';
			}
	}	
}*/

int monomorphic_check (int incomingSiteDerivedAlleleCount, int setSamples, int64_t * cnt, int skipSNP)
{
	if(skipSNP==1) // to avoid double counting
		return 0;

	int check = 1;

	if(incomingSiteDerivedAlleleCount==0 || incomingSiteDerivedAlleleCount==setSamples)
	{
		check = 0;
 		++(*cnt);
	}

	return check;	
}

int strictPolymorphic_check (int incomingSiteDerivedAlleleCount, int incomingSiteTotalAlleleCount, int64_t * cnt, int skipSNP)
{
	if(skipSNP==1) // to avoid double counting
		return 0;

	int check = 1;

	if(incomingSiteDerivedAlleleCount==incomingSiteTotalAlleleCount)
	{
		check = 0;
		++(*cnt);
	}

	return check;	
}

int maf_check (int ac, int at, double maf, int64_t * cnt, int skipSNP)
{
	if(skipSNP==1) // to avoid double counting
		return 0;

	if(ac<=0||at<=0)
		return 0;

	int check = 1; // default: do not discard

	double aaf = ((double)ac)/((double)at);
	double adf = ((double)at-ac)/((double)at);

	if(aaf<maf || adf<maf)
	{
		check = 0;
		++(*cnt);
	}

	return check;
}

void ignoreLineSpaces(FILE *fp, char *ent)
{
	while(*ent==' '|| *ent == 9) // horizontal tab
		*ent = (char)fgetc(fp);  
}

int flagMatch(FILE *fp, char flag[], int flaglength, char tmp)
{
	int counter = 0;
	while(counter < flaglength)
	{
		if(tmp != flag[counter])
		  {
		    break;
		  }
		tmp = (char)fgetc(fp);

		++counter;
	}
	
	return counter;
}

void RSD_printTime (FILE * fp1, FILE * fp2)
{
	clock_gettime(CLOCK_REALTIME, &requestEnd);
	double TotalTime = (requestEnd.tv_sec-requestStart.tv_sec)+ (requestEnd.tv_nsec-requestStart.tv_nsec) / BILLION;


	fprintf(fp1, "\n");
	fprintf(fp1, " Total execution time %.5f seconds\n", TotalTime);

	fprintf(fp2, "\n");
	fprintf(fp2, " Total execution time %.5f seconds\n", TotalTime);

#ifdef _PTIMES
	fprintf(fp1, " Total OoC time %.5f seconds\n", TotalOoCTime);
	fprintf(fp2, " Total OoC time %.5f seconds\n", TotalOoCTime);

	fprintf(fp1, " Total Mu time %.5f seconds\n", TotalMuTime);
	fprintf(fp2, " Total Mu time %.5f seconds\n", TotalMuTime);
#endif
}

void RSD_countMemory (size_t newMemSz)
{
	MemoryFootprint+=newMemSz;
}

inline void * rsd_malloc (size_t size)
{
	RSD_countMemory (size);
	return malloc (size);
}

inline void * rsd_realloc (void * p, size_t size)
{
	RSD_countMemory (size);
	return realloc (p, size);
}

void RSD_printMemory (FILE * fp1, FILE * fp2)
{
	fprintf(fp1, " Total memory footprint %.0f kbytes\n", MemoryFootprint/1024.0);
	fprintf(fp1, "\n");

	fprintf(fp2, " Total memory footprint %.0f kbytes\n", MemoryFootprint/1024.0);
	fprintf(fp2, "\n");
}

void RSD_printSiteReportLegend (FILE * fp, int64_t imputePerSNP, int64_t createPatternPoolMask)
{
	if(fp==NULL)
		return;

	if(imputePerSNP==0 && createPatternPoolMask==0) // M=0
		fprintf(fp, "\n Index: Name | Sites = SNPs + Discarded | Discarded = HeaderCheckFailed + MAFCheckFailed + WithMissing + Monomorphic\n");
	else
	{
		if(imputePerSNP==1) // M=1
			fprintf(fp, "\n Index: Name | Sites = SNPs + Discarded | Discarded = HeaderCheckFailed + MAFCheckFailed + Monomorphic + PotentiallyMonomorphicSites | Imputed\n");
		else // M=2,3
			fprintf(fp, "\n Index: Name | Sites = SNPs + Discarded | Discarded = HeaderCheckFailed + MAFCheckFailed + Monomorphic + PotentiallyMonomorphicSites \n");
	}
	fflush(fp);
}

#ifdef _ZLIB
int gzscanf (gzFile fp, char * string)
{
	assert(string!=NULL);
	char t = (char) gzgetc(fp);

	while(t==' ' || t=='\n' || t==EOF || t==13 || t=='\t')
	{
		if(t==EOF)
			return 0;

		t = (char) gzgetc(fp);
	}

	int i=0;
	string[0]='\0';
	while(t!=' ' && t!='\n' && t!=EOF && t!=13 && t!='\t')
	{
		string[i++]=t;
		//assert(t!=' ' && t!='\n' && t!=EOF && t!=13 && t!='\t');
		t = (char) gzgetc(fp);
	}
	gzungetc(t,fp);
	//assert(t==' ' || t=='\n' || t==EOF || t==13 || t=='\t');

	string[i]='\0';

	return 1;
}
#endif

FILE * skipLine (FILE * fp)
{
	assert(fp!=NULL);
	
	char tchar;
	tchar= (char)fgetc(fp);
	while(tchar!='\n' && tchar!=EOF)
		tchar = (char)fgetc(fp); // skip line

	return fp;
}

int matchChromInList (char * newChromName, char ** chromList, int chromListSize)
{
	assert(newChromName!=NULL);
	int i;
	for(i=0;i<chromListSize;i++)
	{
		if(!strcmp(newChromName, chromList[i]))
			return 1;
	}

	return 0;
}

char ** addChromToList (char * newChromName, char ** chromList, int * chromListSize)
{
	if(!strcmp(newChromName, "."))
		return chromList;

	(*chromListSize)++;

	char ** chromListNew = rsd_realloc(chromList, sizeof(char*)*((unsigned long)(*chromListSize)));
	assert(chromListNew!=NULL);

	chromListNew[(*chromListSize)-1] = (char*)rsd_malloc(sizeof(char)*STRING_SIZE);
	assert(chromListNew[(*chromListSize)-1]!=NULL);

	strncpy(chromListNew[(*chromListSize)-1], newChromName, STRING_SIZE);

	return chromListNew;
}

void VCFFileCheck (void * vRSDDataset, char * fileName, FILE * fpOut) // TODO: Implement this for vcf.gz
{
	assert(vRSDDataset!=NULL);
	RSDDataset_t * RSDDataset = (RSDDataset_t *)vRSDDataset;
	assert(fileName);

	FILE * fp = RSDDataset->inputFilePtr;

	char fileNameNew[STRING_SIZE];
	strncpy(fileNameNew, fileName, STRING_SIZE-1);
	strcat(fileNameNew, ".fxd");

	char tstring[STRING_SIZE];

	// Check reorder requirement based on CHROM

	// Jump to header line
	int rcnt = fscanf(fp, "%s", tstring);
	while(rcnt==1 && strcmp(tstring, "#CHROM"))
		rcnt = fscanf(fp, "%s", tstring);

	// Skip header line
	fp = skipLine(fp);

	int i, chromListSize = 0;
	char ** chromList = NULL;

	int reorderReq = 0;
	
	int doneParsing = 0;
	while(!doneParsing)
	{
		rcnt = fscanf(fp, "%s", tstring);

		if(rcnt!=EOF)
		{
			int chromMatch = matchChromInList (tstring, chromList, chromListSize);
			
			if(chromMatch==0)
				chromList = addChromToList (tstring, chromList, &chromListSize);
			else
			{
				if(strcmp(tstring, chromList[chromListSize-1]))
				{
					if(reorderReq==0)
					{
						fprintf(fpOut, "\nWARNING: Wrong data order (CHROM) in file %s", fileName);
						fflush(fpOut);

						fprintf(stdout, "\nWARNING: Wrong data order (CHROM) in file %s", fileName);
						fflush(stdout);

						reorderReq = 1;
					}						
				}
			}

			fp = skipLine(fp);
		}
		else
			doneParsing = 1;
	}

	// Check reorder requirement based on POS

	double prevPOS = 0.0;
	if(reorderReq==0 || reorderReq==1)
	{
		for(i=0;i<chromListSize;i++)
		{
			fclose(fp);	

			fp = fopen(fileName, "r");
			assert(fp!=NULL);
	
			// Jump to header line
			rcnt = fscanf(fp, "%s", tstring);
			while(rcnt==1 && strcmp(tstring, "#CHROM"))
				rcnt = fscanf(fp, "%s", tstring);

			// Skip header line
			fp = skipLine(fp);

			prevPOS = 0.0;

			doneParsing = 0;
			while(!doneParsing)
			{
				rcnt = fscanf(fp, "%s", tstring);

				if(rcnt!=EOF)
				{
					if(!strcmp(chromList[i], tstring))
					{
						rcnt = fscanf(fp, "%s", tstring); // POS
						assert(rcnt!=-1);

						if(strcmp(tstring, "."))
						{
							double curPOS = (double)atof(tstring);

							if(curPOS<prevPOS)
							{
								if(reorderReq==0 || reorderReq==1)
								{
									fprintf(fpOut, "\nWARNING: Wrong data order (POS) in file %s", fileName);
									fflush(fpOut);

									fprintf(stdout, "\nWARNING: Wrong data order (POS) in file %s", fileName);
									fflush(stdout);

									reorderReq = 2;
								}
							}
							prevPOS = curPOS;
						}							

						fp = skipLine(fp);
					}
				}
				else
					doneParsing = 1;
			}
		}
	}

	if(reorderReq!=0)
	{
		fprintf(fpOut, "\n\n");
		fflush(fpOut);	

		fprintf(stdout, "\n\n");
		fflush(stdout);	
	}

	if(chromList!=NULL)
	{
		for(i=0;i<chromListSize;i++)
		{
			if(chromList[i]!=NULL)
			{	
				free(chromList[i]);
				chromList[i] = NULL;
			}
		}	
		free(chromList);
	}

	assert(fp!=NULL);
	RSDDataset->inputFilePtr = fp;
}

int VCFFileCheckAndReorder (void * vRSDDataset, char * fileName, int overwriteOutput, FILE * fpOut)
{
	assert(vRSDDataset!=NULL);
	RSDDataset_t * RSDDataset = (RSDDataset_t *)vRSDDataset;
	assert(fileName!=NULL);

	FILE * fp = RSDDataset->inputFilePtr;
	FILE * fpNew = NULL;

	char fileNameNew[STRING_SIZE];
	strncpy(fileNameNew, fileName, STRING_SIZE-1);
	strcat(fileNameNew, ".fxd");

	char tstring[STRING_SIZE];

	int snpDataBufSz = STRING_SIZE;
	int snpDataBufInd = -1;
	char * 	snpDataBuf = (char*)rsd_malloc(sizeof(char)*((unsigned long)snpDataBufSz));
	assert(snpDataBuf!=NULL);

	// Check reorder requirement based on CHROM

	// Jump to header line
	int rcnt = fscanf(fp, "%s", tstring);
	while(rcnt==1 && strcmp(tstring, "#CHROM"))
		rcnt = fscanf(fp, "%s", tstring);

	// Skip header line
	fp = skipLine(fp);

	int i, chromListSize = 0;
	char ** chromList = NULL;

	int reorderReq = 0;
	
	int doneParsing = 0;
	while(!doneParsing)
	{
		rcnt = fscanf(fp, "%s", tstring);

		if(rcnt!=EOF)
		{
			int chromMatch = matchChromInList (tstring, chromList, chromListSize);
			
			if(chromMatch==0)
				chromList = addChromToList (tstring, chromList, &chromListSize);
			else
			{
				if(strcmp(tstring, chromList[chromListSize-1]))
				{
					if(reorderReq==0)
					{
						fprintf(fpOut, "\nWARNING: Wrong data order (CHROM) in file %s", fileName);
						fflush(fpOut);

						fprintf(stdout, "\nWARNING: Wrong data order (CHROM) in file %s", fileName);
						fflush(stdout);

						reorderReq = 1;
					}						
				}
			}

			fp = skipLine(fp);
		}
		else
			doneParsing = 1;
	}

	// Check reorder requirement based on POS

	int * chromSNPSize = (int*)rsd_malloc(sizeof(int)*((unsigned long)chromListSize));
	assert(chromSNPSize!=NULL);
	
	for(i=0;i<chromListSize;i++)
		chromSNPSize[i] = 0;
	
	double prevPOS = 0.0;
	if(reorderReq==0 || reorderReq==1)
	{
		for(i=0;i<chromListSize;i++)
		{
			fclose(fp);	

			fp = fopen(fileName, "r");
			assert(fp!=NULL);
	
			// Jump to header line
			rcnt = fscanf(fp, "%s", tstring);
			while(rcnt==1 && strcmp(tstring, "#CHROM"))
				rcnt = fscanf(fp, "%s", tstring);

			// Skip header line
			fp = skipLine(fp);

			prevPOS = 0.0;

			doneParsing = 0;
			while(!doneParsing)
			{
				rcnt = fscanf(fp, "%s", tstring);

				if(rcnt!=EOF)
				{
					if(!strcmp(chromList[i], tstring))
					{
						rcnt = fscanf(fp, "%s", tstring); // POS
						assert(rcnt!=-1);

						if(strcmp(tstring, "."))
						{
							chromSNPSize[i]++;

							double curPOS = (double)atof(tstring);

							if(curPOS<prevPOS)
							{
								if(reorderReq==0 || reorderReq==1)
								{
									fprintf(fpOut, "\nWARNING: Wrong data order (POS) in file %s", fileName);
									fflush(fpOut);

									fprintf(stdout, "\nWARNING: Wrong data order (POS) in file %s", fileName);
									fflush(stdout);

									reorderReq = 2;
								}
							}
							prevPOS = curPOS;
						}							

						fp = skipLine(fp);
					}
				}
				else
					doneParsing = 1;
			}
		}
	}

	if(reorderReq!=0)
	{
		fprintf(fpOut, "\nMESSAGE: Creating reordered file %s", fileNameNew);
		fflush(fpOut);

		fprintf(stdout, "\nMESSAGE: Creating reordered file %s", fileNameNew);
		fflush(stdout);

		fpNew = fopen(fileNameNew, "r");

		if(fpNew!=NULL) // fxd vcf file already exists
		{
			if(overwriteOutput==0)
			{
				fprintf(fpOut, "\nERROR: Reordered file %s exists. Use -f to overwrite it.\n\n", fileNameNew);
				fflush(fpOut);

				fprintf(stderr, "\nERROR: Reordered file %s exists. Use -f to overwrite it.\n\n", fileNameNew);
				exit(0);
			}
			else
			{
				fclose(fpNew);
			}
		}

		fpNew = fopen(fileNameNew, "w");
		assert(fpNew!=NULL);

		fclose(fp);	
		fp = fopen(fileName, "r");
		assert(fp!=NULL);

		// Copy all header lines
		int headerDone = 0;

		while(!headerDone)
		{
			rcnt = fscanf(fp, "%s", tstring); // first string in a line
			assert(rcnt==1);

			fprintf(fpNew, "%s", tstring); // copy string

			if(!strcmp(tstring, "#CHROM"))
				headerDone = 1;
			
			// and rest of line
			tstring[0] = (char) fgetc(fp);
			while(tstring[0]!='\n')
			{
				fprintf(fpNew, "%c", tstring[0]);
				tstring[0] = (char) fgetc(fp);	
			}
			fprintf(fpNew, "\n");			
		}

		// Copy SNP data in right order
		for(i=0;i<chromListSize;i++)
		{
			fprintf(fpOut, "\nMESSAGE: Appending %d SNPs ( %s )", chromSNPSize[i], chromList[i]);
			fflush(fpOut);

			fprintf(stdout, "\nMESSAGE: Appending %d SNPs ( %s )", chromSNPSize[i], chromList[i]);
			fflush(stdout);

			// Reset source-file ptr
			fclose(fp);	
			fp = fopen(fileName, "r");
			assert(fp!=NULL);

			// Jump to header line
			rcnt = fscanf(fp, "%s", tstring);
			while(rcnt==1 && strcmp(tstring, "#CHROM"))
				rcnt = fscanf(fp, "%s", tstring);

			// Skip header line
			fp = skipLine(fp);

			RSDLinkedListNode_t * RSDLinkedList = NULL;

			// Scan file for current chrom
			doneParsing = 0;
			while(!doneParsing)
			{
				rcnt = fscanf(fp, "%s", tstring);

				if(rcnt!=EOF)
				{
					if(!strcmp(chromList[i], tstring))
					{
						snpDataBufInd = 0;
						snpDataBuf[snpDataBufInd]='\0';
				
						strncpy(snpDataBuf, chromList[i], STRING_SIZE);
						snpDataBufInd = (int)strlen(chromList[i]);

						rcnt = fscanf(fp, "%s", tstring); // POS
						assert(rcnt!=-1);
			
						if(strcmp(tstring, "."))
						{
							snpDataBuf[snpDataBufInd++] = '\t';
							snpDataBuf[snpDataBufInd] = '\0'; 

							strcat(snpDataBuf, tstring);
							snpDataBufInd += strlen(tstring); 
							snpDataBuf[snpDataBufInd] = '\0';

							double curPos = (double)atof(tstring); 

							tstring[0] = (char) fgetc(fp);	
							while(tstring[0]!='\n')
							{
								if(snpDataBufInd+1>=snpDataBufSz)
								{
									snpDataBufSz+=STRING_SIZE;
									snpDataBuf = rsd_realloc(snpDataBuf, sizeof(char)*((unsigned long)snpDataBufSz));
									assert(snpDataBuf!=NULL);
								}
								snpDataBuf[snpDataBufInd++] = tstring[0]; 
								tstring[0] = (char) fgetc(fp);	
							}
							snpDataBuf[snpDataBufInd] = '\0'; 

							RSDLinkedListNode_t * RSDLinkedList_tmp = RSDLinkedList_addNode (RSDLinkedList, curPos, snpDataBuf);
							assert(RSDLinkedList_tmp!=NULL);
							RSDLinkedList = NULL;
							RSDLinkedList = RSDLinkedList_tmp;							
						}
						else
							fp = skipLine(fp);

					}
					else
						fp = skipLine(fp);
				}
				else
					doneParsing = 1;
			}

			int listSize = RSDLinkedList_getSize (RSDLinkedList);
			assert(listSize==chromSNPSize[i]);

			if(listSize!=chromSNPSize[i])
				assert(0);

			RSDLinkedList_appendToFile (RSDLinkedList, fpNew);

			RSDLinkedList = RSDLinkedList_free(RSDLinkedList);
			assert(RSDLinkedList==NULL);
		}

		fclose(fpNew);
			
		/*fpNew = fopen(fileNameNew, "r");
		assert(fpNew!=NULL);

		int check = VCFFileCheckAndReorder (fpNew, fileNameNew, overwriteOutput);
		assert(check == VCF_FILE_CHECK_PASS);
		
		if(fpNew!=NULL)
		{
			fclose(fpNew);
			fpNew=NULL;
		}*/


		fprintf(fpOut, "\nMESSAGE: Processing continues using file %s", fileNameNew);
		fflush(fpOut);

		fprintf(stdout, "\nMESSAGE: Processing continues using file %s", fileNameNew);
		fflush(stdout);

		strncpy(fileName, fileNameNew, STRING_SIZE);

		fprintf(fpOut, "\n\n");
		fprintf(stdout, "\n\n");
	}

	if(snpDataBuf!=NULL)
	{
		free(snpDataBuf);
		snpDataBuf = NULL;
	}

	if(chromSNPSize!=NULL)
	{
		free(chromSNPSize);
		chromSNPSize=NULL;
	}

	if(chromList!=NULL)
	{
		for(i=0;i<chromListSize;i++)
		{
			if(chromList[i]!=NULL)
			{	
				free(chromList[i]);
				chromList[i] = NULL;
			}
		}	
		free(chromList);
	}

	assert(fp!=NULL);
	RSDDataset->inputFilePtr = fp;
		
	return VCF_FILE_CHECK_PASS;
}

#ifdef _RSDAI
int split_string (char * src, char * str1, char * str2, char delimiter)
{
	assert(src!=NULL);
	assert(str1!=NULL);
	assert(str2!=NULL);
	
	int i=-1, sz=strlen(src);
	
	for(i=0;i<sz;i++)
	{
		if(src[i]==delimiter)
			break;
	}
	
	if(i>=sz)
		return -1;
	
	memcpy(str1, src, sizeof(char)*i);
//	strncpy(str1, src, i);
	str1[i]='\0';

	memcpy(str2, src+i+1, sizeof(char)*(sz-i-1));
	
//	strncpy(str2, src+i+1, sz-i-1);
	str2[sz-i-1]='\0';
	
	return 1;	
}

void exec_command (char * cmd)
{
	assert(cmd);
	
#ifdef _C1
	int ret = system(cmd);
	assert(ret!=-1);	
#else
	fp = popen(cmd);
	assert(fp!=NULL);

	int ret = pclose(fp);
	assert(ret!=-1);	
#endif	
}

void dir_exists_check (char * path)
{
	assert(path!=NULL);
	
	struct stat st;
	
	if(stat(path,&st) != 0)
	{
		fprintf(stderr, "\nERROR: Directory %s not found!\n\n", path);
		exit(0);
	}
}

void getIndicesFromImageName (char * imgName, int * setIndex, int * gridPointIndex, int * gridPointDataIndex)
{
	assert(imgName!=NULL);
	assert(setIndex!=NULL);
	assert(gridPointIndex!=NULL);
	assert(gridPointDataIndex!=NULL);
	
	char tstring[STRING_SIZE];
	
	strncpy(tstring, imgName, STRING_SIZE-1);
	
	char * istring = strtok(tstring, "_");
	(*setIndex) = (int)atoi(istring);
	
	istring = strtok(NULL, "_");
	(*gridPointIndex) = (int)atoi(istring);	
	
	istring = strtok(NULL, ".");
	(*gridPointDataIndex) = (int)atoi(istring);	
}

int is_valid_NN_architecture (char * arc)
{
	assert(arc!=NULL);
	
	if(!strcmp(arc, ARC_SWEEPNET))
		return 1;
		
	if(!strcmp(arc, ARC_SWEEPNET1D))
		return 1;
		
	if(!strcmp(arc, ARC_SWEEPNETRECOMB))
		return 1;

	return 0;	
}

int numOfClasses_NN_architecture (char * arc)
{
	assert(arc!=NULL);
	
	if(!strcmp(arc, ARC_SWEEPNET))
		return CLA_SWEEPNET;
		
	if(!strcmp(arc, ARC_SWEEPNET1D))
		return CLA_SWEEPNET1D;
		
	if(!strcmp(arc, ARC_SWEEPNETRECOMB))
		return CLA_SWEEPNETRECOMB;

	fprintf(stderr, "\nERROR: Unknown network architecture %s!\n\n", arc); 
	exit(0);
}

int numOfPositiveClasses_NN_architecture (char * arc)
{
	assert(arc!=NULL);
	
	if(!strcmp(arc, ARC_SWEEPNET))
		return PCLA_SWEEPNET;
		
	if(!strcmp(arc, ARC_SWEEPNET1D))
		return PCLA_SWEEPNET1D;
		
	if(!strcmp(arc, ARC_SWEEPNETRECOMB))
		return PCLA_SWEEPNETRECOMB;

	fprintf(stderr, "\nERROR: Unknown network architecture %s!\n\n", arc); 
	exit(0);
}

char * getDataType_string (char * imgFormat, int imgDataType)
{
	assert(imgFormat!=NULL);
	assert(imgDataType>=0 && imgDataType<=3);
	
	if(!strcmp(imgFormat, "bin"))
	{
		if(imgDataType==BIN_DATA_RAW)
			 return "raw SNP data and SNP distances";
			 
		if(imgDataType==BIN_DATA_ALLELE_COUNT)
			 return "derived allele frequencies and SNP distances";
			
		return "unknown data type (binary)";
	}
	else
	{
		if(imgDataType==IMG_DATA_RAW)
			 return "raw SNP data";
			 
		if(imgDataType==IMG_DATA_PAIRWISE_DISTANCE)
			 return "raw SNP data and SNP distances";

		if(imgDataType==IMG_DATA_MUVAR_SCALED)
			 return "raw SNP data scaled based on mu-var";
			 
 		if(imgDataType==IMG_DATA_EXPERIMENTAL)
			 return "undefined data type (PNG, experimental)";
			
		return "unknown data type (PNG)";	
	}
	
	return "unknown data type";
}
#endif

int getStringLengthInt (int prv, int in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%d", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

int getStringLengthUint64 (int prv, uint64_t in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%lu", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

int getStringLengthString (int prv, char * in) 
{
	int sLen = ((int)strlen(in))>prv?(int)strlen(in):prv;
	return sLen;
}

int getStringLengthDouble0 (int prv, double in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%.0f", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

int getStringLengthDouble1 (int prv, double in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%.1f", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

int getStringLengthDouble5 (int prv, double in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%.5f", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

int getStringLengthExp (int prv, double in) 
{
	char tstring[STRING_SIZE];
	sprintf(tstring, "%.3e", in);
	int sLen = ((int)strlen(tstring))>prv?(int)strlen(tstring):prv;
	return sLen;
}

#ifdef _RSDAI
void printRAiSD (FILE * fpOut)
{
	// https://www.developmenttools.com/ascii-art-generator/#p=testall&v=0&f=O8&t=RAiSD-AI
	// Roman
   
const char * raisd = "\n\
<<<==============================================================================================o\n\n\
   ooooooooo.         .o.        o8o   .oooooo..o oooooooooo.                   .o.       ooooo\n\
   `888   `Y88.      .888.       `\"'  d8P'    `Y8 `888'   `Y8b                 .888.      `888'\n\
    888   .d88'     .8\"888.     oooo  Y88bo.       888      888               .8\"888.      888\n\
    888ooo88P'     .8' `888.    `888   `\"Y8888o.   888      888              .8' `888.     888\n\
    888`88b.      .88ooo8888.    888       `\"Y88b  888      888   8888888   .88ooo8888.    888\n\
    888  `88b.   .8'     `888.   888  oo     .d8P  888     d88'            .8'     `888.   888\n\
   o888o  o888o o88o     o8888o o888o 8\"\"88888P'  o888bood8P'             o88o     o8888o o888o\n\n\
o==============================================================================================>>>\n\
"; 

fprintf(fpOut, "%s", raisd);
fflush(fpOut);
}
#else
void printRAiSD (FILE * fpOut)
{

const char * raisd = "\n\
 ooooooooo.         .o.        o8o   .oooooo..o oooooooooo.\n\
 `888   `Y88.      .888.       `\"'  d8P'    `Y8 `888'   `Y8b\n\
  888   .d88'     .8\"888.     oooo  Y88bo.       888      888\n\
  888ooo88P'     .8' `888.    `888   `\"Y8888o.   888      888\n\
  888`88b.      .88ooo8888.    888       `\"Y88b  888      888\n\
  888  `88b.   .8'     `888.   888  oo     .d8P  888     d88'\n\
 o888o  o888o o88o     o8888o o888o 8\"\"88888P'  o888bood8P'\n\
";

fprintf(fpOut, "%s", raisd);
fflush(fpOut);
}
#endif
