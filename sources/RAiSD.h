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

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <inttypes.h>
#include <time.h>
#include <unistd.h>
#include <math.h>
//#include <gsl/gsl_errno.h>
//#include <gsl/gsl_spline.h>
//#include <gsl/gsl_interp.h>
#ifdef _RSDAI
#include <png.h> // sudo apt-get install libpng-dev and -lpng
#include <sys/stat.h>
#endif
#ifdef _ZLIB
#include "zlib.h"
#endif

#define MAJOR_VERSION 4
#define MINOR_VERSION 0
#define RELEASE_MONTH "July"
#define RELEASE_YEAR 2024

/*Testing*/
extern uint64_t selectionTarget;
extern double MuVar_Accum;
extern double MuSfs_Accum;
extern double MuLd_Accum;
extern double Mu_Accum;
extern uint64_t selectionTargetDThreshold;
extern double MuVar_Success;
extern double MuSfs_Success;
extern double MuLd_Success;
extern double Mu_Success;
extern double fpr_loc;
extern int scr_svec_sz;
extern float * scr_svec;
extern double tpr_thres;
extern double tpr_scr;
extern int setIndexValid;
#ifdef _RSDAI
extern double NN_Accum;
extern double NN_Success;
extern double compNN_Accum;
extern double compNN_Success;
#endif
/**/

#ifdef _PTIMES
extern struct timespec requestStartOoC;
extern struct timespec requestEndOoC;
extern double TotalOoCTime;

extern struct timespec requestStartMu;
extern struct timespec requestEndMu;
extern double TotalMuTime;
#endif

#define WIN_MODE_FXD 0 // this is the default one
#define WIN_MODE_OSE 1 // one-sided expansion
#define WIN_MODE_FC 2 // floating-center
#define WIN_MODE_DSR 3 // double-sided reduction

#define STRING_SIZE 8192
#define PATTERNPOOL_SIZE 8 // MBs without the mask (actual memfootprint approx. double)
#define	PATTERNPOOL_SIZE_MASK_FACTOR 2
#define CHUNK_MEMSIZE_AND_INCREMENT 1024 // 1024 sites
#define POSITIONLIST_MEMSIZE_AND_INCREMENT 1024 // positions
#define MULTI_STEP_PARSING 0
#define SINGLE_STEP_PARSING 1 // set this to 0 to deactivate completely
#define DEFAULT_WINDOW_SIZE 50
#define MIN_WINDOW_SIZE 6
#define MIN_NUMBER_OF_SAMPLES 3
#define ALL_SAMPLES_VALID -1 // when -1, all samples are assumed valid and will be processed
#define SAMPLE_IS_VALID 1
#define SAMPLE_IS_NOT_VALID 0
#define MAX_COMMANDLINE_FLAGS 100
#define MAX_SAMPLENAME_CHARACTERS 1000

#define OTHER_FORMAT -1
#define MS_FORMAT 0
#define FASTA_FORMAT 1
#define MACS_FORMAT 2
#define VCF_FORMAT 3
#define SF_FORMAT 4

#define MIN_MU_VAL 0.00000001

#define BILLION 1E9

#define RSDPLOT_BASIC_MU 0
#define	RSDPLOT_MANHATTAN 1
#define RSDPLOT_COMMONOUTLIERS 2

#define LUTMAP_WIDTH		256 // 65536
#define	LUTMAP_GROUPSIZE	8 // 16
#define LUTMAP_INTERVAL 	8 // 4

#define	TREEMAP_REALLOC_INCR	1000
#define	TREEMAP_NODEPOOL_CHUNKSIZE 10000

#define VCF_FILE_CHECK_PASS 1
#define VCF_FILE_CHECK_FAIL 0

#define	L_FLAG_INDEX 2
#define B_FLAG_INDEX 17

#define M_FLAG_INDEX 6
#define Y_FLAG_INDEX 5

#define CO_FLAG_INDEX 22

#ifdef _RSDAI
#define GRID_FLAG_INDEX 21
#define IMG_TARGET_SITE_FLAG_INDEX 31
#define IMG_CLASS_LABEL_FLAG_INDEX 33
#define MDL_PATH_FLAG_INDEX 34
#define CL_TEST_PATH_FLAG_INDEX 35
#define GRD_RNG_FLAG_INDEX 40
#define NN_ARC_FLAG_INDEX 41
#define DATA_TYPE_INDEX 42
#define POSITIVE_CLASS_FLAG_INDEX 43
#define CLASS_PAIRINGS_4 44
#define POSITIVE_CLASS_FLAG_INDEX2 45
#endif

#define FASTA2VCF_CONVERT_n_PROCESS 0
#define FASTA2VCF_CONVERT_n_EXIT 1

#define VCF2MS_CONVERT 1

#define GAP '-'
#define AD 'A'
#define CY 'C'
#define GU 'G'
#define TH 'T'
#define UN 'N'
#define ad 'a'
#define cy 'c'
#define gu 'g'
#define th 't'
#define un 'n'

#define MAJORITY 0
#define PROBABILITY 1

#define SCOREBUFFER_REALLOC_INCR 1024

#define SWEED_CO 0
#define RAiSD_CO 1

#ifdef _RSDAI

#define OP_DEF -1
#define OP_CREATE_IMAGES 0
#define OP_TRAIN_CNN 1
#define OP_TEST_CNN 2
#define OP_USE_CNN 3

#define PIXEL_REORDERING_ENABLED 1
#define PIXEL_REORDERING_DISABLED 0

#define SORT_ROWS 0
#define SORT_COLUMNS 1

#define AI_MODE_TRAIN_NETWORK 1
#define AI_MODE_CLASSIFY_IMAGES 0

#define HAMPEL_FILTER_SIZE 11

#define IMG_DATA_RAW 0
#define IMG_DATA_PAIRWISE_DISTANCE 1
#define IMG_DATA_MUVAR_SCALED 2
#define IMG_DATA_EXPERIMENTAL 3

#define BIN_DATA_RAW 0
#define BIN_DATA_ALLELE_COUNT 1

#define ARC_SWEEPNET "SweepNet"
#define CLA_SWEEPNET 2
#define PCLA_SWEEPNET 1

#define ARC_SWEEPNET1D "FAST-NN"
#define CLA_SWEEPNET1D 2
#define PCLA_SWEEPNET1D 1

#define ARC_SWEEPNETRECOMB "SweepNetRecombination"
#define CLA_SWEEPNETRECOMB 4
#define PCLA_SWEEPNETRECOMB 2

#endif
 // images, training, classification, scan , compositescan

// RAiSD.c
extern struct timespec requestStart;
extern struct timespec requestEnd;

