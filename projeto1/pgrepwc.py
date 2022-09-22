
'''
Projecto SO - processos/threads

Comando a implementar:
    pgrepwc [-a] [-c|-l] [-p n] {palavras} [-f ficheiros]

    -a: opção que define se o resultado da pesquisa são as linhas de texto que contêm unicamente uma das palavras ou
todas as palavras. Por omissão (ou seja, se a opção não for usada), somente as linhas contendo unicamente uma das
palavras serão devolvidas.

    -c: opção que permite obter o número de ocorrências encontradas das palavras a pesquisar.

    -l: opção que permite obter o número de linhas devolvidas da pesquisa. Caso a opção -a não esteja ativa, o número
de linhas devolvido é por palavra.

    -p n: opção que permite definir o nível de paralelização n do comando (ou seja, o número de processos (filhos)/threads 
que são utilizados para efetuar as pesquisas e contagens). Por omissão, deve ser utilizado apenas um processo (o processo pai) 
para realizar as pesquisas e contagens.

    palavras: as palavras a pesquisar no conteúdo dos ficheiros. O número máximo de palavras a pesquisar é de 3.

    -f ficheiros: podem ser dados um ou mais ficheiros, sobre os quais é efetuada a pesquisa e contagem. Caso não sejam dados 
ficheiros na linha de comandos (ou seja, caso não seja passada a opção -f), estes devem ser lidos de stdin (o comando no início da sua execução pedirá ao utilizador quem são os ficheiros a processar).

'''
'''
Overview:


 Processo Pai -> Lê o comando com as opçoes todas -> Distribui o trabalho pelos n processos/threads -> No final recebe as contagens de cada processo/Thread

 Processos filhos -> Recebe o workload do Pai -> Lê  ficheiro e guarda a informação de num e linha das palavras -> Manda o num para o PAI


'''
import sys
import math
import logging
import threading
import time
import string
import re

#função que cria uma lista com as pedidas para pesquisar
def get_words(arguments):
    words=[] #lista de palavras a pesquisar
    start=arguments.index("-p") + 2 #onde começam essas palavras na linha de comandos (índice)
    word=""
    while word!="-f": #enquanto não forem dados os ficheiros
        words.append(arguments[start]) #adicionar à lista a palavra encontrada.
        start=start+1
        word=arguments[start]
 ##   print(words)
    return words



#Função que cria uma lista com os ficheiros onde pesquisar as palavras
def get_files(arguments,num_words, words):  #!!!!!NUM_WORDS não está declarada nesta função
    num_words = len(words) #!!!!!!! 
    files=[] #lista de ficheiros a pesquisar
    start=arguments.index("-p") + 3 + num_words #onde começar a procurar os ficheiros
    file="" 
    while start!=len(arguments): #enquanto não acabarem os argumentos, o programa adiciona à lista os ficheiros
        files.append(arguments[start]) #adicionar os argumentos que correspondem ao nome do ficheiro
        start=start+1 #incrementar o índice
        
 ##   print(files)
    return files



#Função que cria uma variável que guarda o número de threads que o utilizador pediu para criar
def get_numThread(arguments): 
    start=arguments.index("-p")+1 # valor dado por n
    #print("O numero de threads é: ", arguments[start]) #teste
    num=int(arguments[start]) #variável criada com o número de threads
    return num

#função que verifica se a opção -a está ativa
def is_a_option(arguments):
    try:
        value_index = arguments.index("-a") 
    except:
        value_index = -1

    if(value_index<0): #se for dado o valor do índice (tem de ser positivo) indica que a opção está ativa
        return False 
    else:
        return True

#Verifica se a opção -c está ativa
def is_c_option(arguments): 
    try:
        value_index = arguments.index("-c")
    except:
        value_index = -1

    if(value_index<0): #se for dado o valor do índice (tem de ser positivo) indica que a opção está ativa
        return False
    else:
        return True


#verifica se a opção -l está ativa
def is_l_option(arguments):
    try:
        value_index = arguments.index("-l")
    except:
        value_index = -1

    if(value_index<0): #se for dado o valor do índice (tem de ser positivo) indica que a opção está ativa
        return False
    else:
        return True



