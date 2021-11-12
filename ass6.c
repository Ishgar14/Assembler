void main(){
    char name[] = "Rushikesh";
    int age, 
    IQ 
    = 
    200;

    printf("Enter your age: ");
    scanf("%d", &age);

    unsigned   char   *ptr = (unsigned  char * ) & age;
    age++;
    /*
        This is a multiline comment
    */

    if(age >= 18 && IQ > 100){
        // I have the big brain
        printf("You are a smart adult.");
    }
    else if(age >= 18 && IQ < 100){
        printf("You are an adult");
    }
    else {
        printf("Too young!");

        if(IQ > 100)
            printf("But smart");
    }
}
