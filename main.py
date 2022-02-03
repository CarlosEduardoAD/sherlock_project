'''----------------------------SHERLOCK_PROJECT------------------------------'''
# Documentação disponível na página do github

# Importação das bibliotecas
from discord.ext import commands  # Biblioteca do discord
import sqlite3  # Biblioteca do sqlite3
from cryptography.fernet import Fernet as f  # Biblioteca utilizada para a criptografia
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import re
from dotenv import load_dotenv
import logging
import time



# Declaração de variáveis/objetos principais

client = commands.Bot(command_prefix="?")
nao = "http", "jpg", "png", "mp4", "mp3", "zip", "deb", "exe", "rpm","rar","sql","html","mpeg" # Palavras que não podem ser colocadas como senha
data = time.localtime()
horas = time.strftime("%H:%M:%S", data)
logger = logging.getLogger("SHERLOCK")



#Configuração do Logging
logging.basicConfig(filename = "logs.log", level=logging.INFO)
file = logging.FileHandler("logs.log")
file.setLevel(logging.INFO)
logger.addHandler(file)


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
        nome = y[1] # Apanhado do primeiro elemento da lista
        conn = sqlite3.connect("base.db") # Conexão com base de dados
        cursor = conn.cursor() # Criação do cursor (para executar comandos SQL)
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {nome}(
                        id integer NOT NULL PRIMARY KEY,
                        login text,
                        senha text,
                        hash text)''') #Comando SQL
        await ctx.send("Seu cofre foi criado com sucesso") # Envio da mensagem de sucesso
        logger.info(f"{horas}: cofre criado") # Log

    #Se alguma coisa não estiver certa na mensagem (usuário colocou as informações na mesma linha, usuário não colocou informações e/ou não colocou as corretas, manda uma mensagem de erro)
    except: await ctx.send("Não foi possível criar seu cofre, verifique se preencheu as informações da forma correta")
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
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=320000,
                )  # Criação do hash (utiliza tecnologia sha256 como descrito nos argumentos)
                key = (main_hash.derive(pt2))  # Geração da chave
                t = f(base64.urlsafe_b64encode(key))  # Codificação da chave em base64 (pra "binarizar")
                nova_senha = t.encrypt(pt2)  # Senha criptografada
                conn = sqlite3.connect('base.db') # Conexão com base de dados
                cursor = conn.cursor() # Cursor
                cursor.execute(f"INSERT INTO {pt3}(login,hash,senha) VALUES (?,?,?)", (pt1, key, nova_senha,)) # Cadastro do login, senha e hash
                conn.commit() # Gravação dos resultados
                conn.close() # Fechamento da conexão
                await ctx.author.send(f"Senha cadastrada com sucesso, não se esqueça, seu login é este- {pt1}") # Mensagem de sucesso
                logger.info(f"{horas}: cadastro realizado") # Log
        else:
            await ctx.send("Palavra-chave inválida, digite ela novamente") # Se o login não respeitar o padrão regex, ele retorna essa mensagem
    except Exception:
        # Se algo estiver errado com a mensagem do usuário, essa mensagem é retornada
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
        conn = sqlite3.connect("base.db") # Conexão
        cursor = conn.cursor() # Cursor
        cursor.execute(f"SELECT senha FROM {tab} WHERE login = (?)", (pc,)) # Procura a senha a partir do login
        fetch = cursor.fetchone() # Resgata o resultado
        senha_criptografada = fetch[0] # Resultado é retornado em forma de lista dentro de uma tupla, se pega o primeiro elemento dessa lista
        cursor.execute(f"SELECT hash FROM {tab} WHERE login = (?)", (pc,)) # Procura o Hash a partir do login
        fetch2 = cursor.fetchone() # Resgata o resultado
        key = fetch2[0] # Pega o primeiro elemento da lista gerada
        t = f(base64.urlsafe_b64encode(key)) # Codifica a chave
        senha_descriptografada = t.decrypt(senha_criptografada) # Agora com a chave, descriptografa a senha retornada anteriormente
        await ctx.author.send("Aqui está sua senha senhor: " + senha_descriptografada.decode("utf-8")) # Mensagem de sucesso
        conn.commit() # Gravação
        conn.close() # Fechamento
        logger.info(f"{horas}: requisição realizada") # Log

    # Se os dados não existirem ou se faltar alguma informação na hora de realizar o comando, essa mensagem é retornada
    except Exception:
        await ctx.send('''Pelo visto o senhor não cadastrou essa senha,
