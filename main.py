'''----------------------------SHERLOCK_PROJECT------------------------------'''
# Documentação disponível na página do github

import base64  # Ferramenta de Codificação
import logging  # Ferramenta de log (rlx q aqui não tem log4shell ok)
import os  # Usado simplesmente para gerar caractéres aleatórios
import re  # Ferramenta de REGEX
import time  # Ferramenta de tempo
from argon2 import PasswordHasher, Type # Ferramenta de criptografia
import discord  # Importação da biblioteca do discord para ativação dos intents
from cryptography.fernet import Fernet as f  # Biblioteca utilizada para a criptografia
from cryptography.hazmat.primitives import hashes  # Importação da biblioteca de Hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt  # Importação do algoritmo de criptografia
# Importação das bibliotecas
from discord.ext import commands  # Biblioteca do discord
from dotenv import load_dotenv  # Ferramenta de ambiente
from pymysqlpool.pool import Pool as mariadb  # Ferramenta de conexão pool com o banco de dados

# Declaração de variáveis/objetos principais

intents = discord.Intents.default() #Declaração do objeto dos intents
intents.members = True # Permite o acesso aos membros do servidor
client = commands.Bot(command_prefix="?", intents=intents) # Quando alguém for digitar um comando, ele precisa digitar com um ponto de interrogação antes
nao = (".jpg", ".png", ".mp4", ".mp3", ".zip", ".deb", ".exe", ".rpm",".rar", ".html",".mpeg" , ".css", ".js") # Palavras que não podem ser colocadas como senha
data = time.localtime() # Data local para log
horas = time.strftime("%H:%M:%S", data) # Formatação da data
logger = logging.getLogger("SHERLOCK") # Criação do objeto que pega o logger do Sherlock
load_dotenv() # Carrega o ambiente onde está o token
token = os.getenv('token') # Pega o token do ambiente
senha_watch = os.getenv('senha_watch') # Pega a senha do watchdog

#Configuração do Logging
logging.basicConfig(filename = "logs.log", level=logging.INFO)
file = logging.FileHandler("logs.log")
file.setLevel(logging.INFO)
logger.addHandler(file)

# Configuração do banco de dados
pool = mariadb(host='localhost', user='watchdog', password='desmasiadostrintaecincose357', database='baskerville')
conn = pool.get_conn()
cursor = conn.cursor()

'''-------------------------ÍNICIO DA APLICAÇÃO-----------------------------'''

# Checagem de disponibilidade do bot
@client.event # Evento do bot (não é ativado por trigger)
async def on_ready():
    print("Bot está pronto") #Se o bot estiver apto para se conectar, só printe que ele está pronto
    logger.info("Bot está pronto") # Log
    return True

@client.command() # Evento do bot (não é ativado por trigger)
async def criar_conta(ctx): # Quando um membro entrar no servidor com o bot nele, ele já vai criar a conta automaticamente
    try:
        msg = str(ctx.message.content).splitlines()
        senha = msg[1].encode("utf-8")
        a = ctx.author # O cliente do discord pega o canal com base no id
        nome_do_usuario = str(a.name) # Pega o nome do usuário e codifica ele para bytes
        member_id = str(a.id) # Pega o id do usuário
        hash = PasswordHasher(
            salt_len=16,
            hash_len=32,
            memory_cost=65536,
            time_cost=4,
            parallelism=2,type=Type.ID
        )# Geração do salt
        senha_hasehada = hash.hash(senha) # Criptografia da senha
        cursor = conn.cursor()  # Declaração do objeto do cursor
        sql_query = "INSERT INTO users(discord_id, name, master_password) VALUES(%s, %s, %s)"
        cursor.execute(sql_query, (member_id, nome_do_usuario, senha_hasehada)) # Execução da query
        conn.commit()
        await ctx.send(f"Seja bem vindo {a.name}, sua conta já foi criada com sucesso") # Manda pro usuário que a conta já foi criada
        logger.info(f"{a.name} criou a conta com sucesso") # Log
    except IndexError:
        await ctx.send(f"Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando ?criar_conta \n"
                       "2- A sua senha mestra (Não perca ela por favor, e mesmo assim se perder, você ainda pode substituir ela")
    except Exception as e:
        await ctx.send("Por onde andava ? Que seja, bem vindo novamente, sua conta já estava aqui quando verifiquei pela última vez")

