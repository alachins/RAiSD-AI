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

/* Given "bitmap", this returns the pixel of bitmap at the point 
   ("x", "y"). */

pixel_t * getPixel (bitmap_t * bitmap, int x, int y)
{
    return bitmap->pixels + bitmap->width * y + x;
}
    
/* Write "bitmap" to a PNG file specified by "path"; returns 0 on
   success, non-zero on error. */

int save_png_to_file (bitmap_t *bitmap, const char * path)
{
	assert(bitmap!=NULL);
	assert(path!=NULL);
	
	FILE * fp;
	png_structp png_ptr = NULL;
	png_infop info_ptr = NULL;
	size_t x, y;
	png_byte ** row_pointers = NULL;

	int status = -1; // fail
	int pixel_size = 3;
	int depth = 8;

	fp = fopen (path, "wb");
	if (fp==NULL) 
		return status;

	png_ptr = png_create_write_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if (png_ptr == NULL) 
	{
		fclose(fp);
		return status;
	}

	info_ptr = png_create_info_struct (png_ptr);
	if (info_ptr == NULL) 
	{
		png_destroy_write_struct (&png_ptr, &info_ptr);
		fclose(fp);	
		return status;
	}

	// Set up error handling.

	if (setjmp (png_jmpbuf (png_ptr))) 
	{
		png_destroy_write_struct (&png_ptr, &info_ptr);
		fclose(fp);	
		return status;
	}

	// Set image attributes.

	png_set_IHDR (png_ptr,
		  info_ptr,
		  bitmap->width,
		  bitmap->height,
		  depth,
		  PNG_COLOR_TYPE_RGB,
		  PNG_INTERLACE_NONE,
		  PNG_COMPRESSION_TYPE_DEFAULT,
		  PNG_FILTER_TYPE_DEFAULT);

	// Initialize rows of PNG. 

	row_pointers = png_malloc (png_ptr, bitmap->height * sizeof (png_byte *));
	for (y = 0; y < bitmap->height; y++) {
	png_byte *row = 
	    png_malloc (png_ptr, sizeof (uint8_t) * bitmap->width * pixel_size);
	row_pointers[y] = row;
	for (x = 0; x < bitmap->width; x++) {
	    pixel_t * pixel = getPixel (bitmap, x, y);
	    *row++ = pixel->red;
	    *row++ = pixel->green;
	    *row++ = pixel->blue;
	}
	}

	// Write the image data to "fp". 

	png_init_io (png_ptr, fp);
	png_set_rows (png_ptr, info_ptr, row_pointers);
	png_write_png (png_ptr, info_ptr, PNG_TRANSFORM_IDENTITY, NULL);

	status = 0; // success

	for (y = 0; y < bitmap->height; y++) {
		png_free (png_ptr, row_pointers[y]);
	}
	png_free (png_ptr, row_pointers);
	png_destroy_write_struct (&png_ptr, &info_ptr);
	fclose(fp);	

	return status;
}

#endif
