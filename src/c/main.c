#define LINE_LEN_MAX 72

#include<stdio.h>


int main(int argc, char *argv[]){
	FILE *source = fopen("test.txt", "r");
	FILE *listing = fopen("listing.txt", "w");
	
	char c=fgetc(source);
	int lineNum=0;
	while(c!=EOF){ //read a line into the line buffer until EOF
		int f=0;
		lineNum++;
		char line_buffer[LINE_LEN_MAX+1]; //+1 so we can end with null terminator

		while(c!=EOF && c!='\n' && f<LINE_LEN_MAX){ //Read chars of line into buffer
			line_buffer[f]=c;
			f++;
			c=fgetc(source);
		}
		fputs(line_buffer, listing);
	}

	fclose(source);
	
	return 0;
}
