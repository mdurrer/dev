#include <stdio.h>

int main(int argc,  char *argv[])
{
	
	struct person
	{
		char *name;
		char *vorname;
		int alter;
	};
	struct person PersonA;
	struct person PersonB;	
	PersonA.name = "Durrer";
	PersonA.vorname = "Michael";
	PersonA.alter = 19;
	PersonB = PersonA;
	int i;
	char *str;
	char good[]= "Good morning, I'm Michael, yay!";
	for (i=0;i<argc;i++)
	{
			printf("argc: [%d], argv: [%s]\n", i, argv[i]);
	}

	printf ("Starting Struct-Tests\n");
	printf("%s\n",good);
	str = good; /* Set pointer to good adress */
	do
	{
	printf("%c" ,*str);
	str = str +1;
	}
	while (*str != 0);
	printf("\n");
	
	printf("Nachname: %s\nVorname: %s\nAlter:%d\n",PersonA.name, PersonA.vorname, PersonA.alter);
	printf("Nachname: %s\nVorname: %s\nAlter:%d\n",PersonB.name, PersonB.vorname, PersonB.alter);
	return 0;	
}