extern double StartTime;
extern double FinishTime;
extern double MemoryFootprint;
extern FILE * RAiSD_Info_FP;
extern FILE * RAiSD_SiteReport_FP;
extern FILE * RAiSD_ReportList_FP;

void 			RSD_header 			(FILE * fpOut);

// RAiSD_Support.c
unsigned long long 	rdtsc				(void);
double 			gettime				(void);
int			snpv_cmp 			(uint64_t * A, uint64_t * B, int size);
int			snpv_cmp_cross_masks		(uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size);
int			isnpv_cmp_cross_masks		(uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size);
int			isnpv_cmp 			(uint64_t * A, uint64_t * B, int size, int numberOfSamples);
int			isnpv_cmp_with_mask		(uint64_t * A, uint64_t * B, uint64_t * mA, uint64_t * mB, int size, int numberOfSamples);
int			getGXLocation_vcf 		(char * string, char * GX);
int 			getGXData_vcf 			(char * string, int location, char * data);
void			getGTData_vcf 			(char * string, int locationGT, int locationGP, int locationGL, char * data);
int			getGTAlleles_vcf		(char * string, char * stateVector, int statesTotal, char * sampleData, int * derivedAlleleCount, int * totalAlleleCount, int ploidy);
int			rsd_popcnt_u64			(uint64_t input);
double 			DIST 				(double a, double b);
float * 		putInSortVector			(int * size, float * vector, float value);
char 			alleleMask_binary 		(char c, int * isDerived, int *isValid, FILE * fpOut);
char 			alleleMask_fasta 		(char c, int * isDerived, int *isValid, FILE * fpOut, char outgroupState);
int 			monomorphic_check 		(int incomingSiteDerivedAlleleCount, int setSamples, int64_t * cnt, int skipSNP);
int 			maf_check 			(int ac, int at, double maf, int64_t * cnt, int skipSNP);
int 			strictPolymorphic_check 	(int incomingSiteDerivedAlleleCount, int incomingSiteTotalAlleleCount, int64_t * cnt, int skipSNP);
void 			dataShuffleKnuth		(char * data, int startIndex, int endIndex);
extern void		ignoreLineSpaces		(FILE * fp, char * ent);
extern int 		flagMatch			(FILE * fp, char flag[], int flaglength, char tmp);
extern void 		RSD_printTime 			(FILE * fp1, FILE * fp2);
extern void 		RSD_printMemory 		(FILE * fp1, FILE * fp2);
extern void 		RSD_countMemory 		(size_t newMemSz);
int 			diploidyCheck			(char * data);
void 			getGPProbs 			(char * data, double *p00, double *p01, double * p11, int isLik);
void 			reconGT 			(char * data);
void 			RSD_printSiteReportLegend 	(FILE * fp, int64_t imputePerSNP, int64_t createPatternPoolMask);
extern void *		rsd_malloc			(size_t size);
extern void *		rsd_realloc			(void * p, size_t size);
void 			VCFFileCheck 			(void * vRSDDataset, char * fileName, FILE * fpOut);
int 			VCFFileCheckAndReorder		(void * vRSDDataset, char * fileName, int overwriteOutput, FILE * fpOut);
void 			printRAiSD 			(FILE * fpOut);
FILE * 			skipLine 			(FILE * fp);
void 			get_print_slen 			(int * slen, void * input, int mode);
int 			getStringLengthInt 		(int prv, int in);
int 			getStringLengthUint64 		(int prv, uint64_t in);
int 			getStringLengthString 		(int prv, char * in);  
int 			getStringLengthDouble0 		(int prv, double in);
int 			getStringLengthDouble1 		(int prv, double in); 
int 			getStringLengthDouble5 		(int prv, double in); 
int 			getStringLengthExp 		(int prv, double in);
double 			maxd 				(double a, double b); 

#ifdef _RSDAI
int 			split_string 			(char * src, char * str1, char * str2, char delimiter);
void 			exec_command 			(char * cmd);
void 			dir_exists_check 		(char * path);
void			getIndicesFromImageName		(char * imgName, int * setIndex, int * gridPointIndex, int * gridPointDataIndex);
int 			numOfClasses_NN_architecture		(char * arc);
int 			numOfPositiveClasses_NN_architecture 	(char * arc);
int 			is_valid_NN_architecture 		(char * arc);
char * 			getDataType_string 		(char * imgFormat, int imgDataType);
#endif

#ifndef _INTRINSIC_POPCOUNT
extern char	 	POPCNT_U16_LUT [0x1u << 16];
int 			popcount_u32_iterative	(unsigned int n);
void 			popcount_u64_init 	(void);
#endif

#ifdef _ZLIB
int 			gzscanf 		(gzFile fp, char * string);
#endif

// RAiSD_LinkedList.c
typedef struct RSDLinkedListNode
{
	struct 	RSDLinkedListNode * prv;
	struct 	RSDLinkedListNode * nxt;
	double 	snpPosition;
	char * 	snpData;
} RSDLinkedListNode_t;

RSDLinkedListNode_t * 	RSDLinkedList_new 		(double pos, char * snp);
RSDLinkedListNode_t * 	RSDLinkedList_free		(RSDLinkedListNode_t * listHead);
RSDLinkedListNode_t * 	RSDLinkedList_addNode 		(RSDLinkedListNode_t * listHead, double pos, char * snp);
int 			RSDLinkedList_getSize 		(RSDLinkedListNode_t * listHead);
void 			RSDLinkedList_appendToFile 	(RSDLinkedListNode_t * listHead, FILE * fp);

