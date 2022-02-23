'''----------------------------SHERLOCK_PROJECT------------------------------'''
# Documentação disponível na página do github

# Importação das bibliotecas
from discord.ext import commands  # Biblioteca do discord
from cryptography.fernet import Fernet as f  # Biblioteca utilizada para a criptografia
from cryptography.hazmat.primitives import hashes # Importação da biblioteca de Hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # Importação do algoritmo de criptografia
import os # Usado simplesmente para gerar caractéres aleatórios
import base64 # Ferramenta de Codificação
import re # Ferramenta de REGEX
from dotenv import load_dotenv # Ferramenta de ambiente
import logging # Ferramenta de log (rlx q aqui não tem log4shell ok)
import time # Ferramenta de tempo
import pymysql as mariadb # Conector do mysql (disfarçado de maria db ;) )

# Declaração de variáveis/objetos principais

client = commands.Bot(command_prefix="?") # Quando alguém for digitar um comando, ele precisa digitar com um ponto de interrogação antes
nao = "http", "jpg", "png", "mp4", "mp3", "zip", "deb", "exe", "rpm","rar","sql","html","mpeg" # Palavras que não podem ser colocadas como senha
data = time.localtime() # Data local para log
horas = time.strftime("%H:%M:%S", data) # Formatação da data
logger = logging.getLogger("SHERLOCK") # Criação do objeto que pega o logger do Sherlock

#Conexão com Base de dados
conn = mariadb.connect(host='localhost',
                       user='carlo',
                       password='carloseduardo0814',
                       database='sherlock',
                       cursorclass = mariadb.cursors.DictCursor)
# Declaração do objeto do cursor
cursor = conn.cursor()

#Configuração do Logging
logging.basicConfig(filename = "logs.log", level=logging.INFO)
file = logging.FileHandler("logs.log")
file.setLevel(logging.INFO)
logger.addHandler(file)

'''-------------------------ÍNICIO DA APLICAÇÃO-----------------------------'''

# Checagem de disponibilidade do bot
@client.event
async def on_ready():
    print("Bot is ready")
    logger.info("Bot está pronto")

'''-------------------------COMANDO DE CRIAR------------------------------'''

