# Probabilistic Inference using Bayesian Networks 

Bayesian Networks (Bayes Nets) are graphical models that represent the joint conditional probability distribution of a set of random variables. They use directed acyclic graphs where each node represents a random variable, and edges signify direct dependencies between these variables.

You can read more about Bayesian Network [here](https://en.wikipedia.org/wiki/Bayesian_network)

I have implemented two methods for drawing inferences from Bayes Network :

- Exact inference using variable elimination
- Approximate inferences using rejection sampling


To run the code :
```
python3 ./main.py <file1> <file2>
```

here file1 contains the description of Bayesian Network while the file2 contains the queries associated with bayesian network in file1.

### File Structure :

1. File1 : This file contains the description of bayesian network as follows:
```
N
X1 Parents of X1 separated by space
Conditional probability table
X2 Parents of X2 separated by space
Conditional probability table
...
```

The first line indicates the number of random variables in the network. The variables and their 
parents, are presented in the second line, followed by the conditional probability table

For example :
```
3 – there are three random variables in the network 
1 2 – Random variable 1 has a single parent 2 
0.8 0.2 – P(1=true|2=true) = 0.8 and P(1=false|2=true) = 0.2 
0.4 0.6 – P(1=true|2=false) = 0.4 and P(1=false|2=false) = 0.6 
3 – Random variable 3 has no parents 
0.2 0.8 – P(3=true) = 0.2 and P(3=false) = 0.8 
2 – Random variable 2 has no parents 
0.6 0.4 – P(2=true) = 0.6 and P(2=false) = 0.4
```

2. File2 : This file contains the inference queries
```
technique q query variables separated by space e evidence variables separated by space 
```

For example: 

if we want to use variable elimination to estimate P(1=true,2=true|3=false) for the 
previous network the query line will look like 
 
ve q 1 2 e ~3  
 
If we have to perform the same inference using rejection sampling, then the query would be 
 
rs q 1 2 e ~3 

Note : "~" symbol is used to indicate that the variable if false.

Assumption : we assumed that we are only interested in obtaining probability values instead of a distribution and also we assumed bayes net to represent only boolean variables.

The output generated is written in separate files which have the probability value , one per line for every query in file2.




### Submitted by:
- Chirag Varshney (112201023)