'''-------------------------COMANDO DE COLOCAR------------------------------'''

@client.command()
async def colocar(ctx):
    try:
        # Declaração do objeto do cursor
        msg = (str(ctx.message.content)) # Apanhado do countéudo
        x = msg.splitlines() # Divisão do countéudo em lista
        senha = x[1] # Apanhado da senha
        pt1 = (x[2]) # login
        pt2 = (x[3]) # site
        pt3 = (x[4]) # senha
        pt4 = (x[5]) # palavra_chave
        id = ctx.author.id
        watchdog_query = "SELECT name, master_password from users where discord_id = %s"
        cursor.execute(watchdog_query, (id,))
        a = cursor.fetchone()
        senha_do_cofre = a["master_password"]
        ph = PasswordHasher()
        if not ph.verify(senha_do_cofre, str(senha).encode("UTF-8")):
            await ctx.send("Você não tem permissão para fazer esse comando, crie uma conta primeiro por favor")
        pattern = "[a-zA-Z]+[0-9]" # Padrão regex
        if (re.search(pattern, pt4)): # Se o login seguir o padrão regex, ele vai criar um hash
            if any(word in msg for word in nao): # Se alguma palavra que está na tupla de palavras que não podem ser colocadas como uma senha estiverem aqui, ele retorna um erro.
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                main_hash = Scrypt(
                    salt = os.urandom(256),
                     length = 32,
                     n = 2**14,
                     r = 8,
                     p = 1,
                ) # Resumo: Criação do hash (utiliza tecnologia scrypt como descrito nos argumentos)
                key = (main_hash.derive(pt1.encode("UTF-8")))  # Geração da chave
                t = f(base64.urlsafe_b64encode(key))  # Codificação da chave em base64 (pra "binarizar")
                nova_senha = t.encrypt(pt3.encode("UTF-8"))
                login = t.encrypt(pt1.encode("UTF-8"))
                site = t.encrypt(pt2.encode("UTF-8"))# Senha criptografada
                sql_query = f"INSERT INTO passwords(`id_discord`,`login`,`site`,`keyword`,`password`, `secret`) VALUES (%s,%s,%s,%s,%s,%s)" # Query para colocar o login, a senha, e o hash
                cursor.execute(sql_query,(id, login, site, pt4, nova_senha, key)) # Cadastro do login, senha e hash
                conn.commit() # Gravação dos resultados # Fechamento da conexão
                await ctx.author.send(f"Senha cadastrada com sucesso, não se esqueça, sua palavra-chave é esta: {pt4}") # Mensagem de sucesso
                logger.info(f"{horas}: cadastro realizado") # Log
        else:
            await ctx.author.send("Palavra-chave inválida, você não pode digitar espaços, precisa separar por um hífen e só pode colocar números depois do hífen") # Se o login não  respeitar o padrão regex, ele retorna essa mensagem
    except IndexError: # Se o usuário tiver esquecido de colocar algo, retorna esse erro
        await ctx.author.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                              "1- O comando '?colocar'\n"
                              "2- Sua senha mestra \n"
                              "3- O seu login (email etc) \n"
                              "4- O nome do site \n"
                              "5- A palavra chave que quer guardar para acessar a senha \n"
                              "6- A sua senha")
    except Exception as e: # Se alguma coisa não estiver certa na mensagem, retorna esse erro
        await ctx.send(e)
        await ctx.author.send("Não foi possível colocar sua senha, verifique se as informações estão corretas")
        #Se algo estiver errado com a mensagem do usuário, essa mensagem é retornada
        await ctx.author.send("Não foi possível cadastrar sua senha, "
                              "1- Veja se não colocou arquivos ou links da web\n"
                              "2- Observe se preencheu os três campos corretamente (para mais informações digite ajuda)\n"
                              "3- Verifique se o seu login não é o mesmo do que o de outra pessoa\n")

'''-------------------------FIM DO COMANDO DE COLOCAR------------------------------'''