#Função que faz a divisão dos ficheiros pelas threads
def work_division(numThreads, num_files):
    files_per_thread=[]  #lista com ficheiros atribuídos a cada thread
    if(numThreads<=num_files): #Caso1 --> nº ficheiros ser MAIOR que nº threads
        rest= num_files%numThreads #-->efetuar a divisão dos ficheiros pelas threads - a variável rest verifica que se cada cada threads fica exatamente com o mesmo numero de ficheiros
        left=num_files
        if(rest==0):  #cada thread fica exatamente com o mesmo número de ficheiros
            for i in range(numThreads): 
                files_per_thread.append(num_files//numThreads) #atribuição do numero de ficheiros a cada thread
        else: #quando a divisão não dá resto 0, a cada thread é atribuído um º de ficheiros diferente
            # print(num_files//numThreads) #teste
            for i in range(numThreads):  #DUVIDAS
                if(i!=numThreads-1):
                    files_per_thread.append(math.ceil(num_files/numThreads))
                    left=left-math.ceil(num_files/numThreads)
                else:
                    files_per_thread.append(left)
    if(numThreads>num_files): #caso2: se houver mais threads do que ficheiros automáticamente cada thread fica com um só ficheiro
        for i in range(0, num_files): 
            files_per_thread.append(1)

    
    return files_per_thread 



def find_words(words,files,boolA,boolL,boolC, queue):
   ## print(words) #lista com as palavras que é para procurar
   ##  print(files) # lista com o nome dos files que é suposto ler
    numWords = len(words)

    wordsC=[] #falta meter as contagens de cada palavra -> se tiver 2 palavras ->
    linesC=[] #contagem das linhas 
    for e in range(numWords):
        wordsC.append(0)
        linesC.append(0)
                            #na posiçao 0 desta lista meter a contagem da primeira palavra -> posiçao 1 para a segunda palavra etc...
    wordCount = 0;
    lineCount = 0;
    
     #falta meter as contagens das linhas onde aparece cada palavra -> se tiveres 2 palavras -> 
                            #na posiçao 0 desta lista meter a contagem das linhas da primeira palavra -> posiçao 1 para a segunda palavra etc...
    checkIfCount = 0

    ocorrencias = []   
    ocorre = []

    for k in range(len(files)):
        fileHandle = open(files[k], 'r')
        data = fileHandle.read()
        
        
        if (boolC):
            #fazer caso A + C 
            if(boolA):
            # caso exista pelo menos uma das palavras, conta essa palavra, todas as vezes que aparece no ficheiro

                data = data.split()
                for e in range(numWords) :
                    wordsC[e] += data.count(words[e])
            #fazer caso C sem A, ou seja, VAMOS INTERPRETAR que é para incrementar N marias numa linha
            #onde apareçam N marias e não apareçam as outras palavras.
            else:
                data = data.splitlines()
                for line in data:
                    if len(words) == 1:  #só uma paralavra a procuar
                        ocorrencias.clear()   #[0]
                        ocorrencias.append(0)
                        ocorre.clear()
                        ocorre.append(0)
                    elif len(words) == 2:# 2 palavras a procurar
                        ocorrencias.clear()
                        ocorrencias.append(0)
                        ocorrencias.append(0) #[0,0]  
                        ocorre.clear()
                        ocorre.append(0)
                        ocorre.append(0)
                    else: #ter 3 palavras a procurar
                        ocorrencias.clear()
                        ocorrencias.append(0) #[0,0,0] 
                        ocorrencias.append(0)
                        ocorrencias.append(0) 
                        ocorre.clear()
                        ocorre.append(0)
                        ocorre.append(0)
                        ocorre.append(0)
                    #para cada palavra
                    for e in range(numWords):
                        if words[e] in line:
                            ocorre[e] = 1
                            ocorrencias[e] += line.count(words[e])
                    if sum(ocorre) == 1:
                        for e in range(numWords):
                            if (ocorre[e] == 1):
                                wordsC[e] += ocorrencias[e]
            #returns list!

        if (boolL):
            if(boolA):
            #fazer caso A + L = 
            #caso L e nao A, ou seja, vetor de ocorrencias 
            #ou seja, devolver uma lista em que cada entrada é o numero de linhas em que a palavra
            #prespetiva aparece UNICAMENTE, ou seja, as outras nao aparecem nessas linhas
                Lines = data.splitlines()
            
                for line in Lines:
                    for e in range(numWords):
                        if words[e] in line:
                            checkIfCount = 1
                    if (checkIfCount == 1 ):
                        lineCount += 1
                        checkIfCount = 0

            else:
                data = data.splitlines()
                for line in data:
                    if len(words) == 1:  #só uma paralavra a procuar
                        ocorrencias.clear()   #[0]
                        ocorrencias.append(0)
                        ocorre.clear()
                        ocorre.append(0)
                    elif len(words) == 2:# 2 palavras a procurar
                        ocorrencias.clear()
                        ocorrencias.append(0)
                        ocorrencias.append(0) #[0,0]  
                        ocorre.clear()
                        ocorre.append(0)
                        ocorre.append(0)
                    else: #ter 3 palavras a procurar
                        ocorrencias.clear()
                        ocorrencias.append(0) #[0,0,0] 
                        ocorrencias.append(0)
                        ocorrencias.append(0) 
                        ocorre.clear()
                        ocorre.append(0)
                        ocorre.append(0)
                        ocorre.append(0)
                    #para cada palavra
                    for e in range(numWords):
                        if words[e] in line:
                            ocorre[e] = 1
                            ocorrencias[e] += line.count(words[e])
                    if sum(ocorre) == 1:
                        for e in range(numWords):
                            if (ocorre[e] == 1):
                                linesC[e] += 1
            

    
        fileHandle.close

    if(boolC):
        queue.put(wordsC)
    
    if(boolL and boolA):
        queue.put(lineCount)

    if(boolL and  not boolA):
        queue.put(linesC)


    
    ## Opens files 
    ## prints what is necessary:
    ## Estes processos/threads pesquisam as palavras nos ficheiros, contam as ocorrências das palavras e o 
    ## número de linhas onde estas foram encontradas nos ficheiros e escrevem os resultados (linhas encontradas e contagens) 

    # fazer return das duas lista assim return list_for_count_words, list_for_count_lines para depois a main Thread juntar tudo

    # ver como funciona o return das threads childs para aa parent ( VER MELHOR ISTO)

## if "-p" in sys.argv():
   ## numThreads = int(sys.argv.index("-p")+1)
    ##if numThreads > len(get_files(sys.argv,len(words))):
        ##numThreads=numThreads
##else:
   ## numThreads = 1
 

def main_thread():
    arguments=(sys.argv)
    print(arguments)
    numThreads = get_numThread(arguments)
    words = get_words(arguments)
    files = get_files(arguments,len(words))
    boolA = is_a_option(arguments)
    boolL = is_l_option(arguments)
    boolC = is_c_option(arguments)

    files_per_thread= work_division(numThreads, len(files))
    #print("Exists?", files_per_thread)
    start=0
    threadLock = threading.Lock() # permite que seja tudo feito por ordem
    threads =  []

    #test = find_words(words, files, boolA, boolL, boolC)
    #print("Teste valor e")
    #print(test)

    #variaveis para receber resultados dos filhos

    lineCount = 0
    lineCountList = []
    lineCountTotal = 0

    #variavel pa guardar cada resultado de cada thread 
    lineCountPerWordTemp = []
    #variavel para irem incrementando utilizando a variavel acima
    #e preciso ver que é preciso investigar como somar listas, nao é trivial, é preciso somar index a index
    lineCountPerWordTotal = []
    #mesma cena aqui
    wordCountTemp = []
    wordCount = []
    queue = Queue.Queue

    for e in range(numThreads):
        selected_files = files[start:start+files_per_thread[e]]
     ## vamos selecionar os ficheiros que queremos e reescrever
        child = threading.Thread(target=find_words, args=(words,selected_files,boolA,boolL,boolC, queue))
        threads.append(child)
        child.start()
        print("Criando thread")
        exemplo: lineCountTemp = queue.get()
        lineCountTotal+= LineCountTemp
        
    #    start=start+files_per_thread[e]
    
    for index, thread in enumerate(threads): # Isto é o que espera que todas acabem
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)
        print("Acabou thread")
        #bora somar resultados ne?
       # if(boolL and boolA):
       #     lineCountTotal += 
    
main_thread()