@client.command()
async def criar(ctx):
    try:
        msg = str(ctx.message.content) # Declaração da varíavel central que pega o conteúdo da mensagem
        y = msg.splitlines() # Seperação conteúdo, cada palavra em uma nova linha será armazaenada como um elemento de uma lista
        tabela = y[1] # Apanhado do primeiro elemento da lista
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {tabela}(
                        id integer NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                        login text NOT NULL,
                        senha text,
                        hash BLOB)''')
        await ctx.send("Seu cofre foi criado com sucesso") # Envio da mensagem de sucesso
        conn.commit() # Gravação dos dados
        logger.info(f"{horas}: cofre criado") # Log

    # Se alguma coisa não estiver certa na mensagem (usuário colocou as informações na mesma linha e/ou usuário não colocou informações, manda uma mensagem de erro)
    except IndexError:
        await ctx.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência \n"
                       "1- O comando '?criar'\n"
                       "2- O nome do cofre que você quer colocar")
    except Exception:
        await ctx.send("Não foi possível criar seu cofre, verifique se as informações estão corretas")

'''-------------------------FIM DO COMANDO DE CRIAR------------------------------'''

'''-------------------------COMANDO DE COLOCAR------------------------------'''

@client.command()
async def colocar(ctx):
    try:
        msg = (str(ctx.message.content)) # Apanhado do countéudo
        x = msg.splitlines() # Divisão do countéudo em lista
        pt1 = str(x[1]) # Apanhado do primeiro elemento, esse será o login
        pt2 = (x[2].encode("utf-8")) # Apanhado do segundo elemento, esse será a senha a ser criptografada
        pt3 = str(x[3]) # # Nome do cofre, aqui será o elemento central, pois ele determinará onde será colocado as informações acima
        pattern = "[a-zA-Z0-9]+\-[0-9]" # Padrão regex
        if (re.search(pattern, pt1)): # Se o login seguir o padrão regex, ele vai criar um hash
            if any(word in msg for word in nao): # Se alguma palavra que está na tupla de palavras que não podem ser colocadas como uma senha estiverem aqui, ele retorna um erro.
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                salt = os.urandom(256)  # Salt
                main_hash = PBKDF2HMAC(
                    algorithm=hashes.SHA256(), # Algoritmo de criptografia
                    length=32, # Vai ter um tamanho de 32 bits
                    salt=salt, # O salt é igual aos números aleatórios lá da variável
                    iterations=320000, # Ele vai fazer 320000 iterações para criar a chave
                )  # Resumo: Criação do hash (utiliza tecnologia sha256 como descrito nos argumentos)
                key = (main_hash.derive(pt2))  # Geração da chave
                t = f(base64.urlsafe_b64encode(key))  # Codificação da chave em base64 (pra "binarizar")
                nova_senha = t.encrypt(pt2)  # Senha criptografada
                sql_query = f"INSERT INTO `{pt3}`(`login`,`senha`,`hash`) VALUES (%s,%s,%s)" # Query para colocar o login, a senha, e o hash
                cursor.execute(sql_query,(pt1,nova_senha.decode("utf-8"),key)) # Cadastro do login, senha e hash
                conn.commit() # Gravação dos resultados # Fechamento da conexão
                await ctx.author.send(f"Senha cadastrada com sucesso, não se esqueça, seu login é este: {pt1}") # Mensagem de sucesso
                logger.info(f"{horas}: cadastro realizado") # Log
        else:
            await ctx.send("Palavra-chave inválida, você não pode digitar espaços, precisa separar por um hífen e só pode colocar números depois do hífen") # Se o login não  respeitar o padrão regex, ele retorna essa mensagem
    except IndexError: # Se o usuário tiver esquecido de colocar algo, retorna esse erro
        await ctx.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?colocar'\n"
                       "2- Seu login \n"
                       "3- Sua senha \n"
                       "4- O nome do seu cofre")
    except Exception:
         #Se algo estiver errado com a mensagem do usuário, essa mensagem é retornada
        await ctx.send("Não foi possível cadastrar sua senha, "
                       "1- Veja se não colocou arquivos ou links da web\n"
                       "2- Observe se preencheu os três campos corretamente (para mais informações digite ajuda)\n"
                       "3- Verifique se o seu login não é o mesmo do que o de outra pessoa\n")

'''-------------------------FIM DO COMANDO DE COLOCAR------------------------------'''


'''-------------------------COMANDO DE PROCURAR------------------------------'''
@client.command(pass_context=True)
async def procurar(ctx):
    try:
        msg = (str(ctx.message.content)) # Mensagem do usuário
        x = msg.splitlines() # Divisão em lista
        pc = str(x[1]) # Pega o login
        tab = str(x[2])# Pega o nome do cofre
        cursor.execute(f"SELECT senha FROM {tab} WHERE login = (%s)", (pc,)) # Procura a senha a partir do login
        fetch = cursor.fetchone() # Resgata o resultado
        for item in fetch:
            senha_criptografada = fetch[item] # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        cursor.execute(f"SELECT hash FROM {tab} WHERE login = (%s)", (pc,)) # Procura o Hash a partir do login
        fetch2 = cursor.fetchone() # Resgata o resultado
        for item in fetch2:
            key = fetch2[item] # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        t = f(base64.urlsafe_b64encode(key)) # Codifica a chave
        senha_descriptografada = t.decrypt(senha_criptografada.encode("UTF-8")) # Agora com a chave, descriptografa a senha retornada anteriormente
        await ctx.author.send("Aqui está sua senha senhor: " + senha_descriptografada.decode("utf-8")) # Mensagem de sucesso
        conn.commit() # Gravação
        logger.info(f"{horas}: requisição realizada") # Log

     # Se faltar alguma informação na hora de realizar o comando, essa mensagem é retornada
    except IndexError:
        await ctx.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?procurar' \n"
                       "2- Seu login \n"
                       "3- O nome do seu cofre")
    # Caso contrário os elementos não existam, retorna essa mensagem
    except Exception:
        await ctx.send('''Pelo visto o senhor não cadastrou essa senha,
