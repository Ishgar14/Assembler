void main(){
    char name[] = "Rushikesh";
    int age = 20, IQ = 200;

    if(age >= 18 && IQ > 100){
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
