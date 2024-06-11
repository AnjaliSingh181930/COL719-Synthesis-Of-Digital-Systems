%{
    #include "parser.h"
    #include <stdio.h>
    void ShowError();
   
%}

******* regular expression *******

variable ([a-zA-Z])
constant ([0-9])+


%%

******* token specification *******

"+"             { return ADD; }
"-"             { return SUB; }
"*"             { return MUL; }
"/"             { return DIV; }
"="             { return EQU; }
{constant}      {yylval.num = atoi(yytext); return CONST; }
{variable}      {sscanf(yytext, "%c", yyval.var); return VARI;}
\n              { return EOL; }
[ \t]           { /* ignore whitespace */ }
.               {return yytext[0];}

%%

void Showerror(){
    print("Other Input");
}

int yywrap(){
    return 1; 
}