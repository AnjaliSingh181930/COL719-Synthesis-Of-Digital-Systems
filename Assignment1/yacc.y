%{
    #include <stdio.h>
    #include <stdlib.h>
    extern int yylex(void);
    extern int yyparse(void);
    void yyerror(char *s){
        fprintf(stderr, "error: %s\n", s);
    }

    int main(int argc, char **argv){
        yyparse();
        return 0;
    }
%}

%token ADD SUB MUL DIV EQU CONST VARI EOL

%union{
    int num;
    char var;
}

%type <num> CONST
%type <var> VARI


%%

%%