cadastre ela primeiro para que eu possa guardá-la ou procure outra que já cadastrou''')

'''-------------------------FIM DO COMANDO DE PROCURAR------------------------------'''

'''-------------------------COMANDO DE ATUALIZAR------------------------------'''
@client.command()
async def atualizar(ctx):
    try:
        msg = (str(ctx.message.content)) # Mensagem do usuário
        x = msg.splitlines() # Divisão em lista
        pt1 = str(x[1]) # Pega o login
        pt2 = (x[2].encode("utf-8")) # Pega a senha que vai substituir a passada
        pt3_2 = str(x[3]) # Pega o nome do cofre
        pattern = "[a-zA-Z0-9]+\-[0-9]" # Padrão regex
        if (re.search(pattern, pt1)): # Se a mensagem respeitar o padrão
            if any(word in msg for word in nao): # Se alguma palavra proibida estiver na tupla, retorne um erro
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                salt = os.urandom(256)
                main_hash = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=320000,
                )
                key = (main_hash.derive(pt2))  # Geração da chave
                t = f(base64.urlsafe_b64encode(key))  # Codificação da chave
                nova_senha = t.encrypt(pt2)  # Criptografia da senha
                conn = sqlite3.connect('base.db') # Conexão
                cursor = conn.cursor() # Cursor
                cursor.execute(f"UPDATE {pt3_2} SET senha = (?), hash = (?) WHERE login = (?) ", (nova_senha, key, pt1)) # Substituição da senha
                conn.commit() # Gravação
                conn.close() # Fechamento
                await ctx.author.send("Senha atualizada com sucesso") # Mensagem de sucesso
                logger.info(f"{horas}: atualização realizada") # Log
        else:
            await ctx.send("Palavra-chave inválida, digite ela novamente") # Se o padrão regex não for respeitado
    # Se algo estiver errado, essa mensagem será retornada
    except:
         await ctx.send("Não foi possível atualizar, verifique se preencheu a segunda linha com seu login")

'''-------------------------FIM DO COMANDO DE ATUALIZAR------------------------------'''

'''-------------------------COMANDO DE VER------------------------------'''

@client.command()
async def ver(ctx):
    try:
        msg = str(ctx.message.content) # Mensagem do usuário
        z = msg.splitlines() # Divisão em lista
        tab = z[1] # Nome do cofre
        conn = sqlite3.connect("base.db") # Conexão
        cursor = conn.cursor() # Cursor
        cursor.execute(f"SELECT login FROM {tab}") # Seleciona todos os logins do cofre (somente os logins)
        rs = cursor.fetchall() # Resgate de todos os logins
        conn.commit() # Gravação
        conn.close() # Fechamento
        cont = 1 # Contador
        for row in rs: # Pra cada linha (login) no resultado
            await ctx.send(f"Essa é a sua senha número {cont}: " + " | ".join(row)) # Deve se mandar a mensagem com cada login do cofre
            cont = cont + 1 # E cada vez que a iteração acontecer, haverá um índice falando qual o número do login e consequetemente revelando a quantidade de senhas que você colocou ali
        logger.info(f"{horas}: resquisição de tabela realizada") # Log
    # Se a tabela não existir ou estiverem faltando informações, essa mensagem aparecerá
    except:
        await ctx.send(f"Por favor, digite um nome de um cofre válido ou de um cofre existente, caso ele ainda não exista, use o comando ?criar")

'''-------------------------FIM DO COMANDO DE VER------------------------------'''

@client.command()
async def ola(ctx):
    await ctx.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'") # Comando base, geralmente é o primeiro que o usuário deve tentar


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
                Você pode atualizar ela com o comando ?atualizar, para evitar problemas, nós avisamos que a senha foi cadastrada e deixamos ela ao lado para que o usuário não a esqueça.    
             ''')

load_dotenv() # Carrega o ambiente onde está o token
token = os.getenv('token') # Pega o token do ambiente
if __name__ == "__main__": # Comando que impede a ativação desnecessária do programa
    client.run(token)