// RAiSD_CommandLine.c
typedef struct
{	// -a is also reserved for the rand gen's seed
	char 		runName[STRING_SIZE]; // Flag: N
	char 		inputFileName[STRING_SIZE]; // Flag: I
	uint64_t	regionLength; // Flag: L for ms, Flag: B for vcf
	uint64_t	regionSNPs; // Flag: B
	int		overwriteOutput; // Flag: f
	int		splitOutput; // Flag: s 
	int		setSeparator; // Flag: t
	int		printSampleList; // Flag: p
	char 		sampleFileName[STRING_SIZE]; // Flag: S
	double		maf; // Flag: m
	int64_t		mbs; // Flag: b
	int64_t		imputePerSNP; //Flag: i
	int64_t		createPatternPoolMask; //Flag: M
	int64_t		patternPoolMaskMode; //Flag: M
	int64_t		displayProgress; // Flag: O
	int64_t		fullReport; // Flag: R
	int64_t		createPlot; // Flag: P
	char 		manhattanThreshold[STRING_SIZE]; // Flag: P
	int64_t		createMPlot; // Flag: A
	double		muThreshold; // Flag: H
	int64_t		ploidy; // Flag: y
	int64_t		displayDiscardedReport; // Flag: D
	int64_t		windowSize; // Flag: w
	int64_t		sfsSlack; // Flag: c
	char		excludeRegionsFile[STRING_SIZE]; // Flag: X
	int64_t		orderVCF; // Flag: o
	char		outgroupName[STRING_SIZE]; // Flag: C
	char		outgroupName2[STRING_SIZE]; // Flag: C2
	char		chromNameVCF[STRING_SIZE]; // Flag: H
	int64_t		fasta2vcfMode; // Flag: E
	int64_t		vcf2msExtra; // Flag: Q
	int64_t		vcf2msMemsize; // Flag: Q
	int64_t		gridSize; // Flag: G
	int64_t		createCOPlot; // Flag: CO
	char 		reportFilenameSweeD[STRING_SIZE]; // Flag: CO
	int		positionIndexSweeD; // Flag: CO
	int		scoreIndexSweeD; // Flag: CO
	char 		reportFilenameRAiSD[STRING_SIZE]; // Flag: CO
	int		positionIndexRAiSD; // Flag: CO
	int		scoreIndexRAiSD; // Flag: CO
	char		commonOutliersThreshold[STRING_SIZE]; // Flag: COT
	double		commonOutliersMaxDistance; // Flag: COD
	float 		muVarExp; // Flag: VAREXP
	float		muSfsExp; // Flag: SFSEXP
	float		muLdExp; // Flag: LDEXP
	
	// Evaluation 
	uint64_t 	selectionTarget;
	uint64_t 	selectionTargetDThreshold;	
	double 		fprLoc;	
	
	double		tprThresMuVar;
	double		tprThresMuSfs;
	double		tprThresMuLd;
	double 		tprThresMu;

#ifdef _RSDAI
	// RAiSD-AI
	int		opCode; // IMG, TST, SCN
	int		enTF; // Flag: TF
	int		threads; // Flag: thr
	int		useGPU; // Flag: gpu
	char		networkArchitecture[STRING_SIZE]; // Flag: arc
	
	// IMG
	uint64_t	imagesPerSimulation;
	uint64_t	imageTargetSite; // this refers to the first generated image only.
	int		imageWindowStep; // applied as a SNP-based sliding window left and right of the ics.
	int		imageReorderOpt;
	char		imageClassLabel[STRING_SIZE];
	int		imagePositionCenteredEn;
	int		forceRemove;
	char		modelPath[STRING_SIZE];
	int		numberOfClasses;
	char **		classLabelList;
	char **		classPathList;
	unsigned int	imageHeight;
	unsigned int	imageWidth;
	int		epochs;
	int		enBinFormat;
	int		trnObjDetection; // 0: classification, 1: detection
	uint64_t	gridRngLeBor;
	uint64_t	gridRngRiBor;
	int		imgDataType;
	int		numOfPositiveClasses;
	int * 		positiveClassIndex;
	int		userWindowSize; // flag set if user provides the window size
	
	// Evaluation
	double		tprThresNnPositiveClass0;
	double		tprThresNnPositiveClass1;
	
	// Experimental
	int		fullFrame;
	int		gridPointReductionMax;	 	
#endif

} RSDCommandLine_t;