cadastre ela primeiro para que eu possa guardá-la ou procure outra que já cadastrou''')

'''-------------------------FIM DO COMANDO DE PROCURAR------------------------------'''

'''-------------------------COMANDO DE ATUALIZAR------------------------------'''
@client.command()
async def deletar(ctx): # Aqui a porca torce o rabo
    try:
        msg = (str(ctx.message.content)) # Mensagem do usuário
        x = msg.splitlines() # Divisão em lista
        pt1 = str(x[1]) # Pega o login
        pt2 = (x[2]) # Pega a tabela
        sql_query = f"DELETE FROM {pt2} WHERE login = %s" # Query para deletar a senha, se não existir, ela prossegue mesmo assim
        cursor.execute(sql_query, pt1) #Execução da query
        if cursor.rowcount > 0:
            await ctx.send("Foi deletado")
            conn.commit()  # Gravação
        else:
            await ctx.send("Não")
    except IndexError: # Se estiver faltando algum elemento, retorna essa mensagem
        await ctx.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?deletar' \n"
                       "2- Seu login \n"
                       "3- O nome do seu cofre")
    # Se alguma coisa não estiver certa mesmo assim, retorne essa mensagem
    except Exception:
        await ctx.send("Não foi possível deletar a senha") #Caso falte nome da tabela ou o nome do comando esteja errado

'''-------------------------FIM DO COMANDO DE ATUALIZAR------------------------------'''

'''-------------------------COMANDO DE VER------------------------------'''

@client.command()
async def ver (ctx):
    try:
        msg = (str(ctx.message.content))  # Mensagem do usuário
        x = msg.splitlines()  # Divisão em lista
        pt2 = str(x[1])  # Pega a tabela
        sql_query = f"SELECT login FROM {pt2}" # Query para selecionar os logins
        cursor.execute(sql_query)  # Seleciona todos os logins do cofre (somente os logins)
        rs = (cursor.fetchall())  # Resgate de todos os logins
        conn.commit()  # Gravação
        conn.close()  # Fechamento
        cont = 1  # Contador
        for i in rs: # Para cada chave no dicionário (objeto) retornado pelo SQL
            resultados = (i["login"]) # Os resultados serão iguais ao valor do login
            await ctx.send(f"Essa é a sua senha número {cont}: " + "".join(resultados)) # Deve se mandar a mensagem com cada login do cofre
            cont = cont + 1  # E cada vez que a iteração acontecer, haverá um índice falando qual o número do login e consequetemente revelando a quantidade de senhas que você colocou ali
        logger.info(f"{horas}: resquisição de tabela realizada")  # Log
    # Se alguma coisa não estiver certa mesmo assim, retorne essa mensagem
    except IndexError: # Se estiver faltando algum elemento, retorna essa mensagem
        await ctx.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?ver' \n"
                       "2- O nome do seu cofre")
    except Exception:
        await ctx.send("Não foi possível deletar a senha")  # Caso falte nome da tabela ou o nome do comando esteja errado

'''-------------------------FIM DO COMANDO DE VER------------------------------'''

'''-------------------------FIM DA APLICAÇÃO------------------------------'''


'''-------------------------ERROR HANDLING------------------------------'''
@client.event
async def on_command_error (ctx,error):
    if isinstance(error, commands.CommandNotFound):
        msg = str(ctx.message.content)
        x = msg.splitlines()
        comando_errado = x[0]
        await ctx.send(f" '{comando_errado}' ? Esse comando não existe, por favor, digite um que eu conheça \n"
                       f"lembrando que meus comandos são, '?colocar', '?procurar' e '?deletarever'")

'''-------------------------FIM DO ERROR HANDLING------------------------------'''

@client.command()
async def ola(ctx): # Comando central
    await ctx.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'")


@client.command()
async def ajuda(ctx): # Comando de ajuda que explica como funciona (está em texto, porém quero fazer em imagem)
    await ctx.send('''Para colocar uma senha, digite '?colocar', e em seguida digite o comando shift 
enter para pular uma linha, na primeira linha você colocará o seu login, na segunda, sua senha. \n
Para ver suas senhas, digite '?procurar', e em seguida, aperte barra de espaço e escreva o seu login. \n 
Asseguramos que você utilize o bot mandando MENSAGENS DIRETAS para ele, e NÃO usando o CHAT DO SERVIDOR, não se dá para confiar 100% em todos em servidores públicos \n
A primeira parte do seu login não pode ter barra de espaço, é necessário colocar também um ponto e alguns números, mais ou menos assim \n 
minhasenhasecreta:201920202021 \n
Este bot não é indicado para ser utilizado em servidores grandes, mas em servidores mais pequenos e de um grupo específico de pessoas
NUNCA coloque seu email como login (exemplos: fulanofaztudo@gmail.com)
Não é possível colocar uma senha com o mesmo login, se quiser colocar uma outra senha para o seu login, terá que ou deletar seu login antigo ou criar fazer uma nova colocação.''')


@client.command()
async def bot(ctx): # Explicação do bot, o que ele faz e aviso de atualizações futuras
    await ctx.send(''' Sou SherLock, bot para gerenciamento de senhas o qual utiliza o cliente do Discord \n