'''-------------------------COMANDO DE PROCURAR------------------------------'''
@client.command(pass_context=True)
async def procurar(ctx):
    try:
        # Declaração do objeto do cursor
        msg = (str(ctx.message.content)) # Mensagem do usuário
        x = msg.splitlines() # Divisão em lista
        senha = x[1] # Senha
        pc = str(x[2]) # Pega a palavra-chave
        id = ctx.author.id
        watchdog_query = "SELECT name, master_password from users where discord_id = %s"
        cursor.execute(watchdog_query, (id,))
        a = cursor.fetchone()
        senha_do_cofre = a["master_password"]
        ph = PasswordHasher()
        if not ph.verify(senha_do_cofre, str(senha).encode("UTF-8")):
            await ctx.send("Você não tem permissão para fazer esse comando, crie uma conta primeiro por favor")
        cursor.execute(f"SELECT password FROM passwords WHERE keyword = (%s)", (pc,)) # Procura a senha a partir do login
        fetch = cursor.fetchone() # Resgata o resultado
        for item in fetch:
            senha_criptografada = fetch[item] # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        cursor.execute(f"SELECT secret FROM passwords WHERE keyword = (%s)", (pc,)) # Procura o Hash a partir do login
        fetch2 = cursor.fetchone() # Resgata o resultado
        for item in fetch2:
            key = fetch2[item] # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        cursor.execute(f"SELECT site FROM passwords WHERE keyword = (%s)", (pc,))  # Procura o Hash a partir do login
        fetch3 = cursor.fetchone()  # Resgata o resultado
        for item in fetch3:
             site = fetch3[item]  # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        cursor.execute(f"SELECT login FROM passwords WHERE keyword = (%s)", (pc,))  # Procura o Hash a partir do login
        fetch4 = cursor.fetchone()  # Resgata o resultado
        for item in fetch4:
            login = fetch4[item]  # Resultado é retornado em forma de um dicionário (ou objeto pode ser também), se pega o elemento referente à chave 'login'
        t = f(base64.urlsafe_b64encode(key)) # Codifica a chave
        senha_descriptografada = t.decrypt(senha_criptografada.encode("UTF-8")) # Agora com a chave, descriptografa a senha retornada anteriormente
        site_descriptografado = t.decrypt(site.encode("UTF-8")) # Agora com a chave, descriptografa o site retornado anteriormente
        login_descriptografado = t.decrypt(login.encode("UTF-8")) # Agora com a chave, descriptografa o login retornado anteriormente
        await ctx.author.send("Aqui está sua senha senhor: " + senha_descriptografada.decode("utf-8")) # Mensagem de sucesso
        await ctx.author.send(f"Aqui está seu site senhor: {site_descriptografado.decode('UTF-8')}")  # Mensagem de sucesso
        await ctx.author.send(f"Aqui está seu login senhor: {login_descriptografado.decode('UTF-8')}")  # Mensagem de sucesso
        conn.commit() # Gravação
        logger.info(f"{horas}: requisição realizada") # Log

    # Se faltar alguma informação na hora de realizar o comando, essa mensagem é retornada
    except IndexError:
        await ctx.author.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                              "1- O comando '?procurar' \n"
                              "2- Sua senha mestra \n"
                              "3- A sua palavra-chave (Se não lembra, usar o comando 'ver'")
    # Caso contrário os elementos não existam, retorna essa mensagem
    except Exception as e:
        await ctx.send(e)
        await ctx.author.send('''Pelo visto o senhor não cadastrou essa senha,
cadastre ela primeiro para que eu possa guardá-la ou procure outra que já cadastrou''')

'''-------------------------FIM DO COMANDO DE PROCURAR------------------------------'''

'''-------------------------COMANDO DE ATUALIZAR------------------------------'''
@client.command()
async def deletar(ctx): # Aqui a porca torce o rabo
    try:
        # Declaração do objeto do cursor
        msg = (str(ctx.message.content))  # Mensagem do usuário
        x = msg.splitlines()  # Divisão em lista
        senha = x[1]  # Senha
        pt1 = str(x[2])  # Pega a palavra-chave
        id = ctx.author.id
        watchdog_query = "SELECT name, master_password from users where discord_id = %s"
        cursor.execute(watchdog_query, (id,))
        a = cursor.fetchone()
        senha_do_cofre = a["master_password"]
        ph = PasswordHasher()
        if not ph.verify(senha_do_cofre, str(senha).encode("UTF-8")):
            await ctx.send("Você não tem permissão para fazer esse comando, crie uma conta primeiro por favor")
        sql_query = f"DELETE FROM passwords WHERE keyword = %s" # Query para deletar a senha, se não existir, ela prossegue mesmo assim
        cursor.execute(sql_query, pt1) #Execução da query
        if cursor.rowcount > 0:
            await ctx.send("A sua senha foi deletada com sucesso")
            conn.commit()  # Gravação
        else:
            await ctx.author.send("Não foi possível deletar sua senha, por favor, digite ela corretamente")
    except IndexError: # Se estiver faltando algum elemento, retorna essa mensagem
        await ctx.author.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?deletar' \n"
                       "2- Sua senha mestra \n"
                       "3- A palavra-chave da sua senha")
    # Se alguma coisa não estiver certa mesmo assim, retorne essa mensagem
    except Exception as e:
        await ctx.send(e)
        await ctx.author.send("Não foi possível deletar a senha") #Caso falte nome da tabela ou o nome do comando esteja errado