void 			RSDHelp 				(FILE * fp);
void 			RSDVersions				(FILE * fp);
RSDCommandLine_t * 	RSDCommandLine_new			(void);
void 			RSDCommandLine_free			(RSDCommandLine_t * RSDCommandLine);
void 			RSDCommandLine_init			(RSDCommandLine_t * RSDCommandLine);
void 			RSDCommandLine_load			(RSDCommandLine_t * RSDCommandLine, int argc, char ** argv);
void 			RSDCommandLine_print			(int argc, char ** argv, FILE * fpOut);
void			RSDCommandLine_printInfo		(RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 			RSDCommandLine_printWarnings 		(RSDCommandLine_t * RSDCommandLine, int argc, char ** argv, void * RSDDataset, FILE * fpOut);
void			RSDCommandLine_printExponents 		(RSDCommandLine_t * RSDCommandLine, FILE * fpOut);

// RAiSD_Chunk.c
typedef struct
{
	int64_t		chunkID; // index
	int64_t		chunkMemSize; // preallocated
	int64_t		chunkSize; // number of snps

	fpos_t		posPosition;
	fpos_t * 	seqPosition;

	double * 	sitePosition;
	int * 		derivedAlleleCount;
	int * 		patternID;

	float *		chunkData; // type casting for alleleCount and patternID

	int		derAll1CntTotal;
	int		derAllNCntTotal; 

} RSDChunk_t;

RSDChunk_t *	RSDChunk_new 			(void);
void 		RSDChunk_free			(RSDChunk_t * ch);
void 		RSDChunk_init			(RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, int64_t numberOfSamples);
void		RSDChunk_reset			(RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine);

// RAiSD_HashMap.c
typedef struct
{
	int64_t		addressListSize; // = sampleSize for convenience
	uint64_t **	addressList;

	uint64_t	addressListEntryMaxSize;
	uint64_t *	addressListEntrySize;
	int64_t		addressListEntryFull;

	int64_t		mainKey;
	int64_t		secondaryKey;

	uint64_t *	mainAddress;
	uint64_t *	secondaryAddress;

	uint64_t *	poolDataFractions;	

} RSDHashMap_t;

RSDHashMap_t * 	RSDHashMap_new				(void);
void		RSDHashMap_init 			(RSDHashMap_t * RSDHashMap, int64_t numberOfSamples, int maxSize, int patternSize);
void 		RSDHashMap_free 			(RSDHashMap_t * hm);
void		RSDHashMap_setMainKey 			(RSDHashMap_t * RSDHashMap, int64_t mainKey);
void		RSDHashMap_setSecondaryKey 		(RSDHashMap_t * RSDHashMap, int64_t secondaryKey);
int 		RSDHashMap_scanPatternPoolFractions 	(RSDHashMap_t * RSDHashMap, uint64_t * incomingSiteCompact, int patternSize, int numberOfSamples, int * match);

// RAiSD_LutMap.c
typedef struct
{
	int64_t		lutMapSize;
	uint8_t *	lutMapMem;
	uint8_t ** 	lutMap;	
	uint8_t *	lutMapMemC;
	uint8_t **	lutMapC;

} RSDLutMap_t;

RSDLutMap_t *	RSDLutMap_new		(void);
void		RSDLutMap_init		(RSDLutMap_t * lm, int64_t numberOfSamples);
void 		RSDLutMap_free 		(RSDLutMap_t * lm);
void 		RSDLutMap_reset		(RSDLutMap_t * lm);
int		RSDLutMap_scan		(RSDLutMap_t * lm, uint64_t * query);
int		RSDLutMap_scanC		(RSDLutMap_t * lm, uint64_t * query, int64_t patternSize, int64_t numberOfSamples);
void 		RSDLutMap_update	(RSDLutMap_t * lm, uint64_t * query);

// RAiSD_TreeMap.c
typedef struct RSDTreeNode_t
{
	struct RSDTreeNode_t * 	childNode[2];
#ifndef _TM_PATTERN_ARRAY
	int64_t			patternID; 		
#endif
} RSDTreeNode_t;

typedef struct 
{
	int64_t nodeMatrixSizeX;
	int64_t nodeMatrixSizeY;

	int64_t	nextNodeDimX;
	int64_t	nextNodeDimY;
	
	RSDTreeNode_t ** nodeMatrix;

} RSDTreeNodePool_t;

typedef struct
{
	int64_t			totalPatterns;
	int64_t			totalNodes;
	size_t			totalMemory;

	RSDTreeNode_t *		rootNode[2];

	// _TM_NODE_POOL
	RSDTreeNodePool_t *	nodePool[2];

	// _TM_PATTERN_ARRAY
	int64_t			maxPatterns; // Thats how many patterns the allocated mem can accommodate.
	RSDTreeNode_t ** 	patternID; // This ptr index in this vec is the patternID.
	

} RSDTreeMap_t;

RSDTreeMap_t * 	RSDTreeMap_new 			(void);
void 		RSDTreeMap_free			(RSDTreeMap_t * RSDTreeMap);
int64_t		RSDTreeMap_matchSNP 		(RSDTreeMap_t * RSDTreeMap, void * RSDPatternPool_g, int64_t numberOfSamples);
int64_t		RSDTreeMap_matchSNPC 		(RSDTreeMap_t * RSDTreeMap, void * RSDPatternPool_g, int64_t numberOfSamples);
int64_t		RSDTreeMap_updateTree 		(RSDTreeMap_t * RSDTreeMap, void * RSDPatternPool_g, int64_t numberOfSamples);
int64_t		RSDTreeMap_updateTreeInit 	(RSDTreeMap_t * RSDTreeMap, void * RSDPatternPool_g, int64_t numberOfSamples, uint64_t * pattern);

// RAiSD_PatternPool.c
typedef struct
{
	int 		memorySize; // MBs
	
	int 		maxSize; // maximum number of patterns that can be stored

	int 		patternSize; // 64-bit words

	int 		dataSize; // number of patterns stored in the pool

	char * 		incomingSite;
	int		incomingSiteDerivedAlleleCount;
	int		incomingSiteTotalAlleleCount;
	uint64_t * 	incomingSiteCompact;
	uint64_t *	incomingSiteCompactMask;
	int64_t		incomingSiteCompactWithMissing;
	double		incomingSitePosition;

	uint64_t	createPatternPoolMask; // 0 if no mask used, 1 if mask used
	uint64_t	patternPoolMaskMode; // 0 for ignoring allele pairs with N, 1 for treating N as extra state
	uint64_t * 	poolData; // pattern data
	uint64_t *	poolDataMask; // pattern data mask (for handling N)
	int *		poolDataAlleleCount; // number of derived alleles per pattern
	int *		poolDataPatternCount; // number of specific pattern occurences
	int *		poolDataWithMissing; // yes/no if missing/not per pattern
	int *		poolDataMaskCount; // popcnt the mask only
	int *		poolDataAppliedMaskCount; // popcnt data&mask

	uint64_t * 	exchangeBuffer; // used to exchange patterns between location in the pool

	RSDHashMap_t *	hashMap;
	RSDLutMap_t * 	lutMap;
	RSDTreeMap_t * 	treeMap;

} RSDPatternPool_t;

RSDPatternPool_t * 	RSDPatternPool_new			(RSDCommandLine_t * RSDCommandLine);
void 			RSDPatternPool_free			(RSDPatternPool_t * pp);
void 			RSDPatternPool_init 			(RSDPatternPool_t * RSDPatternPool, RSDCommandLine_t * RSDCommandLine, int64_t numberOfSamples);
void 			RSDPatternPool_print			(RSDPatternPool_t * RSDPatternPool, FILE * fpOut);
void 			RSDPatternPool_reset 			(RSDPatternPool_t * RSDPatternPool, int64_t numberOfSamples, int64_t setSamples, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine);
int			RSDPatternPool_pushSNP			(RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, int64_t numberOfSamples, RSDCommandLine_t * RSDCommandLine, void * RSDVcf2ms);
void			RSDPatternPool_resize 			(RSDPatternPool_t * RSDPatternPool, int64_t setSamples, FILE * fpOut);
void 			RSDPatternPool_exchangePatterns 	(RSDPatternPool_t * RSDPatternPool, int pID_a, int pID_b);
void 			RSDPatternPool_exchangePatternsFractions(RSDPatternPool_t * RSDPatternPool, int pID_a, int pID_b);
int			RSDPatternPool_imputeIncomingSite 	(RSDPatternPool_t * RSDPatternPool, int64_t setSamples);
void			RSDPatternPool_assessMissing 		(RSDPatternPool_t * RSDPatternPool, int64_t numberOfSamples);

// RAiSD_Dataset.c
typedef struct
{
	FILE * 		inputFilePtr;
#ifdef _ZLIB
	gzFile 		inputFilePtrGZ;
#endif
	char 		inputFileFormat[STRING_SIZE];
	char		setID[STRING_SIZE]; // for vcf this is the chrom number
	int 		inputFileIsMBS;
	int 		numberOfSamples; // -1 when unitialized

	fpos_t 		setPosition; // set position, first "/" in ms or first line with dif chrom number in VCF
#ifdef _ZLIB
	z_off_t		setPositionGZ;
#endif
	int64_t		setParsingMode;
	
	int64_t		setSamples; // number of samples in the set - differs from numberOfSamples in vcf because of ploidy
	int64_t 	setSize; // number of segsites, provided by the set header in ms, -1 for vcf - this can also include non-polymorphic sites
	int64_t		setSNPs; // number of non-discarded sites
	int64_t		setProgress; // number of loaded segsites
	uint64_t	preLoadedsetSNPs;

	uint64_t 	setRegionLength;

	FILE *		sampleFilePtr;
	char **		sampleValidList; // list of names of valid samples
	int		sampleValidListSize; // number of names in the sampleValidList
	int		numberOfSamplesVCF; // this is the full number of samples in the vcf file
	int *		sampleValid; // this must be of size numberOfSamples with sampleValidListSize number of 1s or less, indicates which of the dataset samples are valid

	int64_t		setSitesDiscarded;
	int64_t		setSitesDiscardedHeaderCheckFailed;
	int64_t		setSitesDiscardedWithMissing;
	int64_t		setSitesDiscardedMafCheckFailed;
	int64_t		setSitesDiscardedStrictPolymorphicCheckFailed;
	int64_t		setSitesDiscardedMonomorphic;
	int64_t		setSitesImputedTotal;
	
	double		muVarDenom;

	char *		outgroupSequence;
	char		outgroupName[STRING_SIZE];

	char *		outgroupSequence2;
	char		outgroupName2[STRING_SIZE];

} RSDDataset_t;

RSDDataset_t * 	RSDDataset_new				(void);
void 		RSDDataset_free				(RSDDataset_t * RSDDataset);
void 		RSDDataset_init				(RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDDataset_print 			(RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDDataset_setPosition 			(RSDDataset_t * RSDDataset, int * setIndex);

void 		RSDDataset_initParser			(RSDDataset_t * RSDDataset, FILE * fpOut, RSDCommandLine_t * RSDCommandLine, int isGZ);
extern char	(*RSDDataset_goToNextSet) 		(RSDDataset_t * RSDDataset);
extern int	(*RSDDataset_getNumberOfSamples) 	(RSDDataset_t * RSDDataset);
extern int 	(*RSDDataset_getValidSampleList) 	(RSDDataset_t * RSDDataset);
extern int 	(*RSDDataset_getFirstSNP) 		(RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, uint64_t length, double maf, FILE * fpOut);
extern int	(*RSDDataset_getNextSNP) 		(RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, uint64_t length, double maf, FILE * fpOut);
int 		RSDDataset_getNextSNP_ms 		(RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, uint64_t length, double maf, FILE * fpOut);
int 		RSDDataset_getNextSNP_vcf 		(RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, uint64_t length, double maf, FILE * fpOut);
void		RSDDataset_getSetRegionLength_ms	(RSDDataset_t * RSDDataset, uint64_t length);
void		RSDDataset_getSetRegionLength_vcf	(RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDDataset_printSiteReport 		(RSDDataset_t * RSDDataset, FILE * fp, int setIndex, int64_t imputePerSNP, int64_t createPatternPoolMask);
void 		RSDDataset_resetSiteCounters 		(RSDDataset_t * RSDDataset);
void		RSDDataset_calcMuVarDenom		(RSDDataset_t * RSDDataset);
void 		RSDDataset_writeOutput 			(RSDDataset_t * RSDDataset, int setIndex, FILE * fpOut);
#ifdef _ZLIB
void		RSDDataset_getSetRegionLength_vcf_gz	(RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
int 		RSDDataset_getNextSNP_vcf_gz 		(RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, uint64_t length, double maf, FILE * fpOut);
#endif

// RAiSD_CommonOutliers.c
typedef struct
{
	char 		reportFilenameSweeD[STRING_SIZE];
	int		positionIndexSweeD;
	int		scoreIndexSweeD;

	int64_t		reportSizeSweeD;
	double	*	positionSweeD;
	double	* 	scoreSweeD;

	int64_t		coPointSizeSweeD;
	double	*	coPointPositionSweeD;
	double	* 	coPointScoreSweeD;

	char 		reportFilenameRAiSD[STRING_SIZE];
	int		positionIndexRAiSD;
	int		scoreIndexRAiSD;

	int64_t		reportSizeRAiSD;
	double	*	positionRAiSD;
	double	* 	scoreRAiSD;

	int64_t		coPointSizeRAiSD;
	double	*	coPointPositionRAiSD;
	double	* 	coPointScoreRAiSD;

	char 		report1Filename[STRING_SIZE];
	char 		report2Filename[STRING_SIZE];
	char 		common1Filename[STRING_SIZE];
	char 		common2Filename[STRING_SIZE];

} RSDCommonOutliers_t;

RSDCommonOutliers_t * 	RSDCommonOutliers_new 		(void);
void 			RSDCommonOutliers_free 		(RSDCommonOutliers_t * RSDCommonOutliers);
void 			RSDCommonOutliers_init 		(RSDCommonOutliers_t * RSDCommonOutliers, RSDCommandLine_t * RSDCommandLine);
void 			RSDCommonOutliers_process 	(RSDCommonOutliers_t * RSDCommonOutliers, RSDCommandLine_t * RSDCommandLine);

// RAiSD_MuStatistic.c
typedef struct
{
	char 		reportName [STRING_SIZE];
	FILE *		reportFP;
	char		reportFPFileName[STRING_SIZE];

	int64_t		windowSize; // number of SNPs in each window

	int *		pCntVec;    // temp array used to count pattern occurences, contains (sequentially and at a stride): pattern count left, pattern count right, pattern count exclusive left, pattern count exclusive right
	
	float 		muVarMax; 
	float 		muSfsMax; 
	float 		muLdMax; 
	float 		muMax;

	double 		muVarMaxLoc;
	double 		muSfsMaxLoc;
	double		muLdMaxLoc; 
	double 		muMaxLoc;

#ifdef _MUMEM
	int64_t		muReportBufferSize;
	float * 	muReportBuffer;
#endif

	int64_t		exclTableSize;
	char **		exclTableChromName;
	int64_t *	exclTableRegionStart;
	int64_t *	exclTableRegionStop;

	int64_t		excludeRegionsTotal;
	int64_t	*	excludeRegionStart;
	int64_t	*	excludeRegionStop;

	int64_t		bufferMemMaxSize;
	double *	buffer0Data; // windowCenter
	double *	buffer1Data; // windowStart	
	double *	buffer2Data; // windowEnd
	double *	buffer3Data; // muVAR
	double *	buffer4Data; // muSFS
	double *	buffer5Data; // muLD
	double *	buffer6Data; // mu
#ifdef _RSDAI
	double *	buffer7Data; // nn
	double *	buffer8Data; // pow(muVar, nn)
	double *	buffer9Data; // second binary classification, SweepNetRecombination
	double *	buffer10Data; // second binary classification, SweepNetRecombination
#endif	
	int64_t		currentScoreIndex;
	
	int		currentGridPointSize;

} RSDMuStat_t;

RSDMuStat_t * 	RSDMuStat_new 			(void);
void 		RSDMuStat_free 			(RSDMuStat_t * mu);
void 		RSDMuStat_init 			(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine);
void 		RSDMuStat_resetScores 		(RSDMuStat_t * RSDMuStat);
void 		RSDMuStat_setReportName 	(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDMuStat_setReportNamePerSet 	(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, RSDDataset_t * RSDDataset, RSDCommonOutliers_t * RSDCommonOutliers);
extern void	(*RSDMuStat_scanChunk) 		(RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDMuStat_scanChunkBinary	(RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDMuStat_scanChunkWithMask	(RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
//extern float   	getPatternCount			(RSDPatternPool_t * RSDPatternPool, int * pCntVec, int offset, int * patternID, int p0, int p1, int p2, int p3, int * pcntl, int * pcntr, int * pcntexll, int * pcntexlr);
extern float 	getPatternCounts (int winMode, RSDMuStat_t * RSDMuStat, int sizeL, int sizeR, int * patternID, int p0, int p1, int p2, int p3, int * pcntl, int * pcntr, int * pcntexll, int * pcntexlr);
void		RSDMuStat_loadExcludeTable 	(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine);
void		RSDMuStat_excludeRegion 	(RSDMuStat_t * RSDMuStat, RSDDataset_t * RSDDataset);
extern void 	(*RSDMuStat_storeOutput) 	(RSDMuStat_t * RSDMuStat, double windowCenter, double windowStart, double windowEnd, double muVar, double muSfs, double muLd, double mu);
void 		RSDMuStat_output2FileSimple 	(RSDMuStat_t * RSDMuStat, double windowCenter, double windowStart, double windowEnd, double muVar, double muSfs, double muLd, double mu);
void 		RSDMuStat_output2FileFull 	(RSDMuStat_t * RSDMuStat, double windowCenter, double windowStart, double windowEnd, double muVar, double muSfs, double muLd, double mu);
void 		RSDMuStat_writeBuffer2File 	(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine);
#ifdef _RSDAI
void		RSDMuStat_output2BufferFullExtended (RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, double windowCenter, double windowStart, double windowEnd, double muVar, double muSfs, double muLd, double mu, double label1, double label2, double label3, double label4, int classes);
void 		RSDMuStat_writeBuffer2FileNoInterp (RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine);
void 		RSDMuStat_removeOutliers 	(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine);
#endif
void 		RSDMuStat_storeOutputConfigure 	(RSDCommandLine_t * RSDCommandLine);
float 		RSDMuStat_calcMuVar 		(RSDMuStat_t * RSDMuStat, RSDDataset_t * RSDDataset, RSDChunk_t * RSDChunk, int snpf, int snpl);
float 		RSDMuStat_calcMuSfsFull 	(RSDMuStat_t * RSDMuStat, RSDDataset_t * RSDDataset, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine, int snpf, int snpl);
float 		RSDMuStat_calcMuLd 		(RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, int winlsnpf, int winlsnpl, int winrsnpf, int winrsnpl);
float 		RSDMuStat_calcMu 		(RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, float muVar, float muSfs, float muLd, double windowCenter, int isValid, FILE * fpOut);
int 		RSDMuStat_placeWindow 		(RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, int index, int * snpf, int * snpl, int * winlsnpf, int * winlsnpl, int * winrsnpf, int * winrsnpl,  double * windowCenter, double * windowStart, double * windowEnd, int mode);
// RAiSD_Plot.c
void 		RSDPlot_printRscriptVersion 	(RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
int 		RSDPlot_checkRscript 		(void);
void 		RSDPlot_createRscriptName 	(RSDCommandLine_t * RSDCommandLine, char * scriptName);
void 		RSDPlot_generateRscript 	(RSDCommandLine_t * RSDCommandLine, int mode);
void 		RSDPlot_removeRscript 		(RSDCommandLine_t * RSDCommandLine,int mode);
void 		RSDPlot_createPlot 		(RSDCommandLine_t * RSDCommandLine, RSDDataset_t * RSDDataset, RSDMuStat_t * RSDMuStat, RSDCommonOutliers_t * RSDCommonOutliers, int mode, void * nn);
void 		RSDPlot_createReportListName 	(RSDCommandLine_t * RSDCommandLine, char * reportListName);
void 		RSDMuStat_writeOutput 		(RSDMuStat_t * RSDMuStat, RSDDataset_t * RSDDataset, int setIndex, FILE * fpOut); // print max scores to stdout and info file

// RAiSD_Fasta2Vcf.c
typedef struct
{
	int		statesMax;
	int		statesTotal;
	char *		statesChar;
	int *		statesCount;

	int 		imputeStatesMax;
	int 		imputeStatesTotal;
	char * 		imputeStatesChar;
	double * 	imputeStatesProb;

} RSDFastaStates_t;

void RSDDataset_convertFasta2VCF (RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);

//RAiSD_Vcf2ms.c
typedef struct
{
	FILE * 		outputFilePtr;
	int64_t 	memSz;
	int64_t 	segsites;
	double * 	positionList;
	int64_t 	samples;
	char ** 	data;
	int64_t		status; // if 0, print ms header and make 1

} RSDVcf2ms_t;

RSDVcf2ms_t * 	RSDVcf2ms_new				(RSDCommandLine_t * RSDCommandLine);
void 		RSDVcf2ms_free				(RSDVcf2ms_t * RSDVcf2ms, RSDCommandLine_t * RSDCommandLine);
void 		RSDVcf2ms_appendSNP 			(RSDVcf2ms_t * RSDVcf2ms, RSDCommandLine_t * RSDCommandLine, RSDPatternPool_t * RSDPatternPool, int64_t numberOfSamples);
void 		RSDVcf2ms_printHeader 			(RSDVcf2ms_t * RSDVcf2ms);
void 		RSDVcf2ms_printSegsitesAndPositions 	(RSDVcf2ms_t * RSDVcf2ms);
void 		RSDVcf2ms_printSNPData 			(RSDVcf2ms_t * RSDVcf2ms);
void		RSDVcf2ms_reset				(RSDVcf2ms_t * RSDVcf2ms);

// RAiSD_Eval.c
typedef struct
{
	uint64_t 	selectionTarget;
	double 		muVarAccum;
	double 		muSfsAccum;
	double 		muLdAccum;
	double 		muAccum;
	double		nnPositiveClass0Accum;
	double		nnPositiveClass1Accum;
	

	uint64_t 	selectionTargetDThreshold;
	double 		muVarSuccess;
	double		muSfsSuccess;
	double 		muLdSuccess;
	double 		muSuccess;
	double		nnPositiveClass0Success;
	double		nnPositiveClass1Success;
	
	double 		fprLoc;
	int 		muVarSortVecSz;
	int 		muSfsSortVecSz;
	int 		muLdSortVecSz;	
	int 		muSortVecSz;
	int 		nnPositiveClass0SortVecSz;
	int 		nnPositiveClass1SortVecSz;	
	float *		muVarSortVec;
	float * 	muSfsSortVec;
	float * 	muLdSortVec;	
	float * 	muSortVec;
	float * 	nnPositiveClass0SortVec;
	float * 	nnPositiveClass1SortVec;
	
	double		tprThresMuVar;
	double		tprThresMuSfs;
	double		tprThresMuLd;
	double 		tprThresMu;
	double 		tprThresNnPositiveClass0;
	double 		tprThresNnPositiveClass1;
	double		tprScrMuVar;
	double		tprScrMuSfs;
	double		tprScrMuLd;
	double 		tprScrMu;
	double 		tprScrNnPositiveClass0;
	double 		tprScrNnPositiveClass1;

} RSDEval_t;

RSDEval_t * 	RSDEval_new					(RSDCommandLine_t * RSDCommandLine);
void		RSDEval_init					(RSDEval_t * RSDEval, RSDCommandLine_t * RSDCommandLine);
void 		RSDEval_free 					(RSDEval_t * RSDEval);
void 		RSDEval_calculateDetectionMetricsConfigure 	(RSDCommandLine_t * RSDCommandLine);
extern void 	(*RSDEval_calculateDetectionMetrics)		(RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults);
void 		RSDEval_calculateDetectionMetricsSlidingWindow	(RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults);
void 		RSDEval_calculateDetectionMetricsGrid		(RSDEval_t * RSDEval, void * RSDMuStat_or_RSDResults);
void		RSDEval_print 					(RSDEval_t * RSDEval, void * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, int sets, FILE * fpOut);


#ifdef _RSDAI

//RAiSD_PNG.c
typedef struct
{
    uint8_t 	red;
    uint8_t 	green;
    uint8_t 	blue;
    
} pixel_t;
   
typedef struct
{
    pixel_t *	pixels;
    uint64_t 	width;
    uint64_t 	height;
    
} bitmap_t;

pixel_t * 	getPixel 		(bitmap_t * bitmap, int x, int y);
int 		save_png_to_file 	(bitmap_t *bitmap, const char * path);

//RAiSD_Sort.c
typedef struct
{
	int		maxListSize;
	int		curListSize;
	uint64_t *	scoreList;
	int64_t * 	indexList;
		
} RSDSort_t;

RSDSort_t * 	RSDSort_new 		(RSDCommandLine_t * RSDCommandLine);
void 		RSDSort_init 		(RSDSort_t * RSDSort, int size);
void 		RSDSort_rst 		(RSDSort_t * RSDSort);
void 		RSDSort_free 		(RSDSort_t * RSDSort);
void 		RSDSort_appendScore 	(RSDSort_t * RSDSort, uint64_t score, int64_t index);
void 		RSDSort_appendScores 	(RSDSort_t * RSDSort, void * RSDImage, int mode);


typedef struct
{
	int64_t 	size; // this is the gridPointSize
	
	double *	position;
	double 		positionReduced;
	
	float * 	muVar;
	double  	muVarReduced;

	float *		muSfs;
	double 		muSfsReduced;
	
	float *		muLd;
	double 		muLdReduced;
	
	float * 	mu;
	double 		muReduced;
		
	float *		nnPositiveClass0; // 2-class CNN (SweepNet, FAST-NN)
	double		nnPositiveClass0Reduced;	
		
	float * 	nnPositiveClass1; // 4-class CNN (SweepNetRecombination) or mu-var-nn-class0 combination for 2-class CNN
	double 		nnPositiveClass1Reduced;	
	
	
	
	float * 	nnScores2; // used for recomb. signal only
	float * 	nnScores3; // used for recomb. signal only
	

	
	double 		nnScore0Final;

	double 		nnScore2Final;
	double 		nnScore3Final;	

	
	
	
	double		finalRegionCenter; //Position; // TODO-AI- to be fixed..
	double		finalRegionStart;
	double		finalRegionEnd;
	float		finalRegionScore;

} RSDGridPoint_t;

RSDGridPoint_t * 	RSDGridPoint_new 			(void);
void			RSDGridPoint_free 			(RSDGridPoint_t * RSDGridPoint);
void 			RSDGridPoint_addNewPosition 		(RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine, double pos);
void 			RSDGridPoint_reduce 			(RSDGridPoint_t * RSDGridPoint, RSDCommandLine_t * RSDCommandLine, int op); 
int 			RSDGridPoint_getTargetSNPIndex 		(RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, double targetPos);
RSDGridPoint_t * 	RSDGridPoint_compute 			(void * RSDImagev, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, 
				       				 RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, double targetPos, char * destinationPath, 
				       				 int scoreIndex, int setIndex);
void 			RSDGridPoint_calcCompositeScore		(RSDGridPoint_t * RSDGridPoint, int gridPointDataIndex);
void 			RSDGridPoint_write2FileSimple 		(RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat);
void 			RSDGridPoint_write2FileFull		(RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat);
extern void 		(*RSDGridPoint_write2File) 		(RSDGridPoint_t * RSDGridPoint, RSDMuStat_t * RSDMuStat);
void 			RSDGridPoint_write2FileConfigure 	(RSDCommandLine_t * RSDCommandLine);
void 			RSDGridPoint_getSteps 			(RSDCommandLine_t * RSDCommandLine, int * stepsLeft, int * stepsRight);

//RAiSD_Image.c
typedef struct 
{
	int 		width; // window size
	int 		height; // sample size
	int		snpLengthInBytes;	
	int64_t		firstSNPIndex;
	int64_t		lastSNPIndex;	
	uint64_t 	firstSNPPosition; 
	uint64_t 	lastSNPPosition;
	char 		destinationPath [STRING_SIZE];
	uint64_t	remainingSetImages;
	uint64_t 	generatedSetImages;
	uint64_t 	totalGeneratedImages; 
	int8_t * 	data;
	uint64_t ** 	compressedData;
	int8_t *	dataT; // for pixel reordering 
	int8_t * 	incomingSNP;
	uint32_t *	rowSortScore;
	RSDSort_t *	rowSorter;
	uint32_t *	colSortScore;
	RSDSort_t *	colSorter;
	double *	nextSNPDistance;
	//uint8_t * 	byteBuffer; 
	float *		derivedAlleleFrequency;	
	double		sitePosition;
	bitmap_t 	bitmap;	

} RSDImage_t;

RSDImage_t * 	RSDImage_new 				(RSDCommandLine_t * RSDCommandLine);
void 		RSDImage_init 				(RSDImage_t * RSDImage, RSDDataset_t * RSDDataset, RSDMuStat_t * RSDMuStat, RSDPatternPool_t * RSDPatternPool, RSDCommandLine_t * RSDCommandLine, RSDChunk_t * RSDChunk, int setIndex, FILE * fpOut);
void 		RSDImage_free 				(RSDImage_t * RSDImage);
void		RSDImage_print 				(RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDImage_makeDirectory	 		(RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine);
void 		RSDImage_setRange 			(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, int64_t firstSNPIndex, int64_t lastSNPIndex);
void 		decompressPattern 			(uint64_t * pattern, int patternSz, int sampleSz, int8_t * SNP);
void 		RSDImage_getData 			(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine);
void		RSDImage_setRemainingSetImages 		(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine);
void 		RSDImage_resetRemainingSetImages 	(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDCommandLine_t * RSDCommandLine);
void 		RSDImage_reorderData 			(RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine);
void 		RSDImage_createImages 			(RSDImage_t * RSDImage, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 		RSDImage_createGridImages 		(RSDImage_t * RSDImage, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, RSDSort_t * RSDSortRows, RSDSort_t * RSDSortColumns, FILE * fpOut, uint64_t * remainingImages);


RSDGridPoint_t * RSDImage_createImagesFlex (RSDImage_t * RSDImage, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, double targetPos, char * destinationPath, int scoreIndex);
int 		RSDImage_savePNG 			(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, int imgIndex, int8_t * data, char * destinationPath, float muVar, int scoreIndex, int setIndex, int gridPointSize, FILE * fpOut);
int 		RSDImage_saveBIN 			(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDDataset_t * RSDDataset, RSDPatternPool_t * RSDPatternPool, RSDCommandLine_t * RSDCommandLine, int imgIndex, int8_t * data, char * destinationPath, int scoreIndex, int setIndex, int gridPointSize, double targetPos, FILE * fpOut);
void 		RSDImage_writeOutput 			(RSDImage_t * RSDImage, RSDCommandLine_t * RSDCommandLine, RSDDataset_t * RSDDataset, int setIndex, FILE * fpOut);
void 		RSDImage_setSitePosition 		(RSDImage_t * RSDImage, double sitePosition);
void 		RSDImage_generateFullFrame 		(RSDImage_t * RSDImage, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, FILE * fpOut, char * destinationPath, int scoreIndex, int setIndex);

//RAiSD_NeuralNetwork.c
typedef struct
{
	char		pyPath[STRING_SIZE];
	char		cnnMode[STRING_SIZE];
	int		imageHeight;
	int		imageWidth;
	int		dataFormat; // 0: PNG, 1: bin
	int 		dataType; // 0: raw, 1: pw dist, 2: mu-var scaled
	char		networkArchitecture[STRING_SIZE]; 
	int		epochs;
	char		inputPath [STRING_SIZE]; // for data
	char		modelPath [STRING_SIZE]; // for the model
	char		outputPath [STRING_SIZE]; // for the inference 
	int		classSize;
	char **		classLabel;

} RSDNeuralNetwork_t;

RSDNeuralNetwork_t * 	RSDNeuralNetwork_new 			(RSDCommandLine_t * RSDCommandLine);
void			RSDNeuralNetwork_init			(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 			RSDNeuralNetwork_free			(RSDNeuralNetwork_t * RSDNeuralNetwork);
void 			RSDNeuralNetwork_config			(RSDNeuralNetwork_t * RSDNeuralNetwork, char * mode);
void 			RSDNeuralNetwork_createTrainCommand 	(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, char * trainCommand, int showErrors);
void			RSDNeuralNetwork_train 			(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void			RSDNeuralNetwork_test 			(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void 			RSDNeuralNetwork_printDependencies 	(RSDCommandLine_t * RSDCommandLine, FILE * fpOut);
void			RSDNeutralNetwork_run 			(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, void * RSDGrid, FILE * fpOut);
int			RSDNeuralNetwork_modelExists		(char * modelPath);
void			RSDNeuralNetwork_getColumnHeaders 	(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, char * colHeader1, char * colHeader2);

//RAiSD_Results.c
typedef struct
{
	int64_t			setsTotal;
	char **			setID;
	int64_t 		setGridSize;	
	int64_t	*		gridPointSize; // this is the number of images per gridPoint - practically 2D array
	RSDGridPoint_t ** 	gridPointData; // this is all data for each gridPoint for all gridPoints - practically 2D array
	
	float 			muVarMax; 
	float 			muSfsMax; 
	float 			muLdMax; 
	float 			muMax;
	float			nnPositiveClass0Max;
	float			nnPositiveClass1Max;	

	double 			muVarMaxLoc;
	double 			muSfsMaxLoc;
	double			muLdMaxLoc; 
	double 			muMaxLoc;
	double			nnPositiveClass0MaxLoc;
	double			nnPositiveClass1MaxLoc;

} RSDResults_t;

RSDResults_t * 	RSDResults_new 			(RSDCommandLine_t * RSDCommandLine);
void		RSDResults_free			(RSDResults_t * RSDResults);
void 		RSDResults_setGridSize 		(RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine);
void 		RSDResults_incrementSetCounter 	(RSDResults_t * RSDResults);
void 		RSDResults_setGridPointSize 	(RSDResults_t * RSDResults, int64_t gridPointIndex, int64_t gridPointSize);
void 		RSDResults_setGridPoint		(RSDResults_t * RSDResults, int64_t gridPointIndex, RSDGridPoint_t * RSDGridPoint);
void		RSDResults_process 		(RSDResults_t * RSDResults, RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, RSDDataset_t * RSDDataset, RSDMuStat_t * RSDMuStat, RSDCommonOutliers_t * RSDCommonOutliers, RSDEval_t * RSDEval);
void 		RSDResults_processSet 		(RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine, RSDMuStat_t * RSDMuStat, int setIndex, int gridSize, int gridPointOffset);
void		RSDResults_saveSetID 		(RSDResults_t * RSDResults, RSDDataset_t * RSDDataset);
void 		RSDResults_load 		(RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine);
void 		RSDResults_load_2x2 		(RSDResults_t * RSDResults, RSDCommandLine_t * RSDCommandLine);

//RAiSD_Grid.c
typedef struct
{
	int		sizeAcc;
	int		size;
	double 		firstPoint;
	double		pointOffset;
	char 		destinationPath [STRING_SIZE];

} RSDGrid_t;

RSDGrid_t * 	RSDGrid_new 		(RSDCommandLine_t * RSDCommandLine);
void		RSDGrid_free		(RSDGrid_t * RSDGrid);
void		RSDGrid_init		(RSDGrid_t * RSDGrid, RSDDataset_t * RSDDataset, RSDChunk_t * RSDChunk, RSDMuStat_t * RSDMuStat, RSDCommandLine_t * RSDCommandLine, int setDone);
void 		RSDGrid_makeDirectory	(RSDGrid_t * RSDGrid, RSDCommandLine_t * RSDCommandLine, RSDImage_t * RSDImage);
void 		RSDGrid_cleanDirectory	(RSDGrid_t * RSDGrid, RSDCommandLine_t * RSDCommandLine);
void		RSDGrid_processChunk	(RSDGrid_t * RSDGrid, RSDImage_t * RSDImage, RSDMuStat_t * RSDMuStat, RSDChunk_t * RSDChunk, RSDPatternPool_t * RSDPatternPool, RSDDataset_t * RSDDataset, RSDCommandLine_t * RSDCommandLine, RSDResults_t * RSDResults);
#endif