Meu dever é garantir a segurança da sua senha e seu login, 
em volta à uma internet cheia de hackers e pessoas mal intencionadas \n
Todas as senhas são criptogradas com chaves de alta segurança para garantir que os dados sejam bem protegeidos \n
Aviso: Eu (e meu(s) administradores) NÃO iremos mudar ou visualizar sua senha ou login,
além do mais, os dados são salvos já criptografados com uma chave de ordem aleatória \n
Por mais que seja seguro guardar suas senhas conosco, recomendados fortemente que não guarde as seguintes informações \n
    CPF\n
    CNPJ\n
    DATA DE NASCIMENTO\n
    INFORMAÇÕES DE CARTEIRA DE NASCIMENTO, IDENTIDADE OU CARTEIRA DE MOTORISTA\n
    INFORMAÇÕES ESTRITAMENTE PESSOAIS\n
Assim como há dados que irei aceitar, há dados que não irei aceitar, tais como:\n
    LINKS DA INTERNET (Para evitar que enviem imagens ou links maliciosos, 
    como links de sites pornográficos ou de imagens inadequadas para o público geral)\n
    ARQUIVOS ARMAZENADOS NA WEB\n
Porém se você quer uma senha mais bem protegida, você pode sim colocar:\n
    CARACTERES ESPECIAIS (@,%,$,*, etc...)\n
Segundo Aviso: Este serviço é 100% GRATUITO, você não irá pagar uma mensalidade ou irá ficar restrito á um plano freemium, 
todos os recursos podem ser utilizados por todos usuários\n
porém uma forma de ajudar esse projeto a continuar é doando para o meu administrador, 
não é obrigatório, independente de você doa 1 real todos os dias para ele, 
ou nunca sequer pensou em doar para ele, nosso serviço continuará gratuito\n
Último aviso: Qualquer atualização que meus administradores aplicarem em mim será informada aos usúarios\n''')

@client.command()
async def dicas(ctx): # Dicas de proteção
    await ctx.send('''Não se preocupe, estou aqui para dar algumas dicas \n
             1- Evite senhas simples (1234, 0123 ou "Seu nome"123) \n
                'Vejo isso em todo o lugar, porque realmente preciso fazer isso ?'
                Não que seja estritamente necessário, porém é o mais recomendado \n
                Quando sua senha é enviada para algum servidor (exemplo: senha do instagram), 
                ela pode ou não passar por criptografia \n
                Na maioria dos casos ela vai ser sim criptograda, mas quando não,
                ela basicamente pode ficar exposta em uma base de dados SQL 
                (Base de dados de consulta estruturada, basicamente uma base de dados que pode ser consultada a partir de programação),
                além do hacker poder ter acesso a sua conta, ele pode fazer algo pior, 
                como realizar a SQL Injection (metódo que basicamente embaralha todos os dados da tabela sql) e fazer você perder todos os seus dados.
                Se ela estiver criptografada, pode estar na criptografa em md5, um algoritmo regularmente eficiente mas que porém pode ser facilmente quebrado até por meio de ferramentas online.
                O mais seguro será se ela estiver criptografada com um token que precisa ser acessado, esse token deverá ser criptografado em sha256, por mais que seja bem seguro, ainda é recomendado que coloque uma senha forte.
            2- Como criar uma senha forte ? \n
                Colocar uma palavra-chave da qual você use com frequência e alguma série de números é uma boa ideia, sempre colcar senhas em sites diferentes também é recomendado, em relação aos caractéres especiais, algumas sites não permitem o uso desses caractéres, mas aqui você está livre para usar eles.
            3- E se eu perder minha senha ? 
                Você pode ver suas senhas usando o comando deletarever e se for preciso, deletar ou só manter uma delas
             ''')

load_dotenv() # Carrega o ambiente onde está o token
token = os.getenv('token') # Pega o token do ambiente
if __name__ == "__main__": # Comando que impede a ativação desnecessária do programa
    client.run(token)




