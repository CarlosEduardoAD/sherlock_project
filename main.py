import sourcedefender


'''----------------------------SHERLOCK_PROJECT------------------------------'''
# Documentação disponível na página do github (página a ser inserida)

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
import datetime as dt
import random
import string



# Declaração de variáveis/objetos principais

client = commands.Bot(command_prefix="?")
nao = "http", "jpg", "png", "mp4", "mp3", "zip", "deb", "exe", "rpm","rar","sql","html","mpeg"
data = dt.datetime.now()
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
# Comando central de alocamento de informações do usuário

'''-------------------------COMANDO DE CRIAR------------------------------'''

@client.command()
async def criar(ctx):
    try:
        msg = str(ctx.message.content)
        y = msg.splitlines()
        nome = y[1]
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {nome}(
                        id integer NOT NULL PRIMARY KEY,
                        login text,
                        senha text,
                        hash text)''')
        await ctx.send("Seu cofre foi criado com sucesso")
        logger.info("f{data}: cofre criado")

    except: await ctx.send("Não foi possível criar seu cofre, verifique se preencheu as informações da forma correta")
'''-------------------------FIM DO COMANDO DE CRIAR------------------------------'''

'''-------------------------COMANDO DE COLOCAR------------------------------'''

@client.command()
async def colocar(ctx):
    try:
        msg = (str(ctx.message.content)) # Divisão do input
        x = msg.splitlines()
        pt1 = str(x[1])
        pt2 = (x[2].encode("utf-8"))
        pt3 = str(x[3])
        pattern = "[a-zA-Z0-9]+\-[0-9]"
        if (re.search(pattern, pt1)):
            salt = os.urandom(256)
            main_hash = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=320000,
            )
            key = (main_hash.derive(pt2)) #Geração da chave
            t = f(base64.urlsafe_b64encode(key))
            nova_senha = t.encrypt(pt2)
            if any(word in msg for word in nao):
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                conn = sqlite3.connect('base.db')
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO {pt3}(login,hash,senha) VALUES (?,?,?)", (pt1, key, nova_senha,))
                conn.commit()
                conn.close()
                await ctx.author.send(f"Senha cadastrada com sucesso, não se esqueça, seu login é este- {pt1}")
                logger.info(f"{data}: cadastro realizado")
        else:
            await ctx.send("Palavra-chave inválida, digite ela novamente")
    except Exception:
        await ctx.send("Não foi possível cadastrar sua senha, "
                       "1- Veja se não colocou arquivos ou links da web\n"
                       "2- Observe se preencheu os três campos corretamente (para mais informações digite ajuda)\n"
                       "3- Verifique se o seu login não é o mesmo do que o de outra pessoa\n")

'''-------------------------FIM DO COMANDO DE COLOCAR------------------------------'''


'''-------------------------COMANDO DE PROCURAR------------------------------'''
@client.command(pass_context=True)
async def procurar(ctx):
    try:
        msg = (str(ctx.message.content))
        x = msg.splitlines()
        pc = str(x[1])
        tab = str(x[2])
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT senha FROM {tab} WHERE login = (?)", (pc,))
        fetch = cursor.fetchone()
        senha_criptografada = fetch[0]
        cursor.execute(f"SELECT hash FROM {tab} WHERE login = (?)", (pc,))
        fetch2 = cursor.fetchone()
        key = fetch2[0]
        t = f(base64.urlsafe_b64encode(key))
        senha_descriptografada = t.decrypt(senha_criptografada)
        await ctx.author.send("Aqui está sua senha senhor: " + senha_descriptografada.decode("utf-8"))
        conn.commit()
        conn.close()
        logger.info(f"{data}: requisição realizada")

    except Exception:
        await ctx.send('''Pelo visto o senhor não cadastrou essa senha,
cadastre ela primeiro para que eu possa guardá-la ou procure outra que já cadastrou''')

'''-------------------------FIM DO COMANDO DE PROCURAR------------------------------'''

'''-------------------------COMANDO DE ATUALIZAR------------------------------'''
@client.command()
async def atualizar(ctx):
    try:
        msg = (str(ctx.message.content))  # Divisão do input
        x = msg.splitlines()
        pt1 = str(x[1])
        pt2 = (x[2].encode("utf-8"))
        pt3_2 = str(x[3])
        pattern = "[a-zA-Z0-9]+\-[0-9]"
        if (re.search(pattern, pt1)):
            salt = os.urandom(256)
            main_hash = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=320000,
            )
            key = (main_hash.derive(pt2))  # Geração da chave
            t = f(base64.urlsafe_b64encode(key))
            nova_senha = t.encrypt(pt2)
            if any(word in msg for word in nao):
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                conn = sqlite3.connect('base.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {pt3_2} SET senha = (?), hash = (?) WHERE login = (?) ", (nova_senha, key, pt1))
                conn.commit()
                conn.close()
                await ctx.author.send("Senha atualizada com sucesso")
                logger.info(f"{data}: atualização realizada")
        else:
            await ctx.send("Palavra-chave inválida, digite ela novamente")
    except:
         await ctx.send("Não foi possível atualizar, verifique se preencheu a segunda linha com seu login")

'''-------------------------FIM DO COMANDO DE ATUALIZAR------------------------------'''

'''-------------------------COMANDO DE VER------------------------------'''

@client.command()
async def ver(ctx):
    try:
        msg = str(ctx.message.content)
        z = msg.splitlines()
        tab = z[1]
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT login FROM {tab}")
        rs = cursor.fetchall()
        conn.commit()
        conn.close()
        cont = 1
        for row in rs:
            await ctx.send(f"Essa é a sua senha número {cont}: " + " | ".join(row))
            cont = cont + 1
        logger.info(f"{data}: resquisição de tabela realizada")
    except:
        await ctx.send(f"Por favor, digite um nome de um cofre válido ou de um cofre existente, caso ele ainda não exista, use o comando ?criar")

'''-------------------------FIM DO COMANDO DE VER------------------------------'''

@client.command()
async def ola(ctx):
    await ctx.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'")


@client.command()
async def ajuda(ctx):
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
async def bot(ctx):
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
async def dicas(ctx):
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

load_dotenv()
token = os.getenv('token')
if __name__ == "__main__":
    client.run(token)