'''-------------------------FIM DO COMANDO DE ATUALIZAR------------------------------'''

'''-------------------------COMANDO DE VER------------------------------'''

@client.command()
async def ver (ctx):
    try:
        msg = (str(ctx.message.content))  # Mensagem do usuário
        x = msg.splitlines()  # Divisão em lista
        senha = x[1]  # Senha
        id = ctx.author.id
        watchdog_query = "SELECT name, master_password from users where discord_id = %s"
        cursor.execute(watchdog_query, (id,))
        a = cursor.fetchone()
        senha_do_cofre = a["master_password"]
        ph = PasswordHasher()
        if not ph.verify(senha_do_cofre, str(senha).encode("UTF-8")):
            await ctx.send("Você não tem permissão para fazer esse comando, crie uma conta primeiro por favor")
        sql_query = f"SELECT keyword FROM passwords WHERE id_discord = %s" # Query para selecionar os logins
        cursor.execute(sql_query, id)  # Seleciona todos os logins do cofre (somente os logins)
        rs = (cursor.fetchall())  # Resgate de todos os logins
        conn.commit()  # Gravação
        cont = 1  # Contador
        for i in rs:  # Para cada chave no dicionário (objeto) retornado pelo SQL
            resultados = (i["keyword"])  # Os resultados serão iguais ao valor do login
            await ctx.author.send(f"Essa é a sua palavra-chave número {cont}: " + "".join(resultados)) # Deve se mandar a mensagem com cada login do cofre
            cont = cont + 1  # E cada vez que a iteração acontecer, haverá um índice falando qual o número do login e consequetemente revelando a quantidade de senhas que você colocou ali
        logger.info(f"{horas}: resquisição de tabela realizada")  # Log
    # Se alguma coisa não estiver certa mesmo assim, retorne essa mensagem
    except IndexError: # Se estiver faltando algum elemento, retorna essa mensagem
        await ctx.author.send("Não foi possível, eu vi que você não colocou algum campo, siga esta sequência. \n"
                       "1- O comando '?ver' \n"
                       "2- O nome do seu cofre")
    except Exception as e:
        await ctx.send(e)
        await ctx.author.send("Não foi possível ver suas palavras chaves")  # Caso falte nome da tabela ou o nome do comando esteja errado

'''-------------------------FIM DO COMANDO DE VER------------------------------'''

'''-------------------------FIM DA APLICAÇÃO------------------------------'''


'''-------------------------ERROR HANDLING------------------------------'''
@client.event
async def on_command_error (ctx,error):
    if isinstance(error, commands.CommandNotFound):
        msg = str(ctx.message.content)
        x = msg.splitlines()
        comando_errado = x[0]
        await ctx.author.send(f" '{comando_errado}' ? Esse comando não existe, por favor, digite um que eu conheça \n"
                       f"lembrando que meus comandos são, '?colocar', '?procurar' e '?deletarever'")

'''-------------------------FIM DO ERROR HANDLING------------------------------'''

@client.command()
async def ola(ctx): # Comando central
    await ctx.author.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'")


@client.command()
async def ajuda(ctx): # Comando de ajuda que explica como funciona (está em texto, porém quero fazer em imagem)
    await ctx.author.send('''Para colocar uma senha, digite '?colocar', e em seguida digite o comando shift 
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
    await ctx.author.send(''' Sou SherLock, bot para gerenciamento de senhas o qual utiliza o cliente do Discord \n
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
    await ctx.author.send('''Não se preocupe, estou aqui para dar algumas dicas \n
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

if __name__ == "__main__": # Comando que impede a ativação desnecessária do programa
    client.run(token)




